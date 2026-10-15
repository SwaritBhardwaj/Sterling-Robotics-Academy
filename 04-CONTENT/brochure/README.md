# Brochure

8 A4 pages: Cover, The course, How it works, The kit, Your mentor, Cohorts, Admission, Questions.

| File | What it is |
|---|---|
| `Sterling-Robotics-Academy-Brochure.pdf` | The current PDF sent to families (15 Oct 2026) |
| `source/brochure-src.html` | The page source. Edit this |
| `source/assets/` | Images, logos, headshot source, fonts |
| `source/build.py` | Builds a self-contained HTML and the PDF |

**Live artifact:** https://claude.ai/artifact/Q9fNLPL7SbDxC75f2SAJut (v23).

## Rebuild
```
cd 04-CONTENT/brochure/source
pip install pillow playwright pypdf
python3 build.py
```
It writes `sterling-brochure.html` (git-ignored, 1.2 MB) and the PDF next to it. Move the new PDF up one folder, replacing the old one, and add a line to the history below.

## Look ("Lucid Machinery")
Light, Apple/B&O style. White, ink `#1D1D1F`, greys `#86868B` and `#5E5E63`, line `#E2E2E6`, panel `#F5F5F7`, one blue `#1F55D6`. Instrument Sans, Instrument Serif, Geist Mono. One blue pill button style.

## Rules
- Every CTA links to https://wa.me/message/O2K3UG6UWJEBJ1. Page 8 also says: "Button not opening? Save +1 754 279 2415 and send "Entry test" on WhatsApp."
- No QR code, no India number, no header section numbers, no class times, no "reasoning test".
- Big one-word page titles, parent-friendly week names, generous white space. Readable on a phone, but fonts "not too big".
- **A separate phone edition was made and rejected** ("stick to the original layout"). Don't make one again.
- Weakest point: no testimonials or student photos yet. Never invent them.

## History
| Date | Version | Change |
|---|---|---|
| 2026-10-15 | v23 | Founding cohort "Limited seats only"; "A small class, so more questions get answered live."; email hellosterlingrobotics@gmail.com |
