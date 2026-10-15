#!/usr/bin/env python3
"""
Google Updates Correlator
─────────────────────────

Aligns a site's traffic time series with the official Google search algorithm
update calendar. For every known update, computes the Δ% in clicks and
impressions between the 14 days *before* the start_date and the 14 days
*after* the end_date.

This is the "what broke and when" view that turns a generic "traffic is down"
chart into a layered diagnosis: which updates actually moved the needle,
which were benign, and whether the pattern fits a content / spam / discover
classification.

Inputs (CSV, one of):
    --gsc-daily PATH       Daily export from GSC Performance report.
                           Columns: Date, Clicks, Impressions (Ahrefs and
                           Search Console "Export → CSV" both work).
    --ahrefs-traffic PATH  Daily Ahrefs organic traffic export.
                           Columns: Date, Traffic
    --custom PATH          Generic CSV with explicit column names via
                           --date-col / --clicks-col / --impressions-col

The calendar lives in references/google_updates.json (verified against
status.search.google.com / Search Engine Land). You can override the window
size with --window-days (default 14).

Output: standardized envelope with one row per update + Δ%, Δ absolute,
severity, "hit" verdict (major/partial/benign/recovery). Markdown table
also written when --markdown PATH is provided.

Example:
    python google_updates_correlator.py \\
        --gsc-daily /tmp/gsc_daily.csv \\
        --markdown /tmp/updates.md \\
        --json /tmp/updates.json
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

# Import sibling envelope helpers without requiring scripts/ on PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import SKILL_VERSION, finding, result_envelope  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────
# Calendar loader

CALENDAR_PATH = (
    Path(__file__).resolve().parent.parent / "references" / "google_updates.json"
)


def load_calendar(path: Path = CALENDAR_PATH) -> list[dict]:
    """Load the verified Google updates calendar. Raises FileNotFoundError
    with a helpful message if the calendar is missing — checkers downstream
    rely on this being present at install time."""
    if not path.exists():
        raise FileNotFoundError(
            f"google_updates.json not found at {path}. "
            "Re-install / re-clone the skill to restore references/."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("updates", [])


# ─────────────────────────────────────────────────────────────────────────
# CSV loader

def _parse_date(s: str) -> date:
    """Tolerant date parser. Handles ISO (2026-01-15), US (1/15/2026),
    and 'Jan 15, 2026'. Returns date, not datetime, since updates are
    day-resolution."""
    s = s.strip().strip('"').strip("'")
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%d %b %Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {s!r}")


def _normalize_header(h: str) -> str:
    return h.strip().lower().replace(" ", "_").replace("-", "_")


def load_csv(
    path: Path,
    *,
    date_col: str | None = None,
    clicks_col: str | None = None,
    impressions_col: str | None = None,
) -> list[dict]:
    """Parse a daily-traffic CSV into a list of {date, clicks, impressions}.

    Auto-detects common column names: date / clicks / impressions / traffic
    / organic_traffic. Falls back to explicit column names when provided
    (case-insensitive). Returns rows sorted by date ascending.
    """
    with path.open(encoding="utf-8") as f:
        # GSC exports sometimes ship UTF-8 BOM; tolerate it.
        first = f.read(1)
        if first != "﻿":
            f.seek(0)
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"{path}: empty CSV or unreadable header")
        norm_map = {fn: _normalize_header(fn) for fn in reader.fieldnames}

        def pick(*candidates: str, explicit: str | None = None) -> str | None:
            if explicit:
                explicit_norm = _normalize_header(explicit)
                for orig, norm in norm_map.items():
                    if norm == explicit_norm:
                        return orig
                raise ValueError(
                    f"{path}: column {explicit!r} not in {reader.fieldnames}"
                )
            for cand in candidates:
                for orig, norm in norm_map.items():
                    if norm == cand:
                        return orig
            return None

        date_field = pick("date", "day", explicit=date_col)
        clicks_field = pick("clicks", "click", explicit=clicks_col)
        impr_field = pick(
            "impressions",
            "impression",
            "traffic",
            "organic_traffic",
            explicit=impressions_col,
        )
        if not date_field:
            raise ValueError(
                f"{path}: no date column found (looked for date/day, "
                f"got {reader.fieldnames})"
            )
        if not clicks_field and not impr_field:
            raise ValueError(
                f"{path}: need at least one of clicks/impressions/traffic, "
                f"got {reader.fieldnames}"
            )

        rows: list[dict] = []
        for raw in reader:
            try:
                d = _parse_date(raw[date_field])
            except ValueError:
                continue  # skip malformed rows rather than abort
            row = {"date": d}
            if clicks_field:
                row["clicks"] = _safe_int(raw.get(clicks_field, ""))
            if impr_field:
                row["impressions"] = _safe_int(raw.get(impr_field, ""))
            rows.append(row)
    rows.sort(key=lambda r: r["date"])
    return rows


def _safe_int(s: str) -> int:
    """Convert '1,234' / '1234' / '' to int. Returns 0 on parse failure
    (better than crashing on a stray empty cell)."""
    s = s.strip().replace(",", "")
    if not s:
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


# ─────────────────────────────────────────────────────────────────────────
# Correlation core

def _sum_window(
    rows: list[dict],
    start: date,
    end: date,
    metric: str,
) -> tuple[int, int]:
    """Sum metric over [start, end] inclusive. Returns (sum, days_with_data).
    A window with zero rows is flagged via days_with_data so callers can
    suppress unreliable Δ% on missing data."""
    total = 0
    days = 0
    for r in rows:
        if start <= r["date"] <= end:
            total += r.get(metric, 0)
            days += 1
    return total, days


def _delta_pct(before: int, after: int) -> float | None:
    """Δ% with safe div-by-zero. Returns None when before==0 (a percentage
    against zero baseline is meaningless and would mislead the report)."""
    if before == 0:
        return None
    return round(((after - before) / before) * 100, 1)


def _verdict(d_clicks: float | None, d_impr: float | None) -> str:
    """Classify the impact pattern of a single update.

    Rules (intentionally conservative — better to under-call than over-call):
      - major_hit:   either metric ≤ -20%
      - partial:    either metric ≤ -10% (but not major)
      - benign:     both metrics within ±5%
      - recovery:   either metric ≥ +20%
      - mixed:      everything else (e.g. +impr, -clicks)
      - insufficient_data: one or both metrics missing
    """
    if d_clicks is None and d_impr is None:
        return "insufficient_data"
    worst = min(v for v in (d_clicks, d_impr) if v is not None)
    best = max(v for v in (d_clicks, d_impr) if v is not None)
    if worst <= -20:
        return "major_hit"
    if worst <= -10:
        return "partial"
    if best >= 20:
        return "recovery"
    # both within ±5
    if all(
        v is not None and -5 <= v <= 5
        for v in (d_clicks, d_impr)
        if v is not None
    ):
        return "benign"
    return "mixed"


def correlate(
    rows: list[dict],
    updates: list[dict],
    window_days: int = 14,
    min_data_coverage: float = 0.5,
) -> list[dict]:
    """For each update, compute Δ% windows. Skips updates entirely outside
    the data range. Flags low-coverage windows so callers can mark them
    'insufficient_data' instead of trusting noisy numbers.

    min_data_coverage: fraction of days in each window that must have a
                      row in the CSV. Below this, verdict becomes
                      insufficient_data.
    """
    if not rows:
        return []
    data_start = rows[0]["date"]
    data_end = rows[-1]["date"]
    out = []

    for upd in updates:
        start = _parse_date(upd["start_date"])
        end = _parse_date(upd["end_date"])
        before_end = start - timedelta(days=1)
        before_start = before_end - timedelta(days=window_days - 1)
        after_start = end + timedelta(days=1)
        after_end = after_start + timedelta(days=window_days - 1)

        # Skip updates where either window falls entirely outside the data.
        if after_end < data_start or before_start > data_end:
            continue

        has_clicks = "clicks" in rows[0]
        has_impr = "impressions" in rows[0]

        if has_clicks:
            b_clicks, b_days_c = _sum_window(rows, before_start, before_end, "clicks")
            a_clicks, a_days_c = _sum_window(rows, after_start, after_end, "clicks")
            d_clicks = _delta_pct(b_clicks, a_clicks)
            coverage_c = min(b_days_c, a_days_c) / window_days
        else:
            b_clicks = a_clicks = d_clicks = None
            coverage_c = 1.0  # not applicable

        if has_impr:
            b_impr, b_days_i = _sum_window(rows, before_start, before_end, "impressions")
            a_impr, a_days_i = _sum_window(rows, after_start, after_end, "impressions")
            d_impr = _delta_pct(b_impr, a_impr)
            coverage_i = min(b_days_i, a_days_i) / window_days
        else:
            b_impr = a_impr = d_impr = None
            coverage_i = 1.0

        coverage = min(coverage_c, coverage_i)
        if coverage < min_data_coverage:
            verdict = "insufficient_data"
        else:
            verdict = _verdict(d_clicks, d_impr)

        out.append(
            {
                "update_id": upd["id"],
                "update_name": upd["name"],
                "type": upd["type"],
                "severity": upd["severity"],
                "start_date": upd["start_date"],
                "end_date": upd["end_date"],
                "before_window": [before_start.isoformat(), before_end.isoformat()],
                "after_window": [after_start.isoformat(), after_end.isoformat()],
                "clicks_before": b_clicks,
                "clicks_after": a_clicks,
                "delta_clicks_pct": d_clicks,
                "impressions_before": b_impr,
                "impressions_after": a_impr,
                "delta_impressions_pct": d_impr,
                "coverage_pct": round(coverage * 100, 1),
                "verdict": verdict,
            }
        )
    return out


# ─────────────────────────────────────────────────────────────────────────
# Reporting

def to_markdown(target: str, rows: list[dict], data_range: tuple[date, date]) -> str:
    """Render the correlation result as a consultant-grade Markdown table."""
    lines = [
        f"# Google Updates Impact · {target}",
        "",
        f"Data range: **{data_range[0]} → {data_range[1]}**  ·  "
        f"Calendar: `references/google_updates.json`  ·  "
        f"Skill: v{SKILL_VERSION}",
        "",
        "| Update | Window | Δ Clicks | Δ Impressions | Verdict |",
        "|---|---|---:|---:|---|",
    ]
    for r in rows:
        # Hide Δ% numbers when the window had insufficient coverage — a
        # window with one side empty looks like -100% which misleads the
        # reader. The verdict column already says "insufficient data".
        insufficient = r["verdict"] == "insufficient_data"

        def fmt(x: float | None, hide: bool = insufficient) -> str:
            if hide or x is None:
                return "—"
            return f"{x:+.1f}%"

        verdict_badges = {
            "major_hit": "🔴 major hit",
            "partial": "🟡 partial",
            "benign": "⚪️ benign",
            "recovery": "🟢 recovery",
            "mixed": "🟠 mixed",
            "insufficient_data": "⚫️ insufficient data",
        }
        lines.append(
            f"| {r['update_name']} "
            f"| {r['start_date']} → {r['end_date']} "
            f"| {fmt(r['delta_clicks_pct'])} "
            f"| {fmt(r['delta_impressions_pct'])} "
            f"| {verdict_badges.get(r['verdict'], r['verdict'])} |"
        )
    lines.append("")
    lines.append(
        "_Windows compare 14 days before each update's start vs 14 days "
        "after its end. `insufficient_data` means the data range did not "
        "cover at least 50% of either window._"
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Align traffic data with verified Google updates calendar.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--gsc-daily", type=Path, help="GSC daily export CSV")
    src.add_argument("--ahrefs-traffic", type=Path, help="Ahrefs daily traffic CSV")
    src.add_argument("--custom", type=Path, help="Custom CSV (use --*-col flags)")

    p.add_argument("--target", default="unknown", help="Site label for the report")
    p.add_argument("--window-days", type=int, default=14, help="Window size (default 14)")
    p.add_argument("--date-col", help="Custom CSV: date column name")
    p.add_argument("--clicks-col", help="Custom CSV: clicks column name")
    p.add_argument("--impressions-col", help="Custom CSV: impressions/traffic column name")
    p.add_argument("--json", type=Path, help="Write JSON envelope to this path")
    p.add_argument("--markdown", type=Path, help="Write Markdown table to this path")
    p.add_argument(
        "--calendar",
        type=Path,
        default=CALENDAR_PATH,
        help="Override calendar path (default: references/google_updates.json)",
    )

    args = p.parse_args()

    csv_path = args.gsc_daily or args.ahrefs_traffic or args.custom
    rows = load_csv(
        csv_path,
        date_col=args.date_col,
        clicks_col=args.clicks_col,
        impressions_col=args.impressions_col,
    )
    if not rows:
        print(f"ERROR: no usable rows in {csv_path}", file=sys.stderr)
        return 2

    updates = load_calendar(args.calendar)
    results = correlate(rows, updates, window_days=args.window_days)

    # Severity rollup as P0/P1/P2 issues for downstream page_score / dashboard.
    issues: list[dict] = []
    major_hits = [r for r in results if r["verdict"] == "major_hit"]
    partials = [r for r in results if r["verdict"] == "partial"]
    if major_hits:
        issues.append(
            finding(
                "P0",
                f"{len(major_hits)} Google update(s) caused major traffic drops "
                f"(≥-20% on clicks or impressions, 14-day windows)",
                evidence={
                    "updates": [
                        {"name": r["update_name"], "delta_clicks": r["delta_clicks_pct"]}
                        for r in major_hits
                    ]
                },
            )
        )
    if partials:
        issues.append(
            finding(
                "P1",
                f"{len(partials)} Google update(s) caused partial traffic drops "
                f"(-10% to -20% on either metric)",
                evidence={
                    "updates": [
                        {"name": r["update_name"], "delta_clicks": r["delta_clicks_pct"]}
                        for r in partials
                    ]
                },
            )
        )

    envelope = result_envelope(
        target=args.target,
        response=None,
        checker="google_updates_correlator.py",
        data_range=[rows[0]["date"].isoformat(), rows[-1]["date"].isoformat()],
        window_days=args.window_days,
        updates_in_range=len(results),
        major_hits=len(major_hits),
        partial_hits=len(partials),
        results=results,
        issues=issues,
    )

    if args.json:
        args.json.write_text(json.dumps(envelope, indent=2, default=str), encoding="utf-8")
    if args.markdown:
        md = to_markdown(args.target, results, (rows[0]["date"], rows[-1]["date"]))
        args.markdown.write_text(md, encoding="utf-8")

    if not args.json and not args.markdown:
        print(json.dumps(envelope, indent=2, default=str))

    # Exit code communicates findings to shell pipelines:
    #   0 = no major/partial hits (or insufficient data)
    #   1 = partial hits only
    #   2 = at least one major hit
    if major_hits:
        return 2
    if partials:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
