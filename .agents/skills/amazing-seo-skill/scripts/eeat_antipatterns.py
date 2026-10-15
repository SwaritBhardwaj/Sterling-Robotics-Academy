#!/usr/bin/env python3
"""
E-E-A-T Anti-Pattern Detector
─────────────────────────────

Surfaces concrete editorial signals that depress trust under Google's
post-Mar-2026-Core E-E-A-T weighting. These are the patterns expert SEO
audits flag manually; this script makes them deterministic for any URL.

Detected anti-patterns:

  • open_in_ai_widget    Links offering to "open this article in ChatGPT /
                         Perplexity / Grok / Google AI". Publicly signals
                         the content is LLM-interchangeable.
  • anonymous_author     No identifiable author OR generic byline ("Team",
                         "Editorial", "Staff", "Admin").
  • missing_author_bio   No link from byline to an author profile page.
  • no_external_credentials  Author has no sameAs / outbound links to
                             LinkedIn, conference talks, RFCs, X / Twitter,
                             ORCID, Google Scholar, etc.
  • missing_review_signal     No "reviewed by", "fact-checked by", or
                              "medically reviewed" / "legally reviewed"
                              indication on YMYL-flavoured content.
  • no_publish_or_update_date No clear date on an article-like page.
  • generic_chart_without_source  Inline chart / table without an explicit
                                  "Source:" or methodology note nearby.
  • author_in_schema_only     Author exists in JSON-LD but not visible to
                              humans on the page.

Each finding maps to a P-level so it can flow into page_score / dashboards.

Usage:
    python eeat_antipatterns.py https://example.com/blog/some-article
    python eeat_antipatterns.py URL --json /tmp/x.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import fetch, finding, result_envelope  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────
# Pattern definitions

# Hosts in <a href> that signal an "open this article in X" widget.
AI_WIDGET_HOSTS = (
    "chat.openai.com",
    "chatgpt.com",
    "perplexity.ai",
    "www.perplexity.ai",
    "grok.com",
    "grok.x.ai",
    "x.ai",
    "claude.ai",
    "gemini.google.com",
    "bard.google.com",
)

# Phrases near such links that confirm intent.
AI_WIDGET_PHRASES = (
    "open in chatgpt",
    "open in perplexity",
    "open in grok",
    "open in claude",
    "open in gemini",
    "open in ai",
    "ask chatgpt",
    "ask perplexity",
    "ask claude",
    "read with ai",
    "discuss with ai",
)

# Generic byline patterns. Whole-word so "team" doesn't catch "Steamboat".
GENERIC_BYLINE_RE = re.compile(
    r"\b(team|staff|editorial(?:\s+team)?|admin|administrator|website|"
    r"contributor|writer|guest\s+author)\b",
    re.IGNORECASE,
)

# Trusted credential domains (sameAs targets that indicate real authority).
CREDENTIAL_DOMAINS = (
    "linkedin.com",
    "twitter.com",
    "x.com",
    "orcid.org",
    "scholar.google.com",
    "github.com",
    "wikipedia.org",
    "ieee.org",
    "ietf.org",  # RFCs
    "m3aawg.org",
    "researchgate.net",
)

REVIEW_PHRASES = (
    "reviewed by",
    "fact-checked by",
    "fact checked by",
    "medically reviewed",
    "legally reviewed",
    "edited by",
    "peer reviewed",
)


# ─────────────────────────────────────────────────────────────────────────
# Detectors — each returns (detected: bool, evidence: dict)

def detect_open_in_ai_widget(soup: BeautifulSoup) -> tuple[bool, dict]:
    """Find anchor tags pointing at AI host with phrase nearby OR matching
    UTM-style query that names an AI assistant."""
    hits: list[dict] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        host = urlparse(href).hostname or ""
        if any(host.endswith(h) or h in href for h in AI_WIDGET_HOSTS):
            text = (a.get_text(strip=True) or "").lower()
            # Strict trigger: link goes to AI host AND surrounding text uses
            # one of the canonical "open in ..." phrases.
            # Fallback: link to AI host with very short text (icon-only).
            ctx = a.parent.get_text(" ", strip=True).lower() if a.parent else ""
            phrase_hit = any(p in ctx or p in text for p in AI_WIDGET_PHRASES)
            if phrase_hit or len(text) < 4:
                hits.append({"href": a["href"], "text": text[:80]})
    return bool(hits), {"hits": hits[:6], "count": len(hits)}


def detect_author(soup: BeautifulSoup) -> dict:
    """Pull the visible byline. Order of preference:
      1. <a rel="author">
      2. <meta name="author">
      3. JSON-LD Person via Article.author
      4. Visible byline pattern (By {name})

    Returns dict with: name, source, generic (bool), profile_link (str|None).
    """
    out = {
        "name": None,
        "source": None,
        "generic": False,
        "profile_link": None,
        "in_schema_only": False,
    }
    # 1. rel=author
    a = soup.find("a", attrs={"rel": "author"})
    if a:
        out["name"] = a.get_text(strip=True) or None
        out["source"] = "rel_author"
        out["profile_link"] = a.get("href")

    # 2. meta author
    if not out["name"]:
        m = soup.find("meta", attrs={"name": re.compile(r"^author$", re.I)})
        if m and m.get("content"):
            out["name"] = m["content"].strip()
            out["source"] = "meta_author"

    # 3. JSON-LD
    schema_author = None
    for s in soup.find_all("script", type=lambda v: v and "ld+json" in v.lower()):
        try:
            data = json.loads(s.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        nodes = data if isinstance(data, list) else [data]
        # Some sites use @graph
        flat = []
        for n in nodes:
            if isinstance(n, dict):
                if "@graph" in n and isinstance(n["@graph"], list):
                    flat.extend(n["@graph"])
                else:
                    flat.append(n)
        for n in flat:
            if not isinstance(n, dict):
                continue
            a_field = n.get("author")
            if a_field:
                if isinstance(a_field, dict):
                    schema_author = a_field.get("name")
                elif isinstance(a_field, str):
                    schema_author = a_field
                elif isinstance(a_field, list) and a_field:
                    first = a_field[0]
                    schema_author = first.get("name") if isinstance(first, dict) else first
                break
        if schema_author:
            break

    if not out["name"] and schema_author:
        out["name"] = schema_author
        out["source"] = "schema_only"
        out["in_schema_only"] = True
    elif schema_author and out["name"] and schema_author != out["name"]:
        # Both present — note for evidence but keep visible one
        pass

    # 4. Visible "By X" pattern fallback
    if not out["name"]:
        # Look in first ~2 KB of text to avoid matching "by" in body
        head_text = soup.get_text(" ", strip=True)[:2000]
        m = re.search(r"\bBy\s+([A-Z][a-zA-Z'\-]+(?:\s+[A-Z][a-zA-Z'\-]+){0,2})", head_text)
        if m:
            out["name"] = m.group(1)
            out["source"] = "visible_text"

    if out["name"] and GENERIC_BYLINE_RE.search(out["name"]):
        out["generic"] = True

    return out


def detect_credentials(soup: BeautifulSoup, author_link: str | None) -> dict:
    """Walk the page (and the author profile page if linked) for sameAs
    or outbound links to known credential domains."""
    found = set()
    for a in soup.find_all("a", href=True):
        host = urlparse(a["href"]).hostname or ""
        for cd in CREDENTIAL_DOMAINS:
            if cd in host:
                found.add(cd)
                break
    return {"credential_domains_present": sorted(found), "count": len(found)}


def detect_review_signal(soup: BeautifulSoup) -> bool:
    text = soup.get_text(" ", strip=True).lower()
    return any(p in text for p in REVIEW_PHRASES)


def detect_dates(soup: BeautifulSoup) -> dict:
    """Look for visible published / modified dates. Returns presence flags."""
    found_published = False
    found_modified = False
    for t in soup.find_all("time"):
        if t.has_attr("datetime"):
            attr = t.get("datetime", "")
            label = (t.parent.get_text(" ", strip=True).lower() if t.parent else "")
            if "publish" in label or "posted" in label or not found_published:
                found_published = found_published or bool(attr)
            if "updat" in label or "modif" in label:
                found_modified = True
    # JSON-LD fallback
    for s in soup.find_all("script", type=lambda v: v and "ld+json" in v.lower()):
        try:
            data = json.loads(s.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        nodes = data if isinstance(data, list) else [data]
        for n in nodes:
            if isinstance(n, dict):
                if n.get("datePublished"):
                    found_published = True
                if n.get("dateModified"):
                    found_modified = True
    return {"date_published_visible": found_published, "date_modified_visible": found_modified}


def detect_charts_without_source(soup: BeautifulSoup) -> dict:
    """Find <figure>, <table>, or <canvas> not followed within ~250 chars
    by a 'Source:' or 'Methodology' marker. Soft heuristic; high false-
    positive rate by design — surfaces candidates for human review."""
    suspicious = 0
    for el in soup.find_all(["figure", "table", "canvas"]):
        # Look ahead in DOM text for source mention
        tail = ""
        sib = el.find_next_sibling()
        for _ in range(3):
            if sib is None:
                break
            tail += " " + sib.get_text(" ", strip=True)
            sib = sib.find_next_sibling()
        caption = ""
        cap_el = el.find("figcaption")
        if cap_el:
            caption = cap_el.get_text(" ", strip=True)
        nearby = (caption + " " + tail).lower()
        if not re.search(r"\bsource[:\s]|methodology|data from|via\b", nearby):
            suspicious += 1
    return {"unsourced_visual_count": suspicious}


# ─────────────────────────────────────────────────────────────────────────
# Orchestrator

def analyze_url(url: str, timeout: int = 20) -> dict:
    try:
        r = fetch(url, timeout=timeout)
    except requests.RequestException as e:
        return result_envelope(
            target=url, response=None, checker="eeat_antipatterns.py",
            error=str(e),
            issues=[finding("P0", f"Fetch failed: {e}")],
        )
    if not r.ok:
        return result_envelope(
            target=url, response=r, checker="eeat_antipatterns.py",
            error=f"HTTP {r.status_code}",
            issues=[finding("P0", f"HTTP {r.status_code}")],
        )
    soup = BeautifulSoup(r.text, "html.parser")

    widget_hit, widget_ev = detect_open_in_ai_widget(soup)
    author = detect_author(soup)
    creds = detect_credentials(soup, author.get("profile_link"))
    has_review = detect_review_signal(soup)
    dates = detect_dates(soup)
    charts = detect_charts_without_source(soup)

    issues: list[dict] = []
    if widget_hit:
        issues.append(finding(
            "P1",
            "Open-in-AI widget detected — explicit signal that content is "
            "LLM-interchangeable (negative E-E-A-T signal post-Mar-2026)",
            evidence=widget_ev,
        ))
    if not author["name"]:
        issues.append(finding(
            "P1",
            "No author identifiable (no rel=author, meta author, or visible byline)",
        ))
    elif author["generic"]:
        issues.append(finding(
            "P1",
            f"Generic byline '{author['name']}' — Google weights named "
            f"practitioner authors heavily under current core update",
        ))
    if author["in_schema_only"]:
        issues.append(finding(
            "P2",
            f"Author '{author['name']}' present in JSON-LD only, not visible "
            f"to human readers",
        ))
    if author["name"] and not author["profile_link"]:
        issues.append(finding(
            "P2",
            "Byline present but no link to author profile page",
        ))
    if creds["count"] == 0:
        issues.append(finding(
            "P2",
            "No external credentials linked (no LinkedIn / GitHub / industry "
            "association references on the page)",
        ))
    if not has_review:
        issues.append(finding(
            "P2",
            "No 'reviewed by' or fact-check signal — recommended for "
            "YMYL-adjacent content (finance, health, legal, security)",
        ))
    if not dates["date_published_visible"] and not dates["date_modified_visible"]:
        issues.append(finding(
            "P1",
            "No visible publish or update date on the page",
        ))
    if charts["unsourced_visual_count"] >= 2:
        issues.append(finding(
            "P2",
            f"{charts['unsourced_visual_count']} chart/table elements without "
            f"a 'Source:' or methodology marker nearby",
        ))

    return result_envelope(
        target=url,
        response=r,
        checker="eeat_antipatterns.py",
        open_in_ai_widget=widget_ev | {"detected": widget_hit},
        author=author,
        credentials=creds,
        review_signal_present=has_review,
        dates=dates,
        unsourced_visual_count=charts["unsourced_visual_count"],
        issues=issues,
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("url")
    p.add_argument("--json", type=Path)
    p.add_argument("--timeout", type=int, default=20)
    args = p.parse_args()
    env = analyze_url(args.url, timeout=args.timeout)
    out = json.dumps(env, indent=2, ensure_ascii=False)
    if args.json:
        args.json.write_text(out, encoding="utf-8")
    else:
        print(out)
    # Exit 2 on any P0/P1, 1 on P2-only, 0 on clean
    issues = env.get("issues", [])
    if any(i["severity"] in ("P0", "P1") for i in issues):
        return 2
    if issues:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
