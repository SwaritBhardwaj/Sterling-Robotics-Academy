#!/usr/bin/env python3
"""
Sitemap Freshness Analyzer
──────────────────────────

Beyond "is the sitemap valid?" — this asks "is the editorial team actually
working?" by looking at the temporal distribution of <lastmod> values:

  1. Distribution by year/month — how recent is the catalog?
  2. Stale share — % of URLs with lastmod older than N days (default 180)
  3. Bulk update detection — buckets of URLs sharing the exact same lastmod,
     which is the classic "touched timestamps to refresh the sitemap" pattern
     Google has learned to discount.
  4. Missing-lastmod share — pages submitted without any lastmod signal.

Why this matters: Google demotes content-decay sites. A sitemap with 90% of
URLs stuck on 2024 dates is a leading indicator the team has stopped
publishing, which feeds into the algorithmic re-classification we saw in
recent core updates.

Inputs:
    target               Sitemap URL or domain (auto-discovers /sitemap.xml)
    --stale-days N       Days threshold for "stale" (default 180)
    --bulk-threshold N   Min URLs sharing one lastmod to flag bulk (default 10)
    --json PATH          Write JSON envelope
    --markdown PATH      Write Markdown summary

Exit code:
    0 = healthy editorial cadence
    1 = warning (bulk updates detected OR stale share 50-80%)
    2 = critical (stale share >80% OR no lastmod at all)

Example:
    python sitemap_freshness.py https://example.com/sitemap.xml --markdown /tmp/f.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import SKILL_VERSION, fetch, finding, result_envelope  # noqa: E402
from sitemap_validator import _parse_sitemap, normalize_target  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────
# lastmod parsing — tolerate the dialects sitemaps ship with

def _parse_lastmod(s: str) -> date | None:
    """Sitemaps may use date-only ('2026-05-15') or full ISO 8601
    ('2026-05-15T10:30:00+00:00'). Return date or None on parse failure."""
    if not s:
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    # Try fromisoformat (handles 'Z' suffix in newer Python versions)
    try:
        # Strip trailing Z and replace with +00:00 for fromisoformat
        normalized = s.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────────────
# Aggregation

def _gather_entries(sitemap_url: str) -> tuple[list[dict], list[dict]]:
    """Fetch the sitemap and (if it's an index) all child sitemaps. Returns
    (all_url_entries, fetch_errors). Errors are non-fatal — we still report
    what we managed to read."""
    errors: list[dict] = []
    try:
        r = fetch(sitemap_url, timeout=15)
    except requests.RequestException as e:
        return [], [{"url": sitemap_url, "error": str(e)}]
    if not r.ok:
        return [], [{"url": sitemap_url, "http_status": r.status_code}]

    parsed = _parse_sitemap(r.text)
    if parsed.get("parse_error"):
        return [], [{"url": sitemap_url, "parse_error": parsed["parse_error"]}]

    if parsed["kind"] == "urlset":
        return parsed["entries"], errors

    if parsed["kind"] == "index":
        all_entries: list[dict] = []
        for child in parsed["entries"]:
            try:
                cr = fetch(child["loc"], timeout=15)
                if cr.ok:
                    cp = _parse_sitemap(cr.text)
                    if cp.get("kind") == "urlset":
                        all_entries.extend(cp["entries"])
                    else:
                        errors.append({"url": child["loc"], "warning": "nested or unknown"})
                else:
                    errors.append({"url": child["loc"], "http_status": cr.status_code})
            except requests.RequestException as e:
                errors.append({"url": child["loc"], "error": str(e)})
        return all_entries, errors

    return [], [{"url": sitemap_url, "warning": "unknown sitemap kind"}]


def analyze(
    entries: list[dict],
    *,
    stale_days: int = 180,
    bulk_threshold: int = 10,
) -> dict:
    """Compute distribution + stale + bulk statistics.

    Returns a dict ready to drop into the result envelope. All counts are
    explicit (not derived later) so the consumer can render any view it
    wants without recomputing."""
    today = datetime.now(timezone.utc).date()
    total = len(entries)

    with_lastmod = 0
    parsed_dates: list[date] = []
    raw_lastmod_per_entry: list[tuple[str, str | None]] = []
    by_month: Counter[str] = Counter()
    by_year: Counter[str] = Counter()
    age_buckets = {
        "last_30d": 0,
        "31_90d": 0,
        "91_180d": 0,
        "181_365d": 0,
        "1y_2y": 0,
        "older_than_2y": 0,
    }
    stale_urls: list[str] = []
    parse_failures: list[str] = []

    # Bulk detection — two granularities:
    #   - exact lastmod string ('2025-12-15T10:00:00Z' all-identical → scripted touch)
    #   - same calendar day (different timestamps but same day → manual end-of-month batch)
    # Both patterns get discounted by Google. The exact-match is the more
    # damning signal; the same-day match is a softer warning.
    bulk_groups: dict[str, list[str]] = defaultdict(list)
    bulk_by_day: dict[str, list[str]] = defaultdict(list)

    for e in entries:
        raw = e.get("lastmod")
        loc = e.get("loc", "")
        raw_lastmod_per_entry.append((loc, raw))
        if not raw:
            continue
        with_lastmod += 1
        bulk_groups[raw].append(loc)

        d = _parse_lastmod(raw)
        if d is None:
            parse_failures.append(loc)
            continue
        parsed_dates.append(d)
        by_month[d.strftime("%Y-%m")] += 1
        by_year[d.strftime("%Y")] += 1
        bulk_by_day[d.isoformat()].append(loc)

        age = (today - d).days
        if age <= 30:
            age_buckets["last_30d"] += 1
        elif age <= 90:
            age_buckets["31_90d"] += 1
        elif age <= 180:
            age_buckets["91_180d"] += 1
        elif age <= 365:
            age_buckets["181_365d"] += 1
        elif age <= 730:
            age_buckets["1y_2y"] += 1
        else:
            age_buckets["older_than_2y"] += 1

        if age > stale_days:
            stale_urls.append(loc)

    # Bulk groups: only keep ones above threshold
    bulk_flags = [
        {"lastmod": k, "url_count": len(v), "sample_urls": v[:5]}
        for k, v in sorted(bulk_groups.items(), key=lambda kv: -len(kv[1]))
        if len(v) >= bulk_threshold
    ]
    bulk_day_flags = [
        {"day": k, "url_count": len(v), "sample_urls": v[:5]}
        for k, v in sorted(bulk_by_day.items(), key=lambda kv: -len(kv[1]))
        if len(v) >= bulk_threshold
    ]

    no_lastmod = total - with_lastmod
    stale_share_pct = round(len(stale_urls) / total * 100, 1) if total else 0.0
    no_lastmod_pct = round(no_lastmod / total * 100, 1) if total else 0.0

    # Health verdict — simple bands so the dashboard can colour-code without
    # re-deriving the rule.
    if total == 0:
        verdict = "no_data"
    elif no_lastmod_pct > 50:
        verdict = "no_lastmod_signal"
    elif stale_share_pct > 80:
        verdict = "critical_decay"
    elif stale_share_pct > 50:
        verdict = "warning_decay"
    elif bulk_flags or bulk_day_flags:
        verdict = "bulk_updates_present"
    else:
        verdict = "healthy"

    return {
        "total_urls": total,
        "with_lastmod": with_lastmod,
        "without_lastmod": no_lastmod,
        "without_lastmod_pct": no_lastmod_pct,
        "stale_threshold_days": stale_days,
        "stale_count": len(stale_urls),
        "stale_share_pct": stale_share_pct,
        "stale_sample": stale_urls[:30],
        "parse_failures": parse_failures[:20],
        "by_month": dict(sorted(by_month.items())),
        "by_year": dict(sorted(by_year.items())),
        "age_buckets": age_buckets,
        "bulk_threshold": bulk_threshold,
        "bulk_lastmod_groups": bulk_flags,
        "bulk_same_day_groups": bulk_day_flags,
        "verdict": verdict,
    }


# ─────────────────────────────────────────────────────────────────────────
# Markdown report

def to_markdown(target: str, analysis: dict) -> str:
    a = analysis
    lines = [
        f"# Sitemap Freshness · {target}",
        "",
        f"Skill: v{SKILL_VERSION}  ·  Total URLs: **{a['total_urls']}**  ·  "
        f"Verdict: **{a['verdict']}**",
        "",
        "## Coverage",
        "",
        f"- With `<lastmod>`: **{a['with_lastmod']}** "
        f"({100 - a['without_lastmod_pct']:.1f}%)",
        f"- Without `<lastmod>`: **{a['without_lastmod']}** "
        f"({a['without_lastmod_pct']}%)",
        f"- Stale (>{a['stale_threshold_days']}d): **{a['stale_count']}** "
        f"({a['stale_share_pct']}%)",
        "",
        "## Age Distribution",
        "",
        "| Bucket | URLs |",
        "|---|---:|",
        f"| Last 30 days | {a['age_buckets']['last_30d']} |",
        f"| 31–90 days | {a['age_buckets']['31_90d']} |",
        f"| 91–180 days | {a['age_buckets']['91_180d']} |",
        f"| 181–365 days | {a['age_buckets']['181_365d']} |",
        f"| 1–2 years | {a['age_buckets']['1y_2y']} |",
        f"| Older than 2y | {a['age_buckets']['older_than_2y']} |",
        "",
    ]

    if a["bulk_lastmod_groups"]:
        lines.append("## Bulk lastmod groups — exact timestamp match")
        lines.append("")
        lines.append(
            "Groups sharing the *exact* same lastmod timestamp. Strong signal "
            "of a scripted bulk touch. Google discounts this aggressively.")
        lines.append("")
        lines.append("| lastmod | URL count | Sample |")
        lines.append("|---|---:|---|")
        for g in a["bulk_lastmod_groups"][:10]:
            sample = g["sample_urls"][0] if g["sample_urls"] else ""
            lines.append(f"| `{g['lastmod']}` | {g['url_count']} | {sample} |")
        lines.append("")

    if a.get("bulk_same_day_groups"):
        lines.append("## Bulk lastmod groups — same calendar day")
        lines.append("")
        lines.append(
            "Groups whose lastmod falls on the same day (different timestamps). "
            "Softer signal, but still suggests batch editorial action rather "
            "than organic publishing cadence.")
        lines.append("")
        lines.append("| Day | URL count | Sample |")
        lines.append("|---|---:|---|")
        for g in a["bulk_same_day_groups"][:10]:
            sample = g["sample_urls"][0] if g["sample_urls"] else ""
            lines.append(f"| `{g['day']}` | {g['url_count']} | {sample} |")
        lines.append("")

    if a["by_month"]:
        lines.append("## Recent monthly cadence")
        lines.append("")
        lines.append("| Month | URLs |")
        lines.append("|---|---:|")
        for m, c in list(a["by_month"].items())[-12:]:
            lines.append(f"| {m} | {c} |")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────
# CLI

def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("target", help="sitemap URL or domain")
    p.add_argument("--stale-days", type=int, default=180)
    p.add_argument("--bulk-threshold", type=int, default=10)
    p.add_argument("--json", type=Path)
    p.add_argument("--markdown", type=Path)
    args = p.parse_args()

    sitemap_url = normalize_target(args.target)
    entries, errors = _gather_entries(sitemap_url)
    if not entries:
        env = result_envelope(
            target=sitemap_url,
            response=None,
            checker="sitemap_freshness.py",
            error="no URL entries gathered",
            fetch_errors=errors,
            issues=[finding("P0", "Sitemap unreadable or empty",
                            evidence={"errors": errors})],
        )
        if args.json:
            args.json.write_text(json.dumps(env, indent=2), encoding="utf-8")
        else:
            print(json.dumps(env, indent=2))
        return 1

    analysis = analyze(
        entries,
        stale_days=args.stale_days,
        bulk_threshold=args.bulk_threshold,
    )

    # Translate analysis → P0/P1/P2 issues for downstream tooling
    issues: list[dict] = []
    if analysis["verdict"] == "critical_decay":
        issues.append(finding(
            "P0",
            f"Content decay critical: {analysis['stale_share_pct']}% of URLs "
            f"have lastmod older than {analysis['stale_threshold_days']} days",
            evidence={"stale_count": analysis["stale_count"],
                      "total": analysis["total_urls"]},
        ))
    elif analysis["verdict"] == "warning_decay":
        issues.append(finding(
            "P1",
            f"Content decay warning: {analysis['stale_share_pct']}% of URLs "
            f"have lastmod older than {analysis['stale_threshold_days']} days",
            evidence={"stale_count": analysis["stale_count"]},
        ))
    if analysis["verdict"] == "no_lastmod_signal":
        issues.append(finding(
            "P1",
            f"{analysis['without_lastmod_pct']}% of URLs have no <lastmod> — "
            f"Google has no freshness signal to use",
        ))
    if analysis["bulk_lastmod_groups"]:
        top = analysis["bulk_lastmod_groups"][0]
        issues.append(finding(
            "P2",
            f"{len(analysis['bulk_lastmod_groups'])} bulk-update group(s) "
            f"detected (largest: {top['url_count']} URLs sharing "
            f"{top['lastmod']}) — Google discounts unchanged content with "
            f"touched timestamps",
        ))
    if analysis.get("bulk_same_day_groups"):
        top = analysis["bulk_same_day_groups"][0]
        issues.append(finding(
            "P2",
            f"{len(analysis['bulk_same_day_groups'])} same-day update group(s) "
            f"detected (largest: {top['url_count']} URLs on {top['day']}) — "
            f"batch editorial pattern, weaker freshness signal",
        ))

    env = result_envelope(
        target=sitemap_url,
        response=None,
        checker="sitemap_freshness.py",
        fetch_errors=errors,
        issues=issues,
        **analysis,
    )

    if args.json:
        args.json.write_text(json.dumps(env, indent=2), encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(to_markdown(sitemap_url, analysis), encoding="utf-8")
    if not args.json and not args.markdown:
        print(json.dumps(env, indent=2))

    # Exit code
    if analysis["verdict"] in ("critical_decay", "no_lastmod_signal"):
        return 2
    if analysis["verdict"] in ("warning_decay", "bulk_updates_present"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
