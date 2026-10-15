---
target: course site (assets/site.css)
total_score: 27
max_score: 40
na_heuristics: 
p0_count: 1
p1_count: 3
target_identity: "file:/home/user/Sterling-Robotics-Academy/assets/site.css"
target_fingerprint: "sha256:935b0f9876aefce9e4693ed9757ecb28d663ebd53881db9c96f42a419fb8abe1"
target_path: /home/user/Sterling-Robotics-Academy/assets/site.css
timestamp: 2026-10-15T09-35-41Z
slug: assets-site-css
---
Method: dual-agent (A: design review sub-agent, B: detector and browser sub-agent)

## Design Health Score
| # | Heuristic | Score | Key issue |
|---|---|---|---|
| 1 | Visibility of system status | 2 | Do-now line was fixed text on all 12 weeks; no submitted state |
| 2 | Match with the real world | 3 | ASCII pipe tables; "Kit needed" says little |
| 3 | User control and freedom | 3 | Locked-week page had no menu |
| 4 | Consistency and standards | 3 | Yellow meant five things |
| 5 | Error prevention | 2 | Bare WhatsApp link; wide templates clipped silently |
| 6 | Recognition rather than recall | 3 | Have ready section sat third |
| 7 | Flexibility and efficiency | 2 | No anchors, no print, no skip link |
| 8 | Aesthetic and minimalist design | 3 | Highlighter inflation, dead Resources list |
| 9 | Error recovery | 3 | Errors shown inside the highlighter |
| 10 | Help and documentation | 3 | Footer contacts not tappable |
| Total | | 27/40 | Acceptable |

## Design specificity
Authored for this product: margin numeral, dotted leaders, taped-in figures, wobble button, italic question, highlighter. Detector: 91 warnings, all accepted or false positives (cream-palette and overused-font are the owner's brief; tight-leading and cramped-padding are false positives; organic-clip-path is the intended tape strip).

## Priority issues
- [P0] Must-dos depend on files or links not on the page (week 8 balance_stub). Fix: pending note for unlinked resources; content to link before weeks open.
- [P1] Highlighter inflated and the do-now line ignores the date. Fix: highlighter budget, phase-aware line, Have ready first.
- [P1] Templates clip silently and are small. Fix: no rotation, bigger mono, room for copy, fade and scroll note.
- [P1] Submit ends in a context-free WhatsApp handoff. Fix: prefilled message, sent marker.
- [P2] Text under 17px, locked rows fail contrast, small tap targets. Fix: hand floor 1.0625rem, pencil for locked, 44px menu on phone.

## Persona red flags
Aarav (12): ambiguous "1" in Instrument Serif, clipped tuning log, unlinked Resources. Priya (parent): no class time, untappable footer, no progress view. Keyboard user: tags only in CSS content, duplicate alt and caption, silent copy feedback, no skip link.
