#!/usr/bin/env python3
"""
Content Tier Classifier (LLM-backed)
────────────────────────────────────

Classifies every URL on a site into the consultant tier model commonly
used in premium SEO engagements:

  A_product            Product, pricing, signup, feature pages.
                       The pages the business needs to rank.
  A_blog_relevant      Blog posts directly tied to the product narrative
                       (deliverability, SMTP, API, transactional flow for
                       an email business; staking, custody, security for a
                       crypto wallet, etc).
  B_dev_tutorial       Tutorials adjacent to the product but only
                       tangentially commercial ("send email with X").
                       Useful but rarely converts.
  C_divergent          Content drifting away from the product domain
                       (consumer email tasks, generic productivity tips,
                       random "how to" posts). The pages Google's recent
                       core/spam updates demote hardest.

Then aggregates per tier:
  - URL share (count + %)
  - traffic / impression share (if a metric column is provided)
  - the disproportion ratio between URL share and metric share —
    the "12% of URLs drives 40% of traffic but it's the wrong content" story.

Backend: Claude Haiku via ANTHROPIC_API_KEY (env) or macOS Keychain entry
`anthropic-api-key`. Classification uses URL path + title + first 1k chars
of body when available; URL alone if that's all we have.

Inputs:
    --csv PATH          CSV with URL column (required). Optional: title,
                        h1, traffic / impressions / clicks columns.
    --product-domain    What the business actually sells (e.g.
                        "transactional email", "non-custodial crypto wallet").
                        Used in the LLM prompt to anchor relevance judgement.

Outputs:
    --output PATH       Input CSV with `tier` column added
    --json PATH         Aggregated JSON envelope
    --markdown PATH     Tier breakdown table

Example:
    python content_tier_classifier.py --csv /tmp/urls.csv \\
        --product-domain "transactional email API" \\
        --output /tmp/urls_tiered.csv --markdown /tmp/tiers.md
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import SKILL_VERSION, finding, result_envelope  # noqa: E402

import requests


TIERS = ("A_product", "A_blog_relevant", "B_dev_tutorial", "C_divergent")
BATCH_SIZE = 30  # smaller than intent because each row carries more context


def get_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", "anthropic-api-key", "-w"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise RuntimeError("Anthropic API key not found")


CLASSIFY_PROMPT = """You classify URLs by their content tier relative to a business.

Business domain: **{product_domain}**

For each URL below, output ONE label from this exact list:
- A_product           — product, pricing, signup, feature, integration pages of the business
- A_blog_relevant     — blog content directly tied to the product narrative
- B_dev_tutorial      — technical tutorial adjacent to the product (low commercial intent)
- C_divergent         — content unrelated to the product domain (generic consumer tasks, unrelated topics)

Rules:
- One label per URL, exact match from the list above.
- Use the URL path AND title AND snippet to judge.
- Return a JSON array of strings in the same order as URLs given.
- No explanations, no other keys.

URLs (numbered; preserve order):
{url_list}

Return ONLY the JSON array."""


def _format_url_block(idx: int, row: dict) -> str:
    parts = [f"{idx + 1}. URL: {row['url']}"]
    if row.get("title"):
        parts.append(f"   Title: {row['title']}")
    if row.get("h1") and row.get("h1") != row.get("title"):
        parts.append(f"   H1: {row['h1']}")
    if row.get("snippet"):
        parts.append(f"   Snippet: {row['snippet'][:200]}")
    return "\n".join(parts)


def _classify_batch(rows: list[dict], product_domain: str, api_key: str) -> list[str]:
    url_list = "\n\n".join(_format_url_block(i, r) for i, r in enumerate(rows))
    body = {
        "model": "claude-haiku-4-5",
        "max_tokens": 2048,
        "messages": [
            {
                "role": "user",
                "content": CLASSIFY_PROMPT.format(
                    product_domain=product_domain,
                    url_list=url_list,
                ),
            }
        ],
    }
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=body,
            timeout=90,
        )
    except requests.RequestException as e:
        print(f"   batch failed: {e}", file=sys.stderr)
        return ["unknown"] * len(rows)
    if not r.ok:
        print(f"   batch HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
        return ["unknown"] * len(rows)
    text = r.json().get("content", [{}])[0].get("text", "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        labels = json.loads(text)
    except json.JSONDecodeError:
        print(f"   parse fail: {text[:200]}", file=sys.stderr)
        return ["unknown"] * len(rows)
    out = []
    for i in range(len(rows)):
        if i < len(labels) and isinstance(labels[i], str):
            label = labels[i].strip()
            out.append(label if label in TIERS else "unknown")
        else:
            out.append("unknown")
    return out


# ─────────────────────────────────────────────────────────────────────────
# CSV detection

URL_COLS = ("url", "page", "top page", "address", "landing url", "landing page")
TITLE_COLS = ("title", "title 1", "page title", "meta title")
H1_COLS = ("h1", "h1 1", "h1-1")
SNIPPET_COLS = ("meta description", "description", "snippet")
METRIC_COLS = (
    "traffic", "current traffic", "organic traffic",
    "impressions", "clicks", "url clicks",
)


def _normalize(s: str) -> str:
    return s.strip().lower().replace("_", " ").replace("-", " ")


def _detect(headers: list[str], candidates: tuple[str, ...]) -> str | None:
    nmap = {h: _normalize(h) for h in headers}
    cand = set(candidates)
    for orig, norm in nmap.items():
        if norm in cand:
            return orig
    return None


def _safe_num(s: Any) -> int:
    s = (str(s) if s is not None else "").strip().replace(",", "")
    if not s:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--target", default="unknown")
    p.add_argument("--product-domain", required=True,
                   help="What the business actually sells (anchors LLM judgement)")
    p.add_argument("--url-col", help="Override URL column")
    p.add_argument("--metric-col", help="Override metric column")
    p.add_argument("--output", type=Path)
    p.add_argument("--json", type=Path)
    p.add_argument("--markdown", type=Path)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--dry-run", action="store_true",
                   help="Skip API calls; label everything 'unknown'")
    args = p.parse_args()

    with args.csv.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        u_col = args.url_col or _detect(headers, URL_COLS)
        t_col = _detect(headers, TITLE_COLS)
        h_col = _detect(headers, H1_COLS)
        s_col = _detect(headers, SNIPPET_COLS)
        m_col = args.metric_col or _detect(headers, METRIC_COLS)
        if not u_col:
            print(f"ERROR: no URL column. Headers: {headers}", file=sys.stderr)
            return 2
        rows = list(reader)
    if args.limit:
        rows = rows[: args.limit]

    enriched = []
    for r in rows:
        enriched.append(
            {
                "url": r[u_col].strip(),
                "title": (r.get(t_col, "") if t_col else "").strip(),
                "h1": (r.get(h_col, "") if h_col else "").strip(),
                "snippet": (r.get(s_col, "") if s_col else "").strip(),
                "metric": _safe_num(r.get(m_col, "")) if m_col else 0,
                "_raw": r,
            }
        )

    if args.dry_run:
        tiers = ["unknown"] * len(enriched)
    else:
        api_key = get_api_key()
        tiers = []
        for i in range(0, len(enriched), BATCH_SIZE):
            batch = enriched[i: i + BATCH_SIZE]
            print(
                f"   classifying {i + 1}-{i + len(batch)} of {len(enriched)}...",
                file=sys.stderr,
            )
            tiers.extend(_classify_batch(batch, args.product_domain, api_key))

    counts = Counter(tiers)
    metric_by_tier: dict[str, int] = defaultdict(int)
    for t, row in zip(tiers, enriched):
        metric_by_tier[t] += row["metric"]
    total_metric = sum(r["metric"] for r in enriched)
    n = len(enriched)

    summary = {
        "total_urls": n,
        "product_domain": args.product_domain,
        "metric_column": m_col,
        "metric_total": total_metric,
        "by_tier": [
            {
                "tier": k,
                "url_count": counts.get(k, 0),
                "url_share_pct": round(counts.get(k, 0) / n * 100, 1) if n else 0.0,
                "metric_total": metric_by_tier.get(k, 0),
                "metric_share_pct": round(metric_by_tier.get(k, 0) / total_metric * 100, 1)
                if total_metric else 0.0,
            }
            for k in list(TIERS) + ["unknown"]
        ],
    }

    # "Disproportion" story: when C_divergent shows metric_share > 2× its
    # url_share, the site is leaking authority to off-topic pages.
    issues: list[dict] = []
    c = next(x for x in summary["by_tier"] if x["tier"] == "C_divergent")
    a = next(x for x in summary["by_tier"] if x["tier"] == "A_product")
    if c["metric_share_pct"] > 2 * c["url_share_pct"] and c["metric_share_pct"] > 15:
        issues.append(
            finding(
                "P1",
                f"Divergent content ({c['url_share_pct']}% of URLs) captures "
                f"{c['metric_share_pct']}% of {m_col or 'metric'} — authority "
                f"is concentrated on content unrelated to {args.product_domain}",
            )
        )
    if a["metric_share_pct"] < 10 and total_metric > 0:
        issues.append(
            finding(
                "P0",
                f"Product pages capture only {a['metric_share_pct']}% of "
                f"{m_col or 'metric'} — buyers don't see the actual product offering",
            )
        )

    env = result_envelope(
        target=args.target,
        response=None,
        checker="content_tier_classifier.py",
        summary=summary,
        issues=issues,
    )

    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(headers) + ["tier"])
            w.writeheader()
            for row, tier in zip(rows, tiers):
                w.writerow({**row, "tier": tier})
    if args.json:
        args.json.write_text(json.dumps(env, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    if args.markdown:
        md = [
            f"# Content Tier Breakdown · {args.target}",
            "",
            f"Skill: v{SKILL_VERSION}  ·  URLs: **{n}**  ·  "
            f"Product domain: **{args.product_domain}**",
            "",
            "| Tier | URLs | URL share | Metric | Metric share |",
            "|---|---:|---:|---:|---:|",
        ]
        for x in summary["by_tier"]:
            md.append(
                f"| {x['tier']} | {x['url_count']} | {x['url_share_pct']}% "
                f"| {x['metric_total']:,} | {x['metric_share_pct']}% |"
            )
        args.markdown.write_text("\n".join(md), encoding="utf-8")
    if not args.json and not args.markdown and not args.output:
        print(json.dumps(env, indent=2, ensure_ascii=False))

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
