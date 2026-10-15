#!/usr/bin/env python3
"""
RSS/Atom feed presence + declaration checker.

Why it matters (verified Aug 2026 on a live production audit):
  - A blog with no feed loses a distribution channel that costs nothing:
    feed readers, aggregators, and — increasingly — AI content pipelines
    that watch feeds for fresh sources to cite.
  - A feed that exists but is not declared via <link rel="alternate"> is
    invisible to autodiscovery.

Checks:
  - probes common feed paths (/rss.xml, /feed.xml, /atom.xml, /feed,
    /index.xml, /blog/rss.xml, /blog/feed.xml)
  - parses homepage and blog index for <link rel="alternate"
    type="application/rss+xml|atom+xml">
  - validates any found feed: XML well-formed, item count, newest item date
  - detects whether the site has a blog-like section at all
    (/blog/, /news/, /posts/, /articles/) — no blog, no finding

Exit code: 0 = feed present+declared (or no blog), 1 = fetch failed,
           2 = blog exists but feed missing/undeclared/stale.

Usage:
  feed_checker.py <domain_or_url>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from _fetch import fetch, result_envelope, finding

_FEED_PATHS = ["/rss.xml", "/feed.xml", "/atom.xml", "/feed", "/feed/",
               "/index.xml", "/blog/rss.xml", "/blog/feed.xml", "/blog/atom.xml"]
_BLOG_PATHS = ["/blog/", "/news/", "/posts/", "/articles/"]
_FEED_TYPES = ("application/rss+xml", "application/atom+xml", "application/feed+json")


def _probe(url: str) -> tuple[int | None, str | None]:
    try:
        r = fetch(url, timeout=12)
        return r.status_code, r.text if r.status_code == 200 else None
    except requests.RequestException:
        return None, None


def _declared_feeds(html: str, base_url: str) -> list[dict]:
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
    out = []
    for link in soup.find_all("link", href=True):
        rels = {r.lower() for r in (link.get("rel") or [])}
        ltype = (link.get("type") or "").lower()
        if "alternate" in rels and ltype in _FEED_TYPES:
            out.append({"href": urljoin(base_url, link["href"]), "type": ltype})
    return out


def _validate_feed(body: str) -> dict:
    info: dict = {"well_formed": False, "kind": None, "item_count": 0,
                  "newest_item": None, "age_days": None}
    try:
        root = ET.fromstring(body.strip())
    except ET.ParseError as e:
        info["parse_error"] = str(e)[:120]
        return info
    info["well_formed"] = True
    tag = root.tag.lower()
    dates: list[datetime] = []
    if tag.endswith("rss"):
        info["kind"] = "rss"
        items = root.findall(".//item")
        info["item_count"] = len(items)
        for it in items:
            d = it.findtext("pubDate")
            if d:
                try:
                    dates.append(parsedate_to_datetime(d))
                except (TypeError, ValueError):
                    pass
    elif tag.endswith("feed"):
        info["kind"] = "atom"
        ns = {"a": "http://www.w3.org/2005/Atom"}
        entries = root.findall("a:entry", ns) or root.findall("entry")
        info["item_count"] = len(entries)
        for e in entries:
            d = e.findtext("a:updated", namespaces=ns) or e.findtext("updated")
            if d:
                try:
                    dates.append(datetime.fromisoformat(d.replace("Z", "+00:00")))
                except ValueError:
                    pass
    if dates:
        newest = max(dates)
        if newest.tzinfo is None:
            newest = newest.replace(tzinfo=timezone.utc)
        info["newest_item"] = newest.isoformat()
        info["age_days"] = (datetime.now(timezone.utc) - newest).days
    return info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("url")
    ap.add_argument("--stale-days", type=int, default=90)
    args = ap.parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    try:
        home = fetch(origin + "/", timeout=15)
    except requests.RequestException as e:
        print(json.dumps({"target": origin, "error": str(e)[:200]}, indent=2))
        return 1

    # blog-like section?
    blog_section = None
    for path in _BLOG_PATHS:
        status, _ = _probe(origin + path)
        if status == 200:
            blog_section = path
            break

    # declared feeds on homepage + blog index
    declared = _declared_feeds(home.text, home.url)
    if blog_section:
        _, blog_html = _probe(origin + blog_section)
        if blog_html:
            for f in _declared_feeds(blog_html, origin + blog_section):
                if f not in declared:
                    declared.append(f)

    # probe conventional paths + declared hrefs
    found: list[dict] = []
    tried = []
    for candidate in [d["href"] for d in declared] + [origin + p for p in _FEED_PATHS]:
        if candidate in tried:
            continue
        tried.append(candidate)
        status, body = _probe(candidate)
        if status == 200 and body and ("<rss" in body[:2000] or "<feed" in body[:2000]):
            found.append({"url": candidate, **_validate_feed(body)})

    issues = []
    if blog_section and not found:
        issues.append(finding(
            "P2",
            f"blog section {blog_section} exists but no RSS/Atom feed found "
            f"({len(tried)} paths probed, 0 <link rel=\"alternate\"> declarations) — "
            "feed readers, aggregators and AI content pipelines can't subscribe",
            evidence={"probed": tried[:12], "declared": declared}))
    if found and not declared:
        issues.append(finding(
            "P2",
            f"feed exists ({found[0]['url']}) but is not declared via "
            "<link rel=\"alternate\"> — autodiscovery is broken",
            evidence={"feeds": [f["url"] for f in found]}))
    for f in found:
        if not f["well_formed"]:
            issues.append(finding("P1", f"feed {f['url']} is not well-formed XML",
                                  evidence=f))
        elif f["age_days"] is not None and f["age_days"] > args.stale_days and blog_section:
            issues.append(finding(
                "P2",
                f"feed {f['url']} newest item is {f['age_days']} days old "
                f"(threshold {args.stale_days}d) — stale feed reads as an abandoned site",
                evidence=f))

    out = result_envelope(
        origin, home, "feed_checker.py",
        blog_section=blog_section,
        feeds_found=found,
        feeds_declared=declared,
        paths_probed=len(tried),
        issues=issues,
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 2 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
