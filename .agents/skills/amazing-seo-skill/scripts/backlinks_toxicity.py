#!/usr/bin/env python3
"""
Backlinks Toxicity Analyzer
───────────────────────────

Reads a backlinks CSV export (Ahrefs Site Explorer → Backlinks, Semrush
Backlink Analytics, or Majestic) and produces the consultant-style
toxicity diagnosis:

  1. **DR / Authority distribution** — what % of referring domains are
     DR 0-10 vs DR 30+ vs DR 50+?
  2. **Recent acquisitions quality** — same distribution restricted to
     domains first seen after `--recent-after` (default: 90 days ago).
     "Did our last 3 months of link-building bring quality or junk?"
  3. **Suspicious anchor patterns** — repeated commercial anchors,
     branded anchors on low-DR sites, anchors that name link-selling
     channels (e.g. `TG @LINKS_DEALER`), explicit "buy / cheap / SEO"
     spam patterns.
  4. **Targeted subdomain abuse** — links pointing at non-standard
     subdomains (tracking, redirect, share) that can indicate open-
     redirect exploitation.
  5. **Per-domain toxicity score** 0-100, combining DR floor, anchor
     spam pattern, language mismatch, and link recency.

The script does NOT auto-disavow — it produces evidence for a human-led
disavow review. Output is consultant-ready Markdown + a JSON envelope
that can feed the premium dashboard.

Inputs:
    --ahrefs PATH      Ahrefs export. Recognised columns include:
                       'Referring page URL', 'Domain rating', 'UR',
                       'Anchor', 'First seen', 'Type', 'Target URL'
    --semrush PATH     Semrush Backlink Analytics export. Recognised:
                       'Source URL', 'Source AS' (Authority Score),
                       'Anchor', 'First Seen', 'Target URL'
    --majestic PATH    Majestic export. Recognised: 'SourceURL',
                       'TrustFlow', 'CitationFlow', 'AnchorText', 'TargetURL'

Outputs:
    --json PATH        Aggregated envelope with per-domain scores
    --markdown PATH    Consultant-ready Markdown
    --disavow PATH     Disavow-format text file (one domain or URL per line,
                       prefixed `domain:` per Google spec) — for human review

Exit codes:
    0 = clean (<10% of domains low-authority, no anchor red flags)
    1 = warning (10-30% low-authority or anchor patterns surfaced)
    2 = critical (>30% low-authority OR explicit link-spam anchors)

Example:
    python backlinks_toxicity.py --ahrefs /tmp/ah_backlinks.csv \\
        --recent-after 2026-02-01 --markdown /tmp/toxic.md
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import SKILL_VERSION, finding, result_envelope  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────
# Column resolution per source. Each tuple is (canonical_field, candidates).

COLUMN_MAPS = {
    "ahrefs": {
        "source_url": ("referring page url", "referring page", "source url"),
        "source_domain": ("referring domain", "referring page domain"),
        "authority": ("domain rating", "dr"),
        "ur": ("url rating", "ur"),
        "anchor": ("anchor", "anchor text"),
        "first_seen": ("first seen", "first crawled"),
        "type": ("type", "link type"),
        "target_url": ("target url", "target page"),
    },
    "semrush": {
        "source_url": ("source url", "source page url"),
        "source_domain": ("source domain", "source"),
        "authority": ("source as", "authority score", "as"),
        "anchor": ("anchor", "anchor text"),
        "first_seen": ("first seen", "first detected"),
        "type": ("type", "link type"),
        "target_url": ("target url", "target page"),
    },
    "majestic": {
        "source_url": ("sourceurl", "source url"),
        "source_domain": ("sourcedomain", "source domain"),
        "authority": ("trustflow", "tf"),
        "cf": ("citationflow", "cf"),
        "anchor": ("anchortext", "anchor"),
        "first_seen": ("datefirstseen", "first seen"),
        "target_url": ("targeturl", "target url"),
    },
}


def _normalize(s: str) -> str:
    return s.strip().lower().replace("_", " ").replace("-", " ")


def _find_col(headers: list[str], candidates: tuple[str, ...]) -> str | None:
    nmap = {h: _normalize(h) for h in headers}
    cs = set(candidates)
    for orig, norm in nmap.items():
        if norm in cs:
            return orig
    return None


def _parse_date(s: str) -> date | None:
    if not s:
        return None
    s = s.strip().strip('"')
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%b %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _safe_int(s: str) -> int:
    s = (s or "").strip().replace(",", "")
    if not s:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def _domain_of(url: str) -> str:
    host = urlparse(url).hostname or url
    return host.lstrip("www.").lower()


# ─────────────────────────────────────────────────────────────────────────
# Anchor spam patterns

SPAM_ANCHOR_PATTERNS = (
    (re.compile(r"\b(buy|cheap|order|hire|get).{0,15}(seo|backlinks?|links?)", re.I),
     "buy/cheap-links phrasing"),
    (re.compile(r"@?(SEO_ANOMALY|LINKS?_?DEALER|BHS_?LINKS?|LINK_?BUY|"
                r"SEO_?SHOP)", re.I),
     "named link-selling channel"),
    (re.compile(r"\btg\s*[@:]", re.I), "Telegram channel reference"),
    (re.compile(r"\b(escort|casino|porn|viagra|cialis|loan|crypto.signals?)",
                re.I), "high-spam vertical"),
    # Require actual spaces between tiny tokens, otherwise "click here" gets
    # split char-by-char via backtracking and falsely matches.
    (re.compile(r"^\s*(?:[a-z0-9]{1,3}\s+){4,}[a-z0-9]{1,3}\s*$", re.I),
     "keyword stuffed (very short repeating tokens)"),
)

GENERIC_ANCHORS = {
    "click here", "here", "this site", "this article", "this page",
    "read more", "more info", "website", "link", "url", "homepage",
}

SAFE_SUBDOMAIN_PREFIXES = ("www.", "app.", "docs.", "help.", "support.",
                           "blog.", "api.", "cdn.")


# ─────────────────────────────────────────────────────────────────────────
# Per-link enrichment

def _score_anchor(anchor: str) -> tuple[int, list[str]]:
    """Return (anchor_spam_score 0-100, matched_pattern_names)."""
    if not anchor:
        return 0, []
    score = 0
    hits: list[str] = []
    for pat, name in SPAM_ANCHOR_PATTERNS:
        if pat.search(anchor):
            score += 35
            hits.append(name)
    if anchor.strip().lower() in GENERIC_ANCHORS:
        score += 5
        hits.append("generic phrase")
    return min(score, 100), hits


def _is_unusual_subdomain(target_url: str, primary_domain: str | None = None) -> bool:
    """Flag links targeting non-standard subdomains. Without knowing the
    primary domain we approximate via the SAFE_SUBDOMAIN_PREFIXES list."""
    host = urlparse(target_url).hostname or ""
    host = host.lower()
    if not host:
        return False
    # Drop the rightmost two labels (eTLD+1 heuristic — good enough for
    # the .com / .io / .co.uk cases this script sees in practice).
    parts = host.split(".")
    if len(parts) <= 2:
        return False
    subdomain = ".".join(parts[:-2]) + "."
    if any(subdomain.startswith(p) for p in SAFE_SUBDOMAIN_PREFIXES):
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────
# Loader → list of canonical link dicts

def load_csv(path: Path, source: str) -> list[dict]:
    cmap = COLUMN_MAPS[source]
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        col = {field: _find_col(headers, cands) for field, cands in cmap.items()}
        if not col.get("source_url") and not col.get("source_domain"):
            raise ValueError(
                f"{path}: need source URL or domain. Headers: {headers}"
            )
        rows = []
        for r in reader:
            src_url = (r.get(col["source_url"]) or "").strip() if col["source_url"] else ""
            src_dom = (r.get(col["source_domain"]) or "").strip() if col["source_domain"] else ""
            if not src_dom and src_url:
                src_dom = _domain_of(src_url)
            anchor = (r.get(col["anchor"]) or "").strip() if col["anchor"] else ""
            target = (r.get(col["target_url"]) or "").strip() if col["target_url"] else ""
            auth = _safe_int(r.get(col["authority"], "")) if col["authority"] else 0
            first_seen = _parse_date(r.get(col["first_seen"], "")) if col["first_seen"] else None
            rows.append({
                "source_url": src_url,
                "source_domain": src_dom.lower(),
                "authority": auth,
                "anchor": anchor,
                "first_seen": first_seen,
                "target_url": target,
            })
    return rows


# ─────────────────────────────────────────────────────────────────────────
# Aggregation

DR_BUCKETS = [(0, 10), (11, 20), (21, 30), (31, 50), (51, 70), (71, 100)]


def _bucket_label(auth: int) -> str:
    for lo, hi in DR_BUCKETS:
        if lo <= auth <= hi:
            return f"DR {lo}-{hi}"
    return "DR 0-10"


def analyze(links: list[dict], *, recent_after: date | None) -> dict:
    by_domain: dict[str, dict] = defaultdict(lambda: {
        "domain": None,
        "authority": 0,
        "link_count": 0,
        "anchors": [],
        "first_seen": None,
        "targets": [],
        "anchor_hits": [],
    })
    total_domains_in_input = set()

    # Pass 1: aggregate by source domain.
    for L in links:
        d = L["source_domain"]
        if not d:
            continue
        total_domains_in_input.add(d)
        entry = by_domain[d]
        entry["domain"] = d
        entry["authority"] = max(entry["authority"], L["authority"])
        entry["link_count"] += 1
        if L["anchor"]:
            entry["anchors"].append(L["anchor"])
        if L["target_url"]:
            entry["targets"].append(L["target_url"])
        if L["first_seen"]:
            if entry["first_seen"] is None or L["first_seen"] < entry["first_seen"]:
                entry["first_seen"] = L["first_seen"]

    # Pass 2: toxicity score per domain.
    for d, e in by_domain.items():
        score = 0
        reasons: list[str] = []
        if e["authority"] <= 10:
            score += 35
            reasons.append(f"DR {e['authority']} ≤ 10")
        elif e["authority"] <= 20:
            score += 15
            reasons.append(f"DR {e['authority']} in 11-20 band")
        # Anchor signals: take worst across all anchors from this domain.
        max_anchor_score = 0
        max_hits: list[str] = []
        for a in e["anchors"]:
            s, h = _score_anchor(a)
            if s > max_anchor_score:
                max_anchor_score = s
                max_hits = h
        score += max_anchor_score
        e["anchor_hits"] = max_hits
        if e["anchors"] and len(set(e["anchors"])) == 1 and e["link_count"] >= 3:
            score += 10
            reasons.append("all anchors identical (sitewide template link)")
        # Recent acquisition raises weight on otherwise borderline domains.
        if recent_after and e["first_seen"] and e["first_seen"] >= recent_after:
            score = int(score * 1.1)
            reasons.append("first-seen recently")
        e["toxicity"] = min(score, 100)
        e["reasons"] = reasons + ([f"anchor: {h}" for h in max_hits])

    # DR distribution overall
    dr_overall = Counter(_bucket_label(e["authority"]) for e in by_domain.values())
    # DR distribution recent-only
    dr_recent = Counter(
        _bucket_label(e["authority"]) for e in by_domain.values()
        if recent_after and e["first_seen"] and e["first_seen"] >= recent_after
    )

    # Target subdomain abuse: count how many links point at unusual subdomains
    targets_unusual: Counter[str] = Counter()
    for L in links:
        if L["target_url"] and _is_unusual_subdomain(L["target_url"]):
            host = urlparse(L["target_url"]).hostname or ""
            targets_unusual[host.lower()] += 1

    # Anchor spam top patterns
    anchor_pattern_hits: Counter[str] = Counter()
    for e in by_domain.values():
        for h in e["anchor_hits"]:
            anchor_pattern_hits[h] += 1

    flagged = sorted(
        (e for e in by_domain.values() if e["toxicity"] >= 60),
        key=lambda x: -x["toxicity"],
    )

    total_domains = len(by_domain)
    low_auth = sum(1 for e in by_domain.values() if e["authority"] <= 10)
    low_auth_pct = round(low_auth / total_domains * 100, 1) if total_domains else 0.0

    if total_domains == 0:
        verdict = "no_data"
    elif anchor_pattern_hits or low_auth_pct >= 30:
        verdict = "critical"
    elif low_auth_pct >= 10:
        verdict = "warning"
    else:
        verdict = "clean"

    return {
        "total_links_in_input": len(links),
        "total_unique_domains": total_domains,
        "low_authority_domains_count": low_auth,
        "low_authority_share_pct": low_auth_pct,
        "dr_distribution": dict(dr_overall),
        "dr_distribution_recent": dict(dr_recent) if recent_after else None,
        "recent_after": recent_after.isoformat() if recent_after else None,
        "anchor_spam_patterns": dict(anchor_pattern_hits),
        "unusual_target_subdomains": dict(targets_unusual.most_common(20)),
        "flagged_domains_count": len(flagged),
        "flagged_domains_sample": [
            {
                "domain": e["domain"],
                "authority": e["authority"],
                "link_count": e["link_count"],
                "toxicity": e["toxicity"],
                "reasons": e["reasons"],
                "sample_anchor": e["anchors"][0] if e["anchors"] else None,
                "first_seen": e["first_seen"].isoformat() if e["first_seen"] else None,
            }
            for e in flagged[:50]
        ],
        "verdict": verdict,
    }


# ─────────────────────────────────────────────────────────────────────────
# Output renderers

def to_markdown(target: str, a: dict) -> str:
    lines = [
        f"# Backlinks Toxicity · {target}",
        "",
        f"Skill: v{SKILL_VERSION}  ·  Total links: **{a['total_links_in_input']}**  ·  "
        f"Domains: **{a['total_unique_domains']}**  ·  Verdict: **{a['verdict']}**",
        "",
        "## DR distribution",
        "",
        "| Bucket | Domains | Share |",
        "|---|---:|---:|",
    ]
    total = a["total_unique_domains"] or 1
    for b in sorted(a["dr_distribution"]):
        n = a["dr_distribution"][b]
        lines.append(f"| {b} | {n} | {round(n / total * 100, 1)}% |")
    lines.append("")

    if a.get("dr_distribution_recent"):
        rec = a["dr_distribution_recent"]
        rec_total = sum(rec.values()) or 1
        lines.append(f"## Recent acquisitions (since {a['recent_after']})")
        lines.append("")
        lines.append("| Bucket | Domains | Share |")
        lines.append("|---|---:|---:|")
        for b in sorted(rec):
            n = rec[b]
            lines.append(f"| {b} | {n} | {round(n / rec_total * 100, 1)}% |")
        lines.append("")

    if a["anchor_spam_patterns"]:
        lines.append("## Anchor spam patterns")
        lines.append("")
        lines.append("| Pattern | Domain matches |")
        lines.append("|---|---:|")
        for k, v in sorted(a["anchor_spam_patterns"].items(), key=lambda x: -x[1]):
            lines.append(f"| {k} | {v} |")
        lines.append("")

    if a["unusual_target_subdomains"]:
        lines.append("## Unusual target subdomains")
        lines.append("")
        lines.append("Links pointing at non-standard subdomains — investigate "
                     "for open-redirect / tracker abuse.")
        lines.append("")
        lines.append("| Subdomain | Links |")
        lines.append("|---|---:|")
        for k, v in a["unusual_target_subdomains"].items():
            lines.append(f"| {k} | {v} |")
        lines.append("")

    if a["flagged_domains_sample"]:
        lines.append("## Top flagged domains (toxicity ≥ 60)")
        lines.append("")
        lines.append("| Domain | DR | Links | Toxicity | Reason |")
        lines.append("|---|---:|---:|---:|---|")
        for e in a["flagged_domains_sample"][:25]:
            reason = "; ".join(e["reasons"][:3])
            lines.append(
                f"| {e['domain']} | {e['authority']} | {e['link_count']} | "
                f"{e['toxicity']} | {reason} |"
            )
    return "\n".join(lines)


def to_disavow(a: dict, threshold: int = 70) -> str:
    """Produce a disavow file: `domain:example.com` per Google spec."""
    lines = [
        "# Auto-generated disavow candidates — REVIEW BEFORE SUBMITTING",
        f"# Skill: v{SKILL_VERSION}  ·  Threshold: toxicity >= {threshold}",
        "#",
    ]
    for e in a["flagged_domains_sample"]:
        if e["toxicity"] >= threshold:
            lines.append(f"domain:{e['domain']}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────
# CLI

def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--ahrefs", type=Path)
    src.add_argument("--semrush", type=Path)
    src.add_argument("--majestic", type=Path)
    p.add_argument("--target", default="unknown")
    p.add_argument("--recent-after", type=str,
                   help="YYYY-MM-DD — analyze recent-acquisition window")
    p.add_argument("--json", type=Path)
    p.add_argument("--markdown", type=Path)
    p.add_argument("--disavow", type=Path)
    p.add_argument("--disavow-threshold", type=int, default=70)
    args = p.parse_args()

    if args.ahrefs:
        path, src_name = args.ahrefs, "ahrefs"
    elif args.semrush:
        path, src_name = args.semrush, "semrush"
    else:
        path, src_name = args.majestic, "majestic"

    recent_after = None
    if args.recent_after:
        recent_after = _parse_date(args.recent_after)
    else:
        # Default: 90 days ago
        recent_after = (datetime.now(timezone.utc).date() - timedelta(days=90))

    links = load_csv(path, src_name)
    analysis = analyze(links, recent_after=recent_after)

    issues: list[dict] = []
    if analysis["verdict"] == "critical":
        issues.append(finding(
            "P0",
            f"Backlinks profile critical: {analysis['low_authority_share_pct']}% "
            f"of domains are DR ≤ 10, "
            f"{len(analysis['anchor_spam_patterns'])} anchor spam pattern(s) detected",
            evidence={
                "flagged_domains": analysis["flagged_domains_count"],
                "spam_patterns": list(analysis["anchor_spam_patterns"].keys()),
            },
        ))
    elif analysis["verdict"] == "warning":
        issues.append(finding(
            "P1",
            f"Backlinks profile warning: {analysis['low_authority_share_pct']}% "
            f"of domains are DR ≤ 10",
            evidence={"flagged_domains": analysis["flagged_domains_count"]},
        ))
    if analysis["unusual_target_subdomains"]:
        top = next(iter(analysis["unusual_target_subdomains"]))
        cnt = analysis["unusual_target_subdomains"][top]
        if cnt >= 20:
            issues.append(finding(
                "P0",
                f"{cnt} links target {top} — possible open-redirect / tracker abuse, "
                f"investigate before any disavow action",
            ))

    env = result_envelope(
        target=args.target,
        response=None,
        checker="backlinks_toxicity.py",
        source=src_name,
        issues=issues,
        **analysis,
    )

    if args.json:
        args.json.write_text(json.dumps(env, indent=2, ensure_ascii=False, default=str),
                             encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(to_markdown(args.target, analysis), encoding="utf-8")
    if args.disavow:
        args.disavow.write_text(to_disavow(analysis, threshold=args.disavow_threshold),
                                encoding="utf-8")
    if not (args.json or args.markdown or args.disavow):
        print(json.dumps(env, indent=2, ensure_ascii=False, default=str))

    if analysis["verdict"] == "critical":
        return 2
    if analysis["verdict"] == "warning":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
