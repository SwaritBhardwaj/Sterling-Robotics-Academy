#!/usr/bin/env python3
"""
Keyword Cannibalization Detector
────────────────────────────────

Finds queries where more than one URL of the same site ranks — the classic
"blog post + landing page fight for the same query" pattern. Neither wins;
both leak relevance signals.

Accepts the two CSV shapes you actually get in practice:

  --gsc PATH         GSC "Search results → Queries & Pages" export. Columns
                     expected: Query, Page (or Top page), Clicks,
                     Impressions, Position (or Position avg).
  --ahrefs PATH      Ahrefs Site Explorer → Organic keywords export. Columns
                     expected: Keyword, Current URL (or URL inside),
                     Volume, Position, Traffic.

The detector groups by query, surfaces queries with ≥ --min-urls competing
URLs (default 2), and ranks them by total impressions / traffic so the most
damaging cases come first.

Output: standardized envelope with a `cannibalized` list, each entry
listing the query, total impressions / traffic / clicks, the competing URLs
with their individual positions.

Exit codes:
    0 = no cannibalization above threshold
    1 = cannibalization found, but only low-impression queries
    2 = cannibalization found on high-impression queries (≥ --critical-impr)

Examples:
    python cannibalization_detector.py --gsc /tmp/gsc_queries.csv --markdown out.md
    python cannibalization_detector.py --ahrefs /tmp/ah_keywords.csv \\
        --min-urls 3 --critical-impr 500
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import SKILL_VERSION, finding, result_envelope  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────
# Column auto-detection — both GSC and Ahrefs ship a few variants

GSC_QUERY_COLS = ("query", "search query", "queries")
GSC_PAGE_COLS = ("page", "top page", "url", "landing page")
GSC_CLICKS_COLS = ("clicks", "url clicks")
GSC_IMPR_COLS = ("impressions", "search appearance impressions")
GSC_POS_COLS = ("position", "average position", "position avg", "avg. pos")

AHREFS_KW_COLS = ("keyword", "keywords")
AHREFS_URL_COLS = ("current url", "url inside", "url", "landing url")
AHREFS_VOL_COLS = ("volume", "search volume", "monthly volume")
AHREFS_POS_COLS = ("position", "current position")
AHREFS_TRAFFIC_COLS = ("traffic", "current traffic", "organic traffic")


def _normalize(s: str) -> str:
    return s.strip().lower().replace("_", " ").replace("-", " ")


def _find_col(headers: list[str], candidates: tuple[str, ...]) -> str | None:
    nmap = {h: _normalize(h) for h in headers}
    cand_set = set(candidates)
    for orig, norm in nmap.items():
        if norm in cand_set:
            return orig
    return None


def _safe_int(s: str) -> int:
    s = s.strip().replace(",", "").replace("\xa0", "")
    if not s or s == "-":
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def _safe_float(s: str) -> float:
    s = s.strip().replace(",", "")
    if not s or s == "-":
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


# ─────────────────────────────────────────────────────────────────────────
# Loaders — each returns the canonical record shape:
#   {"query": str, "url": str, "metric": int, "position": float}
# `metric` is impressions for GSC, traffic for Ahrefs. Same downstream code.

def load_gsc(path: Path) -> tuple[list[dict], str]:
    """Returns (rows, metric_label)."""
    with path.open(encoding="utf-8-sig") as f:  # -sig strips BOM if present
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        q_col = _find_col(headers, GSC_QUERY_COLS)
        u_col = _find_col(headers, GSC_PAGE_COLS)
        i_col = _find_col(headers, GSC_IMPR_COLS)
        c_col = _find_col(headers, GSC_CLICKS_COLS)
        p_col = _find_col(headers, GSC_POS_COLS)
        if not q_col or not u_col:
            raise ValueError(
                f"{path}: GSC CSV needs query + page columns. "
                f"Found headers: {headers}"
            )
        rows = []
        for r in reader:
            rows.append(
                {
                    "query": r[q_col].strip(),
                    "url": r[u_col].strip(),
                    "metric": _safe_int(r[i_col]) if i_col else 0,
                    "clicks": _safe_int(r[c_col]) if c_col else 0,
                    "position": _safe_float(r[p_col]) if p_col else 0.0,
                }
            )
        return rows, "impressions"


def load_ahrefs(path: Path) -> tuple[list[dict], str]:
    """Returns (rows, metric_label)."""
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        k_col = _find_col(headers, AHREFS_KW_COLS)
        u_col = _find_col(headers, AHREFS_URL_COLS)
        t_col = _find_col(headers, AHREFS_TRAFFIC_COLS)
        v_col = _find_col(headers, AHREFS_VOL_COLS)
        p_col = _find_col(headers, AHREFS_POS_COLS)
        if not k_col or not u_col:
            raise ValueError(
                f"{path}: Ahrefs CSV needs keyword + URL columns. "
                f"Found headers: {headers}"
            )
        # Prefer traffic; fall back to volume if traffic not present
        m_col = t_col or v_col
        rows = []
        for r in reader:
            rows.append(
                {
                    "query": r[k_col].strip(),
                    "url": r[u_col].strip(),
                    "metric": _safe_int(r[m_col]) if m_col else 0,
                    "clicks": 0,  # Ahrefs export doesn't carry clicks
                    "position": _safe_float(r[p_col]) if p_col else 0.0,
                }
            )
        return rows, "traffic" if t_col else "volume"


# ─────────────────────────────────────────────────────────────────────────
# Core: group + detect

def detect(
    rows: list[dict],
    *,
    min_urls: int = 2,
    min_metric: int = 0,
) -> list[dict]:
    """Group rows by query; return queries with ≥ min_urls distinct URLs.

    Within each query, sort URLs by position ascending (top rankers first).
    Compute total impressions/traffic across all competing URLs.
    """
    by_query: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        if not r["query"] or not r["url"]:
            continue
        by_query[r["query"]].append(r)

    cannibalized = []
    for query, items in by_query.items():
        # Aggregate per URL — the same query/page pair can repeat in a CSV
        # if dates are split. We sum metrics, take min position.
        per_url: dict[str, dict] = {}
        for it in items:
            u = it["url"]
            if u not in per_url:
                per_url[u] = {
                    "url": u,
                    "metric": 0,
                    "clicks": 0,
                    "position": float("inf"),
                }
            per_url[u]["metric"] += it["metric"]
            per_url[u]["clicks"] += it["clicks"]
            if it["position"] > 0:
                per_url[u]["position"] = min(per_url[u]["position"], it["position"])

        if len(per_url) < min_urls:
            continue

        urls = list(per_url.values())
        for u in urls:
            if u["position"] == float("inf"):
                u["position"] = None
            else:
                u["position"] = round(u["position"], 1)
        urls.sort(
            key=lambda u: (
                u["position"] if u["position"] is not None else 999,
                -u["metric"],
            )
        )
        total_metric = sum(u["metric"] for u in urls)
        if total_metric < min_metric:
            continue
        cannibalized.append(
            {
                "query": query,
                "url_count": len(urls),
                "total_metric": total_metric,
                "total_clicks": sum(u["clicks"] for u in urls),
                "urls": urls,
            }
        )

    cannibalized.sort(key=lambda x: -x["total_metric"])
    return cannibalized


# ─────────────────────────────────────────────────────────────────────────
# Markdown

def to_markdown(
    target: str,
    cannibalized: list[dict],
    metric_label: str,
    critical_impr: int,
) -> str:
    lines = [
        f"# Keyword Cannibalization · {target}",
        "",
        f"Skill: v{SKILL_VERSION}  ·  Queries with ≥2 ranking URLs: "
        f"**{len(cannibalized)}**  ·  Metric: **{metric_label}**",
        "",
    ]
    if not cannibalized:
        lines.append("No cannibalization detected above threshold.")
        return "\n".join(lines)

    critical = [c for c in cannibalized if c["total_metric"] >= critical_impr]
    if critical:
        lines.append(f"## Critical (≥{critical_impr} {metric_label})")
        lines.append("")
        lines.append(f"| Query | URLs | Total {metric_label} | Top URL | Pos |")
        lines.append("|---|---:|---:|---|---:|")
        for c in critical[:30]:
            top = c["urls"][0]
            lines.append(
                f"| {c['query']} | {c['url_count']} | {c['total_metric']:,} "
                f"| {top['url']} | {top['position']} |"
            )
        lines.append("")

    lines.append("## All cannibalized queries (top 50 by metric)")
    lines.append("")
    lines.append(f"| Query | URLs | Total {metric_label} | Competing URLs (pos) |")
    lines.append("|---|---:|---:|---|")
    for c in cannibalized[:50]:
        urls_str = " · ".join(
            f"{u['url']} (#{u['position']})" for u in c["urls"][:3]
        )
        if len(c["urls"]) > 3:
            urls_str += f" · +{len(c['urls']) - 3} more"
        lines.append(
            f"| {c['query']} | {c['url_count']} | {c['total_metric']:,} | {urls_str} |"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────
# CLI

def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--gsc", type=Path, help="GSC Queries & Pages CSV")
    src.add_argument("--ahrefs", type=Path, help="Ahrefs Organic keywords CSV")
    p.add_argument("--target", default="unknown")
    p.add_argument("--min-urls", type=int, default=2,
                   help="Minimum competing URLs to flag (default 2)")
    p.add_argument("--min-metric", type=int, default=0,
                   help="Minimum total impressions/traffic to include")
    p.add_argument("--critical-impr", type=int, default=500,
                   help="Threshold for P0 critical cannibalization (default 500)")
    p.add_argument("--json", type=Path)
    p.add_argument("--markdown", type=Path)
    args = p.parse_args()

    if args.gsc:
        rows, metric_label = load_gsc(args.gsc)
        source = "gsc"
    else:
        rows, metric_label = load_ahrefs(args.ahrefs)
        source = "ahrefs"

    cannibalized = detect(
        rows,
        min_urls=args.min_urls,
        min_metric=args.min_metric,
    )

    # P0/P1 issues
    issues: list[dict] = []
    critical = [c for c in cannibalized if c["total_metric"] >= args.critical_impr]
    if critical:
        issues.append(
            finding(
                "P0",
                f"{len(critical)} high-{metric_label} queries are cannibalized "
                f"(≥{args.critical_impr} {metric_label} each)",
                evidence={
                    "top_queries": [
                        {"q": c["query"], "metric": c["total_metric"],
                         "url_count": c["url_count"]}
                        for c in critical[:10]
                    ]
                },
            )
        )
    elif cannibalized:
        issues.append(
            finding(
                "P1",
                f"{len(cannibalized)} cannibalized queries detected (all below "
                f"{args.critical_impr} {metric_label} threshold)",
            )
        )

    env = result_envelope(
        target=args.target,
        response=None,
        checker="cannibalization_detector.py",
        source=source,
        metric_label=metric_label,
        total_queries_analyzed=len({r["query"] for r in rows if r["query"]}),
        cannibalized_count=len(cannibalized),
        critical_count=len(critical),
        cannibalized=cannibalized[:200],  # cap output to keep envelope sane
        issues=issues,
    )

    if args.json:
        args.json.write_text(json.dumps(env, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(
            to_markdown(args.target, cannibalized, metric_label, args.critical_impr),
            encoding="utf-8",
        )
    if not args.json and not args.markdown:
        print(json.dumps(env, indent=2, ensure_ascii=False))

    if critical:
        return 2
    if cannibalized:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
