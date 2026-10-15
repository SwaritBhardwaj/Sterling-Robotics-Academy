#!/usr/bin/env python3
"""
Static-asset cache-policy checker.

Why it matters (verified Aug 2026 on a live production audit):
  - Page-level checkers only inspect the HTML document's headers. Nobody
    fetches the site's actual JS/CSS/font/image assets — where caching is
    usually misconfigured. Real case: content-hashed /_astro/*.js served
    with `max-age=14400, immutable, must-revalidate` — a contradictory
    combo and a 4-hour TTL on files whose name changes when content does.
  - Correct policy: content-hashed assets → `max-age=31536000, immutable`;
    HTML documents → short/no cache with revalidation.

Checks per asset (same-origin by default, up to --max-assets):
  - cache-control present at all
  - hashed-filename assets with max-age < 30 days (wasted revalidation)
  - contradictory directives (immutable+must-revalidate, no-store+max-age,
    no-cache+immutable)
  - HTML document itself cached > 1 hour (stale-content risk)

Exit code: 0 = sane policy, 1 = page fetch failed, 2 = issues found.

Usage:
  asset_cache_checker.py <page_url> [--max-assets 20] [--include-third-party]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from _fetch import fetch, result_envelope, finding, _BASE_HEADERS, _DEFAULT_UA

_HASH_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{8,}$")
_THIRTY_DAYS = 30 * 86400


def _looks_hashed(path: str) -> bool:
    """page.DM6fxY_l.js / logo.Bxun-jk4_Zr0NJA.svg / app.8f3ab12c.css → True."""
    name = path.rsplit("/", 1)[-1]
    parts = re.split(r"[._-]", name)
    for token in parts[:-1]:  # skip the extension
        if (_HASH_TOKEN_RE.match(token)
                and any(c.isdigit() for c in token)
                and any(c.isalpha() for c in token)
                and not token.isdigit()):
            return True
    return False


def _parse_cache_control(value: str | None) -> dict:
    out: dict = {"raw": value, "directives": {}, "max_age": None}
    if not value:
        return out
    for part in value.split(","):
        part = part.strip().lower()
        if "=" in part:
            k, _, v = part.partition("=")
            out["directives"][k.strip()] = v.strip()
        elif part:
            out["directives"][part] = True
    ma = out["directives"].get("max-age")
    if isinstance(ma, str) and ma.isdigit():
        out["max_age"] = int(ma)
    return out


def _collect_assets(html: str, base_url: str, include_third_party: bool) -> list[str]:
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")
    base_host = urlparse(base_url).netloc
    urls: list[str] = []
    for tag, attr in (("script", "src"), ("img", "src"), ("source", "src")):
        for el in soup.find_all(tag, attrs={attr: True}):
            urls.append(urljoin(base_url, el[attr]))
    for el in soup.find_all("link", href=True):
        rels = {r.lower() for r in (el.get("rel") or [])}
        if rels & {"stylesheet", "preload", "modulepreload", "icon"}:
            urls.append(urljoin(base_url, el["href"]))
    seen, out = set(), []
    for u in urls:
        p = urlparse(u)
        if p.scheme not in ("http", "https") or u in seen:
            continue
        if not include_third_party and p.netloc != base_host:
            continue
        seen.add(u)
        out.append(u)
    return out


def _head(url: str) -> tuple[int | None, dict, str | None]:
    headers = dict(_BASE_HEADERS)
    headers["User-Agent"] = _DEFAULT_UA
    try:
        r = requests.head(url, headers=headers, timeout=12, allow_redirects=True)
        if r.status_code in (405, 501):
            raise requests.RequestException("HEAD not allowed")
        return r.status_code, dict(r.headers), None
    except requests.RequestException:
        try:
            r = requests.get(url, headers=headers, timeout=12, stream=True)
            r.close()
            return r.status_code, dict(r.headers), None
        except requests.RequestException as e:
            return None, {}, str(e)[:120]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("url")
    ap.add_argument("--max-assets", type=int, default=20)
    ap.add_argument("--include-third-party", action="store_true")
    args = ap.parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        page = fetch(url, timeout=20)
    except requests.RequestException as e:
        print(json.dumps({"target": url, "error": str(e)[:200]}, indent=2))
        return 1

    html_cc = _parse_cache_control(page.headers.get("Cache-Control"))
    assets = _collect_assets(page.text, page.url, args.include_third_party)
    probed = []
    for asset_url in assets[: args.max_assets]:
        status, headers, err = _head(asset_url)
        cc = _parse_cache_control(headers.get("Cache-Control"))
        probed.append({
            "url": asset_url,
            "path": urlparse(asset_url).path,
            "status": status,
            "error": err,
            "hashed_name": _looks_hashed(urlparse(asset_url).path),
            "cache_control": cc["raw"],
            "max_age": cc["max_age"],
            "directives": sorted(cc["directives"]),
        })

    issues = []
    contradictory, undercached_hashed, missing_cc = [], [], []
    for a in probed:
        if a["error"] or a["status"] != 200:
            continue
        d = set(a["directives"])
        combos = [("immutable", "must-revalidate"), ("no-store", "max-age"),
                  ("no-cache", "immutable")]
        for x, y in combos:
            if x in d and (y in d or (y == "max-age" and a["max_age"])):
                contradictory.append({**{k: a[k] for k in ("path", "cache_control")},
                                      "combo": f"{x} + {y}"})
                break
        if a["hashed_name"] and a["max_age"] is not None and a["max_age"] < _THIRTY_DAYS:
            undercached_hashed.append({"path": a["path"], "max_age": a["max_age"],
                                       "cache_control": a["cache_control"]})
        if a["cache_control"] is None:
            missing_cc.append(a["path"])

    if undercached_hashed:
        issues.append(finding(
            "P2",
            f"{len(undercached_hashed)} content-hashed asset(s) cached < 30 days "
            f"(e.g. {undercached_hashed[0]['path']} max-age={undercached_hashed[0]['max_age']}s) "
            "— hashed filenames change with content, serve max-age=31536000, immutable",
            evidence={"assets": undercached_hashed[:10]}))
    if contradictory:
        issues.append(finding(
            "P2",
            f"{len(contradictory)} asset(s) with contradictory cache directives "
            f"(e.g. {contradictory[0]['combo']}) — pick one policy per asset class",
            evidence={"assets": contradictory[:10]}))
    if missing_cc:
        issues.append(finding(
            "P2", f"{len(missing_cc)} asset(s) served without Cache-Control",
            evidence={"paths": missing_cc[:10]}))
    if html_cc["max_age"] and html_cc["max_age"] > 3600 and \
            "must-revalidate" not in html_cc["directives"]:
        issues.append(finding(
            "P2",
            f"HTML document cached {html_cc['max_age']}s without revalidation — "
            "content updates will be invisible to repeat visitors",
            evidence={"cache_control": html_cc["raw"]}))

    out = result_envelope(
        url, page, "asset_cache_checker.py",
        html_cache_control=html_cc["raw"],
        assets_found=len(assets),
        assets_probed=len(probed),
        hashed_assets=sum(1 for a in probed if a["hashed_name"]),
        assets=probed,
        issues=issues,
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 2 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
