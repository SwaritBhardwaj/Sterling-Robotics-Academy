#!/usr/bin/env python3
"""
Keyword Intent Classifier (LLM-backed)
──────────────────────────────────────

Classifies every keyword in a CSV into one of:

  - informational   (how to / what is / guide / tutorial)
  - commercial      (best / vs / alternative / review / comparison)
  - transactional   (buy / price / signup / free trial / pricing / get)
  - navigational    (brand name / product name searches)

Then aggregates:
  - count of keywords per intent
  - share of total traffic / impressions per intent  (the "are we ranking
    where buyers are?" question)

Why: the most common diagnosis in an algorithmic-decline audit is "the
catalog skews informational, but the business needs commercial traffic".
Without intent classification this is an eyeball judgement that doesn't
scale past 50 keywords. With it, every keyword universe of 5k+ becomes
a 1-paragraph diagnosis.

Backend: Anthropic Claude (Haiku — cheap and fast for short labels) via
ANTHROPIC_API_KEY env var, or `security find-generic-password -s
anthropic-api-key -w` on macOS.

Inputs:
    --csv PATH           CSV with at minimum a keyword column. Optionally
                         traffic / impressions / volume / clicks columns
                         which are summed per intent.
    --keyword-col NAME   Override auto-detected keyword column
    --metric-col NAME    Override metric column to weight intent traffic by

Outputs:
    --output PATH        Write the input CSV back out with an `intent` column
                         added (and `intent_confidence` if --confidence)
    --json PATH          Aggregated JSON envelope
    --markdown PATH      Aggregated Markdown summary

Cost & speed: batched 50 keywords per request. 5,000 keywords ≈ 100
requests ≈ $0.20-0.40 with Haiku, ~3-5 minutes.

Examples:
    python intent_classifier.py --csv /tmp/keywords.csv \\
        --output /tmp/keywords_classified.csv --markdown /tmp/intent.md
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import SKILL_VERSION, finding, result_envelope  # noqa: E402

import requests


# ─────────────────────────────────────────────────────────────────────────
# API key resolution

def get_api_key() -> str:
    """Resolve ANTHROPIC_API_KEY from env, then macOS Keychain. Raises
    RuntimeError with a clear message instead of dying inside requests."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        out = subprocess.run(
            ["security", "find-generic-password", "-s", "anthropic-api-key", "-w"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise RuntimeError(
        "Anthropic API key not found. Set ANTHROPIC_API_KEY or run "
        "`security add-generic-password -s anthropic-api-key -w '<KEY>'`"
    )


# ─────────────────────────────────────────────────────────────────────────
# Classification

INTENT_OPTIONS = ("informational", "commercial", "transactional", "navigational")
BATCH_SIZE = 50  # keywords per LLM call


CLASSIFY_PROMPT = """You are a search intent classifier for SEO audits.

For each keyword below, output ONE label from this exact list:
- informational   (how to, what is, guide, tutorial, learn, examples, definitions)
- commercial      (best, top, vs, alternative, review, comparison, "X for Y")
- transactional   (buy, price, pricing, free trial, signup, get, download, demo)
- navigational    (brand name, product name, login, "X website")

Rules:
- One label per keyword, lowercase, exact match from the list above.
- Output a JSON array of strings in the SAME ORDER as the keywords given.
- No explanations, no other keys, just the array.
- If unsure, prefer informational > commercial > transactional > navigational.

Keywords (numbered for reference; preserve order):
{keyword_list}

Return ONLY the JSON array, e.g.: ["informational", "commercial", ...]"""


def _classify_batch(keywords: list[str], api_key: str) -> list[str]:
    """Call Claude on one batch. Returns intent labels parallel to input.

    Failures are surfaced as 'unknown' for every keyword in the batch
    rather than aborting — the caller still gets a partial dataset, and
    the unknown share is reported as a quality signal."""
    numbered = "\n".join(f"{i + 1}. {k}" for i, k in enumerate(keywords))
    body = {
        "model": "claude-haiku-4-5",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": CLASSIFY_PROMPT.format(keyword_list=numbered),
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
            timeout=60,
        )
    except requests.RequestException as e:
        print(f"   batch failed: {e}", file=sys.stderr)
        return ["unknown"] * len(keywords)
    if not r.ok:
        print(f"   batch HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
        return ["unknown"] * len(keywords)
    data = r.json()
    text = data.get("content", [{}])[0].get("text", "").strip()
    # Strip any surrounding code fences the model might add despite instructions.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        labels = json.loads(text)
    except json.JSONDecodeError:
        print(f"   batch JSON parse failed: {text[:200]}", file=sys.stderr)
        return ["unknown"] * len(keywords)
    # Pad or trim to match input length (defensive: model sometimes returns
    # fewer items than requested if it merges adjacent duplicates).
    out = []
    for i in range(len(keywords)):
        if i < len(labels) and isinstance(labels[i], str):
            label = labels[i].lower().strip()
            if label in INTENT_OPTIONS:
                out.append(label)
            else:
                out.append("unknown")
        else:
            out.append("unknown")
    return out


def classify_all(keywords: list[str], api_key: str, verbose: bool = True) -> list[str]:
    """Classify the full list, batched. Prints progress to stderr."""
    intents: list[str] = []
    total = len(keywords)
    for i in range(0, total, BATCH_SIZE):
        batch = keywords[i: i + BATCH_SIZE]
        if verbose:
            print(
                f"   classifying {i + 1}-{i + len(batch)} of {total}...",
                file=sys.stderr,
            )
        labels = _classify_batch(batch, api_key)
        intents.extend(labels)
    return intents


# ─────────────────────────────────────────────────────────────────────────
# CSV I/O

KEYWORD_CANDIDATES = ("keyword", "keywords", "query", "search query", "queries")
METRIC_CANDIDATES = (
    "traffic", "current traffic", "organic traffic",
    "impressions", "search impressions",
    "volume", "search volume", "monthly volume",
)


def _normalize(s: str) -> str:
    return s.strip().lower().replace("_", " ").replace("-", " ")


def _detect_col(headers: list[str], candidates: tuple[str, ...]) -> str | None:
    nmap = {h: _normalize(h) for h in headers}
    cand_set = set(candidates)
    for orig, norm in nmap.items():
        if norm in cand_set:
            return orig
    return None


def _safe_num(s: str) -> int:
    s = (s or "").strip().replace(",", "")
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
    p.add_argument("--keyword-col", help="Override keyword column name")
    p.add_argument("--metric-col", help="Override metric column (traffic/impressions/volume)")
    p.add_argument("--output", type=Path, help="Write input CSV back with intent column added")
    p.add_argument("--json", type=Path)
    p.add_argument("--markdown", type=Path)
    p.add_argument("--limit", type=int, default=0,
                   help="Cap to first N keywords (testing — default 0 = all)")
    p.add_argument("--dry-run", action="store_true",
                   help="Skip API calls, mark all as 'unknown' (use to check parsing)")
    args = p.parse_args()

    # Load CSV
    with args.csv.open(encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        kw_col = args.keyword_col or _detect_col(headers, KEYWORD_CANDIDATES)
        m_col = args.metric_col or _detect_col(headers, METRIC_CANDIDATES)
        if not kw_col:
            print(
                f"ERROR: no keyword column found in {headers}. "
                f"Use --keyword-col.", file=sys.stderr,
            )
            return 2
        rows = list(reader)
    if args.limit:
        rows = rows[: args.limit]

    keywords = [r[kw_col].strip() for r in rows]
    metrics = [_safe_num(r.get(m_col, "")) if m_col else 0 for r in rows]

    if args.dry_run:
        intents = ["unknown"] * len(keywords)
    else:
        api_key = get_api_key()
        intents = classify_all(keywords, api_key)

    # Aggregate
    counts = Counter(intents)
    traffic_by_intent: dict[str, int] = defaultdict(int)
    for intent, m in zip(intents, metrics):
        traffic_by_intent[intent] += m
    total_metric = sum(metrics)

    summary = {
        "total_keywords": len(keywords),
        "metric_column": m_col,
        "metric_total": total_metric,
        "by_intent": [
            {
                "intent": k,
                "keyword_count": counts.get(k, 0),
                "keyword_share_pct": round(counts.get(k, 0) / len(keywords) * 100, 1)
                if keywords else 0.0,
                "metric_total": traffic_by_intent.get(k, 0),
                "metric_share_pct": round(traffic_by_intent.get(k, 0) / total_metric * 100, 1)
                if total_metric else 0.0,
            }
            for k in list(INTENT_OPTIONS) + ["unknown"]
        ],
    }

    # P1: catalog skews informational while metric concentrates elsewhere — or
    # commercial intent has <5% of metric (the "we don't rank where buyers
    # search" pattern). Both are quotable diagnoses in the report.
    issues: list[dict] = []
    info_share = next(
        x["keyword_share_pct"] for x in summary["by_intent"] if x["intent"] == "informational"
    )
    commercial_metric_share = next(
        x["metric_share_pct"] for x in summary["by_intent"] if x["intent"] == "commercial"
    )
    transactional_metric_share = next(
        x["metric_share_pct"] for x in summary["by_intent"] if x["intent"] == "transactional"
    )
    buyer_metric_share = commercial_metric_share + transactional_metric_share
    if info_share > 70 and buyer_metric_share < 10:
        issues.append(
            finding(
                "P1",
                f"Catalog skews informational ({info_share}%) while buyer-intent "
                f"queries contribute only {buyer_metric_share:.1f}% of "
                f"{m_col or 'metric'} — the site ranks where buyers don't search",
            )
        )
    elif info_share > 70:
        issues.append(
            finding(
                "P2",
                f"{info_share}% of keywords are informational — consider "
                f"shifting editorial mix toward commercial intent",
            )
        )

    env = result_envelope(
        target=args.target,
        response=None,
        checker="intent_classifier.py",
        summary=summary,
        issues=issues,
    )

    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(headers) + ["intent"])
            w.writeheader()
            for r, intent in zip(rows, intents):
                w.writerow({**r, "intent": intent})
    if args.json:
        args.json.write_text(json.dumps(env, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    if args.markdown:
        md = [
            f"# Keyword Intent · {args.target}",
            "",
            f"Skill: v{SKILL_VERSION}  ·  Total keywords: **{summary['total_keywords']}**  ·  "
            f"Metric column: **{m_col or 'none'}**",
            "",
            "| Intent | Keywords | KW share | Metric total | Metric share |",
            "|---|---:|---:|---:|---:|",
        ]
        for x in summary["by_intent"]:
            md.append(
                f"| {x['intent']} | {x['keyword_count']:,} | {x['keyword_share_pct']}% "
                f"| {x['metric_total']:,} | {x['metric_share_pct']}% |"
            )
        args.markdown.write_text("\n".join(md), encoding="utf-8")
    if not args.json and not args.markdown and not args.output:
        print(json.dumps(env, indent=2, ensure_ascii=False))

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
