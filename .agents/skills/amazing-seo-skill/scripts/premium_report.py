#!/usr/bin/env python3
"""
Premium Audit Report Renderer
─────────────────────────────

Consumes one or more JSON envelopes from the v0.8.0 checker family and
renders a consultant-grade HTML report with a premium editorial aesthetic:

  - DM Serif Display headlines + Inter body + JetBrains Mono labels
  - Monochrome (off-white background, near-black ink) with a single
    accent colour (default `#00d4aa` mint; tunable via --accent)
  - Sticky sidebar nav, numbered sections, dense data tables
  - TL;DR card at the top auto-extracted from P0/P1 findings
  - One self-contained HTML file — no external assets except Google Fonts

Each envelope from the canonical checkers maps to a section in the report:

  google_updates_correlator.py   →  §1 Algorithmic Timeline
  sitemap_freshness.py            →  §2 Content Cadence & Decay
  cannibalization_detector.py     →  §3 Keyword Cannibalization
  intent_classifier.py             →  §4 Intent Composition
  content_tier_classifier.py       →  §5 Content Tier Disproportion
  eeat_antipatterns.py             →  §6 E-E-A-T Anti-Patterns
  backlinks_toxicity.py            →  §7 Backlinks Profile
  page_score.py / *                →  §∞ Appendix (any other envelope)

Sections silently absent when their envelope isn't supplied — drop in the
ones you have, the report shrinks to fit.

Usage:
    python premium_report.py \\
        --target example.com \\
        --client "Acme Inc" \\
        --prepared-by "Your Name" \\
        --output /tmp/report.html \\
        envelopes/*.json
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import SKILL_VERSION  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────
# Section renderers — each takes the envelope dict, returns an HTML string

def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _badge(severity: str) -> str:
    cls = {"P0": "crit", "P1": "med", "P2": "low"}.get(severity, "neutral")
    return f'<span class="badge {cls}">{severity}</span>'


def _verdict_badge(verdict: str) -> str:
    palette = {
        "major_hit": ("crit", "🔴 major hit"),
        "partial": ("med", "🟡 partial"),
        "benign": ("low", "⚪️ benign"),
        "recovery": ("low", "🟢 recovery"),
        "mixed": ("med", "🟠 mixed"),
        "insufficient_data": ("neutral", "⚫️ insufficient"),
        "critical": ("crit", "critical"),
        "warning": ("med", "warning"),
        "clean": ("low", "clean"),
        "healthy": ("low", "healthy"),
        "warning_decay": ("med", "warning"),
        "critical_decay": ("crit", "critical decay"),
        "bulk_updates_present": ("med", "bulk updates"),
        "no_lastmod_signal": ("crit", "no signal"),
    }
    cls, label = palette.get(verdict, ("neutral", verdict))
    return f'<span class="badge {cls}">{_esc(label)}</span>'


def render_google_updates(env: dict) -> str:
    if not env:
        return ""
    results = env.get("results", [])
    if not results:
        return ""
    rows_html = []
    for r in results:
        def fmt(x):
            if x is None or r["verdict"] == "insufficient_data":
                return "—"
            return f"{x:+.1f}%"
        rows_html.append(f"""
        <tr>
          <td><b>{_esc(r['update_name'])}</b><br>
              <span class="mono small">{_esc(r['start_date'])} → {_esc(r['end_date'])}</span></td>
          <td class="num">{fmt(r.get('delta_clicks_pct'))}</td>
          <td class="num">{fmt(r.get('delta_impressions_pct'))}</td>
          <td>{_verdict_badge(r['verdict'])}</td>
        </tr>""")
    data_range = env.get("data_range", ["?", "?"])
    return f"""
    <section id="updates"><h2><span class="num">01</span> Algorithmic Timeline</h2>
    <p class="lede">Δ clicks & impressions between the 14 days before each
    Google update's start and the 14 days after its end. Data range:
    <b>{_esc(data_range[0])} → {_esc(data_range[1])}</b>.</p>
    <div class="card">
      <table><thead><tr><th>Update</th><th class="num">Δ Clicks</th>
      <th class="num">Δ Impressions</th><th>Verdict</th></tr></thead>
      <tbody>{''.join(rows_html)}</tbody></table>
    </div></section>"""


def render_sitemap_freshness(env: dict) -> str:
    if not env:
        return ""
    buckets = env.get("age_buckets", {})
    if not buckets:
        return ""
    total = env["total_urls"]
    rows = []
    labels = [
        ("last_30d", "Last 30 days"),
        ("31_90d", "31–90 days"),
        ("91_180d", "91–180 days"),
        ("181_365d", "181–365 days"),
        ("1y_2y", "1–2 years"),
        ("older_than_2y", "Older than 2y"),
    ]
    for key, label in labels:
        n = buckets.get(key, 0)
        pct = round(n / total * 100, 1) if total else 0
        bar_w = min(pct, 100)
        rows.append(f"""
        <div class="hbar">
          <div class="label">{_esc(label)}</div>
          <div class="track"><div class="fill" style="width:{bar_w}%"></div></div>
          <div class="val"><b>{n}</b> <span class="muted">{pct}%</span></div>
        </div>""")
    bulk_html = ""
    if env.get("bulk_same_day_groups"):
        bulk_rows = "".join(
            f"<tr><td class='mono'>{_esc(g['day'])}</td>"
            f"<td class='num'>{g['url_count']}</td>"
            f"<td class='mono small'>{_esc(g['sample_urls'][0] if g['sample_urls'] else '')}</td></tr>"
            for g in env["bulk_same_day_groups"][:10]
        )
        bulk_html = f"""
        <h3>Bulk same-day update groups</h3>
        <table><thead><tr><th>Day</th><th class="num">URLs</th><th>Sample</th></tr></thead>
        <tbody>{bulk_rows}</tbody></table>"""

    return f"""
    <section id="cadence"><h2><span class="num">02</span> Content Cadence & Decay</h2>
    <p class="lede">Sitemap lastmod distribution. <b>{env['stale_share_pct']}%</b>
    of URLs are stale (&gt; {env['stale_threshold_days']} days).
    Verdict: {_verdict_badge(env['verdict'])}</p>
    <div class="card"><div class="hbars">{''.join(rows)}</div>{bulk_html}</div>
    </section>"""


def render_cannibalization(env: dict) -> str:
    if not env or env.get("cannibalized_count", 0) == 0:
        return ""
    metric_label = env.get("metric_label", "metric")
    rows = []
    for c in env.get("cannibalized", [])[:20]:
        urls_html = "<br>".join(
            f'<span class="mono small">#{_esc(u["position"])} · {_esc(u["url"])}</span>'
            for u in c["urls"][:4]
        )
        rows.append(f"""
        <tr><td><b>{_esc(c['query'])}</b></td>
        <td class="num">{c['url_count']}</td>
        <td class="num">{c['total_metric']:,}</td>
        <td>{urls_html}</td></tr>""")
    return f"""
    <section id="cannib"><h2><span class="num">03</span> Keyword Cannibalization</h2>
    <p class="lede"><b>{env['cannibalized_count']}</b> queries have multiple
    URLs competing. <b>{env.get('critical_count', 0)}</b> exceed the critical
    {metric_label} threshold.</p>
    <div class="card"><table><thead><tr><th>Query</th>
    <th class="num">URLs</th><th class="num">Total {_esc(metric_label)}</th>
    <th>Competing URLs (pos)</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table></div></section>"""


def render_intent(env: dict) -> str:
    if not env:
        return ""
    summary = env.get("summary") or {}
    if not summary:
        return ""
    rows = []
    for x in summary["by_intent"]:
        if x["intent"] == "unknown" and x["keyword_count"] == 0:
            continue
        bar = min(x["metric_share_pct"], 100)
        rows.append(f"""
        <div class="hbar">
          <div class="label">{_esc(x['intent'])}</div>
          <div class="track"><div class="fill" style="width:{bar}%"></div></div>
          <div class="val"><b>{x['keyword_count']:,}</b> kw
          <span class="muted">{x['keyword_share_pct']}% · metric {x['metric_share_pct']}%</span></div>
        </div>""")
    return f"""
    <section id="intent"><h2><span class="num">04</span> Intent Composition</h2>
    <p class="lede">Where does the keyword universe sit on the buyer-readiness
    spectrum? Each bar is the share of {_esc(summary.get('metric_column') or 'metric')}
    that intent contributes.</p>
    <div class="card"><div class="hbars">{''.join(rows)}</div></div>
    </section>"""


def render_tiers(env: dict) -> str:
    if not env:
        return ""
    summary = env.get("summary") or {}
    if not summary:
        return ""
    rows = []
    for x in summary["by_tier"]:
        if x["tier"] == "unknown" and x["url_count"] == 0:
            continue
        rows.append(f"""
        <tr><td><b>{_esc(x['tier'])}</b></td>
        <td class="num">{x['url_count']}</td>
        <td class="num">{x['url_share_pct']}%</td>
        <td class="num">{x['metric_total']:,}</td>
        <td class="num">{x['metric_share_pct']}%</td></tr>""")
    return f"""
    <section id="tiers"><h2><span class="num">05</span> Content Tier Disproportion</h2>
    <p class="lede">Business domain: <b>{_esc(summary.get('product_domain', '—'))}</b>.
    URL share vs metric share per tier — disproportion identifies pages
    pulling traffic that don't belong to the product narrative.</p>
    <div class="card"><table><thead><tr><th>Tier</th>
    <th class="num">URLs</th><th class="num">URL share</th>
    <th class="num">Metric</th><th class="num">Metric share</th></tr></thead>
    <tbody>{''.join(rows)}</tbody></table></div></section>"""


def render_eeat(env: dict) -> str:
    if not env:
        return ""
    issues = env.get("issues", [])
    if not issues:
        return ""
    rows = "".join(
        f"<li>{_badge(i['severity'])} {_esc(i['text'])}</li>"
        for i in issues
    )
    author = env.get("author") or {}
    author_html = ""
    if author.get("name"):
        author_html = f"""
        <p><b>Author:</b> {_esc(author['name'])} ·
        source: <code>{_esc(author.get('source'))}</code> ·
        profile link: {_esc(author.get('profile_link') or 'none')}</p>"""
    return f"""
    <section id="eeat"><h2><span class="num">06</span> E-E-A-T Anti-Patterns</h2>
    <p class="lede">URL: <a href="{_esc(env['target'])}">{_esc(env['target'])}</a></p>
    <div class="card">{author_html}<ul class="bullet-list">{rows}</ul></div>
    </section>"""


def render_backlinks(env: dict) -> str:
    if not env:
        return ""
    if env.get("total_unique_domains", 0) == 0:
        return ""
    dr_rows = "".join(
        f"<tr><td>{_esc(k)}</td><td class='num'>{v}</td>"
        f"<td class='num'>{round(v / env['total_unique_domains'] * 100, 1)}%</td></tr>"
        for k, v in sorted(env.get("dr_distribution", {}).items())
    )
    anchor_html = ""
    if env.get("anchor_spam_patterns"):
        anchor_rows = "".join(
            f"<tr><td>{_esc(k)}</td><td class='num'>{v}</td></tr>"
            for k, v in env["anchor_spam_patterns"].items()
        )
        anchor_html = f"""<h3>Anchor spam patterns</h3>
        <table><thead><tr><th>Pattern</th><th class="num">Domain matches</th></tr></thead>
        <tbody>{anchor_rows}</tbody></table>"""
    flagged_html = ""
    if env.get("flagged_domains_sample"):
        flagged_rows = "".join(
            f"<tr><td class='mono small'>{_esc(e['domain'])}</td>"
            f"<td class='num'>{e['authority']}</td>"
            f"<td class='num'>{e['link_count']}</td>"
            f"<td class='num'>{e['toxicity']}</td>"
            f"<td class='small'>{_esc('; '.join(e['reasons'][:3]))}</td></tr>"
            for e in env["flagged_domains_sample"][:25]
        )
        flagged_html = f"""<h3>Top flagged domains</h3>
        <table><thead><tr><th>Domain</th><th class="num">DR</th>
        <th class="num">Links</th><th class="num">Tox</th><th>Reason</th></tr></thead>
        <tbody>{flagged_rows}</tbody></table>"""
    return f"""
    <section id="backlinks"><h2><span class="num">07</span> Backlinks Profile</h2>
    <p class="lede"><b>{env['total_links_in_input']}</b> links across
    <b>{env['total_unique_domains']}</b> domains.
    {env['low_authority_share_pct']}% are DR ≤ 10. Verdict: {_verdict_badge(env['verdict'])}</p>
    <div class="card"><h3>DR distribution</h3>
    <table><thead><tr><th>Bucket</th><th class="num">Domains</th>
    <th class="num">Share</th></tr></thead><tbody>{dr_rows}</tbody></table>
    {anchor_html}{flagged_html}</div></section>"""


def render_appendix(envs: list[dict]) -> str:
    """Catch-all for envelopes that don't match a known checker."""
    known = {
        "google_updates_correlator.py",
        "sitemap_freshness.py",
        "cannibalization_detector.py",
        "intent_classifier.py",
        "content_tier_classifier.py",
        "eeat_antipatterns.py",
        "backlinks_toxicity.py",
    }
    others = [e for e in envs if e.get("checker") not in known]
    if not others:
        return ""
    rows = []
    for e in others:
        issue_count = len(e.get("issues", []))
        rows.append(f"""
        <tr><td class="mono small">{_esc(e.get('checker'))}</td>
        <td>{_esc(e.get('target'))}</td>
        <td class="num">{issue_count}</td></tr>""")
    return f"""
    <section id="appendix"><h2><span class="num">∞</span> Appendix · Other Checks</h2>
    <div class="card"><table><thead><tr><th>Checker</th><th>Target</th>
    <th class="num">Issues</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
    </section>"""


# ─────────────────────────────────────────────────────────────────────────
# TL;DR auto-extraction

def build_tldr(envs: list[dict]) -> list[str]:
    """One bullet per P0 finding; cap at 5. Skipped if there are none."""
    bullets: list[str] = []
    for env in envs:
        for issue in env.get("issues", []):
            if issue.get("severity") == "P0":
                checker = env.get("checker", "")
                src = checker.replace("_", " ").replace(".py", "")
                bullets.append(
                    f"<b>{_esc(src)}:</b> {_esc(issue['text'])}"
                )
    if not bullets:
        # If no P0, surface up to 5 P1.
        for env in envs:
            for issue in env.get("issues", []):
                if issue.get("severity") == "P1":
                    checker = env.get("checker", "")
                    src = checker.replace("_", " ").replace(".py", "")
                    bullets.append(
                        f"<b>{_esc(src)}:</b> {_esc(issue['text'])}"
                    )
    return bullets[:5]


# ─────────────────────────────────────────────────────────────────────────
# CSS — premium editorial stylebook (monochrome + tunable accent)

CSS_TEMPLATE = """
:root{{
  --ink:#0A0A0A; --ink-mid:#3a3a3a; --muted:#8a8a8a;
  --bg:#FAFAFA; --bg-2:#F1EFEA; --card:#FFFFFF;
  --line:#0000001A; --line-soft:#0000000d;
  --accent:{accent}; --accent-tint:{accent}1c; --accent-soft:{accent}0d;
  --crit:#A82626; --crit-tint:#F7DDDD;
  --ok:#3F6E4C; --ok-tint:#DFEAE0;
  --serif:'DM Serif Display',Georgia,serif;
  --sans:'Inter',-apple-system,sans-serif;
  --mono:'JetBrains Mono','SF Mono',Menlo,monospace;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}}
h1,h2,h3{{font-family:var(--serif);letter-spacing:-.012em;font-weight:400}}
h1{{font-size:52px;margin:.1em 0 .3em;line-height:1.05;letter-spacing:-.022em}}
h2{{font-size:32px;margin:0 0 .7em;display:flex;align-items:baseline;gap:18px}}
h2 .num{{font-family:var(--mono);font-size:12px;color:var(--muted);
  font-weight:600;letter-spacing:.12em;text-transform:uppercase;
  border:1px solid var(--line);padding:3px 9px;border-radius:99px;align-self:center}}
h3{{font-size:18px;margin:1.2em 0 .4em;font-weight:600;
  font-family:var(--sans);letter-spacing:0}}
p.lede{{font-size:18px;color:var(--ink-mid);max-width:820px;line-height:1.5;margin:.3em 0 1em}}
.small{{font-size:12px}}
.mono{{font-family:var(--mono)}}
a{{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--accent)}}
a:hover{{background:var(--accent-soft)}}
.conf-strip{{background:var(--accent);color:var(--ink);font-family:var(--mono);
  font-size:11px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;
  text-align:center;padding:9px 16px}}
header.top{{background:var(--card);border-bottom:1px solid var(--line);padding:36px 0}}
header.top .container{{max-width:1280px;margin:0 auto;padding:0 32px}}
.doc-meta{{font-family:var(--mono);font-size:11px;color:var(--muted);
  text-transform:uppercase;letter-spacing:.14em;margin-bottom:14px}}
.meta-row{{font-size:14px;color:var(--ink-mid);display:flex;gap:28px;
  flex-wrap:wrap;margin-top:24px;padding-top:22px;border-top:1px solid var(--line-soft)}}
.meta-row b{{color:var(--ink)}}
.tldr{{margin-top:28px;background:var(--card);border:1px solid var(--ink)}}
.tldr .head{{padding:14px 22px;border-bottom:1px solid var(--ink);background:var(--ink);
  color:var(--accent);font-family:var(--mono);font-size:13px;font-weight:700;
  letter-spacing:.18em;text-transform:uppercase}}
.tldr ul{{list-style:none;margin:0;padding:20px 24px}}
.tldr li{{display:grid;grid-template-columns:22px 1fr;gap:14px;padding:10px 0;
  font-size:17px;line-height:1.5;border-bottom:1px solid var(--line-soft)}}
.tldr li:last-child{{border-bottom:none}}
.tldr li::before{{content:"→";color:var(--accent);font-weight:700;font-size:20px;
  background:var(--ink);width:22px;height:22px;display:inline-flex;
  align-items:center;justify-content:center;margin-top:2px}}
.layout{{display:grid;grid-template-columns:240px 1fr;max-width:1280px;
  margin:0 auto;padding:0 32px;align-items:start}}
@media(max-width:1080px){{.layout{{grid-template-columns:1fr;padding:0 24px}}}}
aside.nav{{position:sticky;top:0;align-self:start;padding:32px 0;max-height:100vh;
  overflow-y:auto;font-family:var(--mono)}}
aside.nav a{{display:flex;gap:8px;padding:7px 14px;font-size:13px;font-weight:500;
  color:var(--ink-mid);text-decoration:none;border-left:2px solid transparent;
  border-bottom:none;transition:all .15s}}
aside.nav a:hover{{background:var(--accent-soft);color:var(--ink);
  border-left-color:var(--accent)}}
aside.nav a .num{{color:var(--muted);font-size:10px;min-width:18px}}
main.main{{padding:24px 0 24px 32px;min-width:0}}
@media(max-width:1080px){{main.main{{padding:24px 0}}}}
.card{{background:var(--card);border:1px solid var(--line);padding:28px;margin:14px 0}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;padding:11px 13px;border-bottom:1px solid var(--line-soft);
  vertical-align:top}}
th{{font-weight:600;color:var(--muted);text-transform:uppercase;font-size:10px;
  letter-spacing:.08em;background:var(--bg-2);font-family:var(--mono)}}
td.num,th.num{{text-align:right;font-variant-numeric:tabular-nums}}
.badge{{display:inline-block;font-family:var(--mono);font-size:10px;font-weight:600;
  padding:3px 9px;text-transform:uppercase;letter-spacing:.08em;border-radius:99px}}
.badge.crit{{background:var(--crit-tint);color:var(--crit)}}
.badge.med{{background:var(--accent-tint);color:var(--ink)}}
.badge.low{{background:var(--ok-tint);color:var(--ok)}}
.badge.neutral{{background:var(--bg-2);color:var(--ink-mid)}}
.hbars{{display:flex;flex-direction:column;gap:12px;margin-top:14px}}
.hbar{{display:grid;grid-template-columns:160px 1fr 240px;align-items:center;
  gap:16px;font-size:14px}}
.hbar .label{{color:var(--ink);font-weight:600;font-family:var(--mono);
  font-size:12px;text-transform:uppercase;letter-spacing:.06em}}
.hbar .track{{height:22px;background:var(--bg-2);overflow:hidden;border:1px solid var(--line-soft)}}
.hbar .fill{{height:100%;background:var(--ink);min-width:2px}}
.hbar .val{{font-family:var(--mono);font-size:12.5px}}
.hbar .val .muted{{color:var(--muted);margin-left:6px}}
.bullet-list{{list-style:none;padding:0;margin:0}}
.bullet-list li{{padding:10px 0;border-bottom:1px solid var(--line-soft);
  font-size:15px;display:flex;gap:10px;align-items:baseline}}
.bullet-list li:last-child{{border-bottom:none}}
code{{font-family:var(--mono);font-size:13px;background:var(--bg-2);
  padding:1px 5px;border-radius:3px}}
footer{{font-family:var(--mono);font-size:11px;color:var(--muted);
  text-transform:uppercase;letter-spacing:.12em;text-align:center;
  padding:32px;border-top:1px solid var(--line);margin-top:64px}}
"""


# ─────────────────────────────────────────────────────────────────────────
# Main

def render_report(
    envs: list[dict],
    target: str,
    client: str,
    prepared_by: str,
    accent: str,
) -> str:
    by_checker: dict[str, dict] = {}
    for e in envs:
        by_checker[e.get("checker", "")] = e

    tldr = build_tldr(envs)
    sections = [
        render_google_updates(by_checker.get("google_updates_correlator.py")),
        render_sitemap_freshness(by_checker.get("sitemap_freshness.py")),
        render_cannibalization(by_checker.get("cannibalization_detector.py")),
        render_intent(by_checker.get("intent_classifier.py")),
        render_tiers(by_checker.get("content_tier_classifier.py")),
        render_eeat(by_checker.get("eeat_antipatterns.py")),
        render_backlinks(by_checker.get("backlinks_toxicity.py")),
        render_appendix(envs),
    ]
    sections = [s for s in sections if s.strip()]
    section_titles = [
        ("updates", "01", "Algorithmic Timeline"),
        ("cadence", "02", "Cadence & Decay"),
        ("cannib", "03", "Cannibalization"),
        ("intent", "04", "Intent"),
        ("tiers", "05", "Tiers"),
        ("eeat", "06", "E-E-A-T"),
        ("backlinks", "07", "Backlinks"),
        ("appendix", "∞", "Appendix"),
    ]
    # Filter nav to only sections we rendered
    rendered_ids = {f'id="{sid}"' for sid in ("updates","cadence","cannib","intent","tiers","eeat","backlinks","appendix")}
    nav_html = "\n".join(
        f'<a href="#{sid}"><span class="num">{num}</span> {label}</a>'
        for sid, num, label in section_titles
        if any(f'id="{sid}"' in s for s in sections)
    )

    tldr_html = ""
    if tldr:
        items = "".join(f"<li><span>{b}</span></li>" for b in tldr)
        tldr_html = f"""
        <div class="tldr">
          <div class="head">TL;DR — top issues</div>
          <ul>{items}</ul>
        </div>"""

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(target)} — SEO audit</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<style>{CSS_TEMPLATE.format(accent=accent)}</style>
</head>
<body>
<div class="conf-strip"><b>CONFIDENTIAL</b> · Prepared for {_esc(client)} · Not for redistribution</div>
<header class="top"><div class="container">
  <div class="doc-meta">Amazing SEO Skill · v{SKILL_VERSION} · {generated}</div>
  <h1>{_esc(target)} — SEO audit</h1>
  <p class="lede">Algorithmic, content, technical and backlinks diagnosis.
  Verified against the Google updates calendar shipped with the skill.</p>
  <div class="meta-row">
    <span>Prepared by <b>{_esc(prepared_by)}</b></span>
    <span>Client <b>{_esc(client)}</b></span>
    <span>Sources <b>GSC / Ahrefs / Crawl / LLM-ensemble</b></span>
  </div>
  {tldr_html}
</div></header>
<div class="layout">
  <aside class="nav">{nav_html}</aside>
  <main class="main">{''.join(sections)}</main>
</div>
<footer>Generated by amazing-seo-skill v{SKILL_VERSION} · github.com/metawhisp/amazing-seo-skill</footer>
</body></html>"""


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("envelopes", nargs="+", type=Path,
                   help="JSON envelope files from any v0.8.0 checker")
    p.add_argument("--target", required=True, help="Site label for the report")
    p.add_argument("--client", default="Internal")
    p.add_argument("--prepared-by", default="amazing-seo-skill")
    p.add_argument("--accent", default="#00d4aa",
                   help="Hex accent colour (default mint #00d4aa)")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    envs = []
    for f in args.envelopes:
        try:
            envs.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception as e:
            print(f"WARNING: could not load {f}: {e}", file=sys.stderr)

    if not envs:
        print("ERROR: no usable envelopes loaded", file=sys.stderr)
        return 2

    html_out = render_report(
        envs,
        target=args.target,
        client=args.client,
        prepared_by=args.prepared_by,
        accent=args.accent,
    )
    args.output.write_text(html_out, encoding="utf-8")
    print(f"Wrote report → {args.output} ({len(html_out):,} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
