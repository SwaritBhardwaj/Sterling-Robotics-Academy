#!/usr/bin/env python3
"""
Throttled lab Core Web Vitals probe — real browser, no PSI key required.

Why it matters (verified Aug 2026 on a live production audit):
  - psi_checker.py depends on a Google PSI API key; without one the CWV
    category silently drops out of page_score. This probe fills that gap
    with a local Playwright Chromium run.
  - Font-swap CLS, late-resource layout shifts, and slow-network LCP only
    manifest when the network/CPU are constrained. An unthrottled probe on
    a dev machine measured CLS 0.002 on a page whose throttled CLS is 0.248
    (at the "poor" threshold) — same page, same code, different timing.
  - Defaults approximate Lighthouse mobile: 150ms RTT, 1.6Mbps down,
    750Kbps up, 4x CPU slowdown, 390x844 mobile viewport.

Reported per condition (median of --runs):
  - TTFB / FCP / LCP (ms) + the actual LCP element (tag, text/src,
    loading attribute) — no "LCP candidate" heuristics, the real entry
  - CLS + top shift entries with source elements and timing
  - font-swap correlation: layout shifts that fire within 200ms after a
    .woff2 finishes downloading are flagged as likely font-swap induced
  - transfer bytes + request count (cross-origin without
    Timing-Allow-Origin reports transferSize 0 — understated, flagged)
  - INP is NOT reported: it requires real user interaction; a lab probe
    that invents an INP number would be lying. Field data (CrUX) is the
    only honest source.

Exit code:
  0 = all medians in "good" (LCP<=2500ms, CLS<=0.1)
  1 = probe failed (browser missing, navigation timeout)
  2 = at least one metric out of "good"

Usage:
  cwv_throttled_probe.py <url> [--runs 3] [--with-fast] [--rtt-ms 150]
                         [--download-kbps 1600] [--upload-kbps 750]
                         [--cpu-rate 4] [--settle-ms 3000] [--desktop]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys

from _fetch import result_envelope, finding

_MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
)

_COLLECT_JS = """
(settleMs) => new Promise(resolve => {
  const out = {ttfb: null, fcp: null, lcp: null, lcp_element: null,
               cls: 0, shifts: [], requests: 0, transfer_bytes: 0,
               fonts: [], zero_transfer_resources: 0};
  const nav = performance.getEntriesByType('navigation')[0];
  if (nav) { out.ttfb = Math.round(nav.responseStart); }
  const fcpE = performance.getEntriesByName('first-contentful-paint');
  if (fcpE.length) out.fcp = Math.round(fcpE[0].startTime);
  try {
    new PerformanceObserver(l => {
      const es = l.getEntries();
      if (!es.length) return;
      const e = es[es.length - 1];
      out.lcp = Math.round(e.startTime);
      const el = e.element;
      out.lcp_element = el ? {
        tag: el.tagName,
        text: (el.textContent || '').trim().slice(0, 80) || null,
        src: e.url || null,
        loading: el.getAttribute ? el.getAttribute('loading') : null,
        fetchpriority: el.getAttribute ? el.getAttribute('fetchpriority') : null,
      } : null;
    }).observe({type: 'largest-contentful-paint', buffered: true});
    new PerformanceObserver(l => {
      for (const e of l.getEntries()) {
        if (e.hadRecentInput) continue;
        out.cls += e.value;
        if (e.value >= 0.01) out.shifts.push({
          t: Math.round(e.startTime),
          value: Math.round(e.value * 10000) / 10000,
          sources: (e.sources || []).slice(0, 3).map(s => s.node
            ? ((s.node.className && String(s.node.className).slice(0, 60)) || s.node.tagName || '?')
            : '?'),
        });
      }
    }).observe({type: 'layout-shift', buffered: true});
  } catch (err) {}
  setTimeout(() => {
    const res = performance.getEntriesByType('resource');
    out.requests = res.length + 1;
    out.transfer_bytes = res.reduce((a, r) => a + (r.transferSize || 0), 0)
                       + (nav ? (nav.transferSize || 0) : 0);
    out.zero_transfer_resources = res.filter(r => !r.transferSize).length;
    out.fonts = res.filter(r => r.name.includes('.woff'))
      .map(r => ({name: r.name.split('/').pop(),
                  finished_ms: Math.round(r.responseEnd),
                  transfer: r.transferSize || 0}));
    out.cls = Math.round(out.cls * 10000) / 10000;
    resolve(out);
  }, settleMs);
})
"""


def _run_once(p, url: str, args, throttled: bool) -> dict:
    browser = p.chromium.launch()
    try:
        ctx_opts = dict(user_agent=_MOBILE_UA, viewport={"width": 390, "height": 844},
                        device_scale_factor=3, is_mobile=True, has_touch=True)
        if args.desktop:
            ctx_opts = dict(viewport={"width": 1280, "height": 800})
        context = browser.new_context(**ctx_opts)
        page = context.new_page()
        cdp = context.new_cdp_session(page)
        if throttled:
            cdp.send("Network.enable")
            cdp.send("Network.emulateNetworkConditions", {
                "offline": False,
                "latency": args.rtt_ms,
                "downloadThroughput": args.download_kbps * 1000 // 8,
                "uploadThroughput": args.upload_kbps * 1000 // 8,
            })
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": args.cpu_rate})
        resp = page.goto(url, wait_until="load", timeout=90000)
        m = page.evaluate(_COLLECT_JS, args.settle_ms)
        m["http_status"] = resp.status if resp else None
        m["final_url"] = page.url
        return m
    finally:
        browser.close()


def _median(runs: list[dict], key: str):
    vals = [r[key] for r in runs if r.get(key) is not None]
    if not vals:
        return None
    med = statistics.median(vals)
    return round(med, 4) if isinstance(med, float) else med


def _font_swap_correlation(run: dict) -> list[dict]:
    """Shifts starting within 200ms after a font finished = likely font-swap."""
    hits = []
    for shift in run.get("shifts", []):
        for font in run.get("fonts", []):
            delta = shift["t"] - font["finished_ms"]
            if 0 <= delta <= 200:
                hits.append({"shift_t": shift["t"], "shift_value": shift["value"],
                             "font": font["name"], "font_finished_ms": font["finished_ms"],
                             "delta_ms": delta, "shift_sources": shift.get("sources", [])})
    return hits


def _summarize(runs: list[dict], condition: str) -> dict:
    worst_cls_run = max(runs, key=lambda r: r.get("cls") or 0)
    return {
        "condition": condition,
        "runs": len(runs),
        "ttfb_ms_median": _median(runs, "ttfb"),
        "fcp_ms_median": _median(runs, "fcp"),
        "lcp_ms_median": _median(runs, "lcp"),
        "lcp_element": runs[0].get("lcp_element"),
        "cls_median": _median(runs, "cls"),
        "cls_per_run": [r.get("cls") for r in runs],
        "top_shifts_worst_run": worst_cls_run.get("shifts", [])[:5],
        "font_swap_correlated_shifts": _font_swap_correlation(worst_cls_run),
        "fonts_loaded": len(runs[0].get("fonts", [])),
        "requests_median": _median(runs, "requests"),
        "transfer_bytes_median": _median(runs, "transfer_bytes"),
        "transfer_understated": bool(runs[0].get("zero_transfer_resources")),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("url")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--with-fast", action="store_true",
                    help="also run an unthrottled set for comparison")
    ap.add_argument("--rtt-ms", type=int, default=150)
    ap.add_argument("--download-kbps", type=int, default=1600)
    ap.add_argument("--upload-kbps", type=int, default=750)
    ap.add_argument("--cpu-rate", type=int, default=4)
    ap.add_argument("--settle-ms", type=int, default=3000)
    ap.add_argument("--desktop", action="store_true",
                    help="1280x800 desktop viewport instead of mobile emulation")
    args = ap.parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(json.dumps({"target": url, "error":
                          "playwright not installed — pip install playwright && playwright install chromium"}))
        return 1

    conditions = []
    try:
        with sync_playwright() as p:
            throttled_runs = [_run_once(p, url, args, throttled=True)
                              for _ in range(args.runs)]
            conditions.append(_summarize(throttled_runs, "throttled"))
            if args.with_fast:
                fast_runs = [_run_once(p, url, args, throttled=False)
                             for _ in range(args.runs)]
                conditions.append(_summarize(fast_runs, "fast"))
    except Exception as e:
        msg = str(e)
        hint = " — run: python -m playwright install chromium" \
            if "Executable doesn't exist" in msg else ""
        print(json.dumps({"target": url, "error": f"probe failed: {msg[:300]}{hint}"}))
        return 1

    throttled = conditions[0]
    issues = []
    lcp = throttled["lcp_ms_median"]
    cls = throttled["cls_median"]
    if lcp is not None and lcp > 4000:
        issues.append(finding("P1", f"LCP {lcp}ms (throttled lab) — 'poor' (>4000ms)",
                              evidence=throttled["lcp_element"]))
    elif lcp is not None and lcp > 2500:
        issues.append(finding("P2", f"LCP {lcp}ms (throttled lab) — 'needs improvement' (2500-4000ms)",
                              evidence=throttled["lcp_element"]))
    if cls is not None and cls > 0.25:
        issues.append(finding("P1", f"CLS {cls} (throttled lab) — 'poor' (>0.25)",
                              evidence={"top_shifts": throttled["top_shifts_worst_run"]}))
    elif cls is not None and cls > 0.1:
        issues.append(finding("P2", f"CLS {cls} (throttled lab) — 'needs improvement' (0.1-0.25)",
                              evidence={"top_shifts": throttled["top_shifts_worst_run"]}))
    if throttled["font_swap_correlated_shifts"]:
        c = throttled["font_swap_correlated_shifts"][0]
        issues.append(finding(
            "P2",
            f"layout shift of {c['shift_value']} fires {c['delta_ms']}ms after "
            f"{c['font']} finishes — likely font-swap CLS; preload that font or add "
            "metric-matched fallback (size-adjust/ascent-override)",
            evidence=throttled["font_swap_correlated_shifts"][:3]))
    lcp_el = throttled.get("lcp_element") or {}
    if lcp_el.get("loading") == "lazy":
        issues.append(finding("P1", "measured LCP element has loading=\"lazy\" — remove it",
                              evidence=lcp_el))

    out = result_envelope(
        url, None, "cwv_throttled_probe.py",
        mode="lab",
        note="lab probe, not field data (CrUX); INP intentionally not reported (needs real interaction)",
        throttle_profile={"rtt_ms": args.rtt_ms, "download_kbps": args.download_kbps,
                          "upload_kbps": args.upload_kbps, "cpu_rate": args.cpu_rate},
        viewport="desktop-1280x800" if args.desktop else "mobile-390x844-dpr3",
        conditions=conditions,
        issues=issues,
    )
    out["final_url"] = throttled_runs[0].get("final_url")
    out["http_status"] = throttled_runs[0].get("http_status")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 2 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
