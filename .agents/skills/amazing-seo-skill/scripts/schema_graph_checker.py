#!/usr/bin/env python3
"""
Cross-page Schema.org entity-graph consistency checker.

Why it matters (verified Aug 2026 on a live production audit):
  - Per-page validators (schema_recommended_fields.py) score field presence
    inside one block on one page and can report 100/100 while the site-wide
    entity graph contradicts itself. Knowledge-graph consolidation and AI
    extraction read the graph, not one page.
  - Real failures this catches that per-page checks structurally cannot:
      * one @id carrying a different `description`/`name` on every page
        (page meta injected into a site-wide entity)
      * `publisher`/`author` declared as an inline anonymous entity that
        duplicates an @id-entity of the same type with a different name/url
        (two Organizations = two identities for the knowledge graph)
      * article listing (Blog.blogPost[]) disagreeing with the article page
        itself about the author (Organization vs Person)
      * schema `softwareVersion` diverging from the version visible in text
      * pages with a visible FAQ block (>=3 <details>) but no FAQPage markup

Exit code: 0 = consistent, 1 = fetch/parse failed for all pages, 2 = conflicts found.

Usage:
  schema_graph_checker.py <seed_url> [--pages 8]
  schema_graph_checker.py <seed_url> --urls URL1 URL2 ...
  schema_graph_checker.py <seed_url> --sitemap https://site/sitemap.xml
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from _fetch import fetch, result_envelope, finding

_TRACKED_FIELDS = ["name", "description", "url", "softwareVersion", "datePublished"]
_VERSION_RE = re.compile(r"\bv?(\d+\.\d+\.\d+)\b")


def _discover_sitemap_urls(seed: str, sitemap_url: str | None) -> list[str]:
    origin = f"{urlparse(seed).scheme}://{urlparse(seed).netloc}"
    candidates = [sitemap_url] if sitemap_url else [
        f"{origin}/sitemap-index.xml", f"{origin}/sitemap.xml", f"{origin}/sitemap_index.xml",
    ]
    for cand in candidates:
        if not cand:
            continue
        try:
            r = fetch(cand, timeout=15)
        except requests.RequestException:
            continue
        if r.status_code != 200 or "<" not in r.text[:200]:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text)
        if not locs:
            continue
        # sitemap index → recurse one level
        if "<sitemapindex" in r.text[:500]:
            urls: list[str] = []
            for child in locs[:5]:
                try:
                    cr = fetch(child, timeout=15)
                    urls += re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", cr.text)
                except requests.RequestException:
                    continue
            if urls:
                return urls
        else:
            return locs
    return []


def _sample(seed: str, urls: list[str], n: int) -> list[str]:
    """Seed + a cross-section spread over first path segments."""
    picked = [seed]
    by_section: dict[str, list[str]] = defaultdict(list)
    for u in urls:
        if u.rstrip("/") == seed.rstrip("/"):
            continue
        seg = (urlparse(u).path.strip("/").split("/") or [""])[0]
        by_section[seg].append(u)
    sections = list(by_section.values())
    i = 0
    while len(picked) < n and any(sections):
        bucket = sections[i % len(sections)]
        if bucket:
            picked.append(bucket.pop(0))
        i += 1
        if i > 10 * n:
            break
    return picked


def _extract_entities(html: str) -> tuple[list[dict], int]:
    """All JSON-LD entities on a page, @graph flattened. Returns (entities, parse_failures)."""
    entities: list[dict] = []
    failures = 0
    for m in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                        html, re.DOTALL | re.IGNORECASE):
        try:
            data = json.loads(m.strip())
        except json.JSONDecodeError:
            failures += 1
            continue
        stack = data if isinstance(data, list) else [data]
        for item in stack:
            if not isinstance(item, dict):
                continue
            if "@graph" in item and isinstance(item["@graph"], list):
                entities += [g for g in item["@graph"] if isinstance(g, dict)]
            else:
                entities.append(item)
    return entities, failures


def _visible_text(html: str) -> str:
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
    for el in soup(["script", "style", "noscript"]):
        el.decompose()
    return soup.get_text(" ", strip=True)


def _norm_url(u: str | None) -> str:
    if not u:
        return ""
    p = urlparse(u)
    return f"{p.netloc}{p.path}".rstrip("/").lower()


def _entity_name(x) -> tuple[str | None, str | None]:
    """(type, name) of an author/publisher value that may be dict/list/str."""
    if isinstance(x, list):
        x = x[0] if x else None
    if isinstance(x, dict):
        return x.get("@type"), x.get("name")
    if isinstance(x, str):
        return None, x
    return None, None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("seed")
    ap.add_argument("--pages", type=int, default=8)
    ap.add_argument("--urls", nargs="*", default=None)
    ap.add_argument("--sitemap", default=None)
    args = ap.parse_args()

    seed = args.seed
    if not seed.startswith(("http://", "https://")):
        seed = "https://" + seed

    if args.urls:
        pages = [seed] + [u for u in args.urls if u.rstrip("/") != seed.rstrip("/")]
    else:
        all_urls = _discover_sitemap_urls(seed, args.sitemap)
        pages = _sample(seed, all_urls, args.pages) if all_urls else [seed]

    # per-@id: field -> {value -> [pages]}
    id_fields: dict[str, dict[str, dict[str, list[str]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list)))
    id_types: dict[str, str] = {}
    named_by_type: dict[str, dict[str, dict]] = defaultdict(dict)   # type -> name -> {id, url, page}
    inline_refs: list[dict] = []            # anonymous author/publisher objects
    listing_authors: dict[str, dict] = {}   # article url -> {type, name, page}
    page_authors: dict[str, dict] = {}
    software_versions: dict[str, list[str]] = defaultdict(list)     # version -> pages
    visible_versions: set[str] = set()
    faq_pages_wo_markup: list[dict] = []
    fetched, failed = [], []

    for page_url in pages:
        try:
            r = fetch(page_url, timeout=20)
        except requests.RequestException as e:
            failed.append({"url": page_url, "error": str(e)[:120]})
            continue
        if r.status_code != 200:
            failed.append({"url": page_url, "error": f"HTTP {r.status_code}"})
            continue
        fetched.append(page_url)
        entities, parse_failures = _extract_entities(r.text)

        for ent in entities:
            etype = ent.get("@type")
            eid = ent.get("@id")
            if eid:
                id_types[eid] = str(etype)
                for f in _TRACKED_FIELDS:
                    v = ent.get(f)
                    if isinstance(v, str) and v.strip():
                        id_fields[eid][f][v.strip()].append(page_url)
            if isinstance(etype, str) and ent.get("name") and (eid or ent.get("url")):
                named_by_type[etype].setdefault(
                    ent["name"], {"id": eid, "url": ent.get("url"), "page": page_url})
            if etype == "SoftwareApplication" and ent.get("softwareVersion"):
                software_versions[str(ent["softwareVersion"])].append(page_url)
            # inline author/publisher (no @id link)
            for field in ("author", "publisher"):
                v = ent.get(field)
                vals = v if isinstance(v, list) else [v]
                for val in vals:
                    if isinstance(val, dict) and not val.get("@id") and val.get("name"):
                        inline_refs.append({"field": field, "type": val.get("@type"),
                                            "name": val["name"], "url": val.get("url"),
                                            "page": page_url, "parent_type": str(etype)})
            # article-listing vs article-page author
            if etype == "Blog" and isinstance(ent.get("blogPost"), list):
                for post in ent["blogPost"]:
                    if isinstance(post, dict):
                        key = _norm_url(post.get("url") or post.get("@id"))
                        t, n = _entity_name(post.get("author"))
                        if key and n:
                            listing_authors[key] = {"type": t, "name": n, "page": page_url}
            if etype in ("BlogPosting", "Article", "NewsArticle", "TechArticle"):
                key = _norm_url(ent.get("mainEntityOfPage") or ent.get("url") or page_url)
                t, n = _entity_name(ent.get("author"))
                if key and n:
                    page_authors[key] = {"type": t, "name": n, "page": page_url}

        text = _visible_text(r.text)
        visible_versions |= set(_VERSION_RE.findall(text))
        # visible FAQ block without FAQPage markup
        details_count = len(re.findall(r"<details[\s>]", r.text, re.IGNORECASE))
        has_faq_heading = bool(re.search(
            r"<h[23][^>]*>[^<]*(?:faq|frequently asked)", r.text, re.IGNORECASE))
        has_faqpage = any(e.get("@type") == "FAQPage" for e in entities)
        if details_count >= 3 and has_faq_heading and not has_faqpage:
            faq_pages_wo_markup.append({"url": page_url, "details_blocks": details_count})

    if not fetched:
        print(json.dumps({"target": seed, "error": "no page could be fetched",
                          "failed": failed}, indent=2))
        return 1

    issues = []

    # 1. same @id, conflicting literal values across pages
    id_conflicts = []
    for eid, fields in id_fields.items():
        for f, values in fields.items():
            if len(values) > 1:
                id_conflicts.append({
                    "id": eid, "type": id_types.get(eid), "field": f,
                    "distinct_values": len(values),
                    "values": {v[:90]: pages_[:3] for v, pages_ in values.items()},
                })
    for c in id_conflicts:
        issues.append(finding(
            "P2",
            f"entity {c['id']} ({c['type']}) has {c['distinct_values']} different "
            f"'{c['field']}' values across pages — one entity must carry one value",
            evidence=c))

    # 2. inline author/publisher duplicating an @id-entity of the same type
    dup_reported = set()
    for ref in inline_refs:
        rtype = ref.get("type")
        if not rtype or rtype not in named_by_type:
            continue
        graph_names = {n: meta for n, meta in named_by_type[rtype].items()
                       if meta.get("id")}
        if not graph_names or ref["name"] in graph_names:
            continue
        key = (ref["field"], rtype, ref["name"])
        if key in dup_reported:
            continue
        dup_reported.add(key)
        other = next(iter(graph_names.items()))
        issues.append(finding(
            "P2",
            f"inline {ref['field']} {rtype} \"{ref['name']}\" is not linked by @id and "
            f"differs from the site's @id-declared {rtype} \"{other[0]}\" — "
            "two identities for the knowledge graph; use \"" + ref['field'] +
            "\": {\"@id\": \"" + str(other[1].get('id')) + "\"}",
            evidence={"inline": ref, "graph_entity": {"name": other[0], **other[1]}}))

    # 3. listing vs page author mismatch
    for key, listed in listing_authors.items():
        actual = page_authors.get(key)
        if actual and (listed["name"] != actual["name"] or
                       (listed["type"] and actual["type"] and listed["type"] != actual["type"])):
            issues.append(finding(
                "P2",
                f"author mismatch for article /{key.split('/', 1)[-1]}: listing says "
                f"{listed['type'] or '?'} \"{listed['name']}\" but the article page says "
                f"{actual['type'] or '?'} \"{actual['name']}\"",
                evidence={"listing": listed, "article_page": actual}))

    # 4. schema softwareVersion vs visible version text
    for sv, pages_ in software_versions.items():
        clean = sv.lstrip("v")
        if visible_versions and clean not in visible_versions:
            issues.append(finding(
                "P2",
                f"schema softwareVersion \"{sv}\" never appears in visible text; visible "
                f"version strings on sampled pages: {sorted(visible_versions)[:5]} — "
                "stale schema, source the version from the release at build time",
                evidence={"schema_version": sv, "visible_versions": sorted(visible_versions)[:10],
                          "pages_with_schema_version": pages_[:3]}))
            break

    # 5. visible FAQ without FAQPage markup
    if faq_pages_wo_markup:
        issues.append(finding(
            "P2",
            f"{len(faq_pages_wo_markup)} page(s) render a visible FAQ block (>=3 <details>) "
            "without FAQPage markup — no Google rich result outside gov/health, but "
            "AI-extraction parity is lost vs pages that have it",
            evidence={"pages": faq_pages_wo_markup[:10]}))

    out = result_envelope(
        seed, None, "schema_graph_checker.py",
        pages_checked=fetched,
        pages_failed=failed,
        entities_with_id=len(id_fields),
        id_field_conflicts=len(id_conflicts),
        inline_identity_duplicates=len(dup_reported),
        author_listing_mismatches=sum(
            1 for i in issues if "author mismatch" in i["text"]),
        issues=issues,
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 2 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
