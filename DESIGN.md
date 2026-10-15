---
name: Sterling Robotics Academy course site
description: The mentor's notebook. One unlined, slightly yellowed sheet, opened at this week.
colors:
  paper: "#F3ECD9"
  paper-light: "#FAF6EA"
  ink: "#26221D"
  pencil: "#625B50"
  pencil-soft: "#8E8576"
  pencil-faint: "#B8AD97"
  pen: "#1D4BBE"
  pen-deep: "#163A93"
  highlighter: "#FFE14D"
  highlighter-soft: "rgba(255, 225, 77, .55)"
  pencil-wash: "rgba(98, 91, 80, .08)"
  tape: "rgba(246, 240, 220, .62)"
  redo: "#8A2A12"
typography:
  display:
    fontFamily: "Instrument Serif, Literata, Georgia, serif"
    fontSize: "clamp(2.6rem, 2rem + 2.6vw, 3.9rem)"
    fontWeight: 400
    lineHeight: 1.02
    letterSpacing: "-0.012em"
  section:
    fontFamily: "Instrument Serif, Literata, Georgia, serif"
    fontSize: "2rem"
    fontWeight: 400
    lineHeight: 1.1
  body:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.7
  question:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "1.4rem"
    fontWeight: 400
    lineHeight: 1.45
  todo:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "1.22rem"
    fontWeight: 500
    lineHeight: 1.65
  numeral:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "5rem"
    fontWeight: 300
    lineHeight: 0.9
  hand:
    fontFamily: "Shantell Sans, Comic Neue, cursive"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
  mono:
    fontFamily: "Geist Mono, ui-monospace, Menlo, monospace"
    fontSize: "0.92rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  wobble: "255px 18px 225px 16px / 16px 225px 18px 255px"
  sm: "4px"
  md: "6px"
  pending: "14px 6px 12px 8px"
spacing:
  margin-column: "12.5rem"
  gap: "3.5rem"
  reading-column: "41rem"
components:
  button:
    textColor: "{colors.ink}"
    rounded: "{rounded.wobble}"
    padding: "0.62rem 1.35rem"
  button-hover:
    backgroundColor: "{colors.pencil-wash}"
  do-now-line:
    backgroundColor: "{colors.highlighter}"
    typography: "{typography.todo}"
  taped-in:
    backgroundColor: "{colors.paper-light}"
    padding: "0.7rem"
  template:
    backgroundColor: "{colors.paper-light}"
    typography: "{typography.mono}"
    padding: "2.3rem 1.2rem 1rem"
---

# Design: the mentor's notebook

## Overview

The course site is Swarit's own notebook, opened at this week. One continuous, unlined, slightly yellowed sheet. It refuses the course-portal default of white cards, tiles and progress bars.

Mode: **Read**. A student (grades 6 to 12, on a laptop beside the robot) finds this week's question, what to have ready, and the tasks, then sends the work. Parents check dates and notes.

The paper colour and the textured, organic feel are the owner's brief. Keep them even when a detector calls cream backgrounds or Instrument Serif common.

## Colors

| Token | Hex | Job | On paper |
|---|---|---|---|
| `--paper` | #F3ECD9 | The sheet | |
| `--paper-light` | #FAF6EA | Taped-in things, inputs | |
| `--ink` | #26221D | All text a student must read | 13.4:1 |
| `--pencil` | #625B50 | Margin notes, labels, locked weeks | 5.7:1 (4.9 on the darkest mottle) |
| `--pencil-soft` | #8E8576 | List markers, the "~" rule only | 3.1:1 |
| `--pencil-faint` | #B8AD97 | Borders, dotted leaders, scrollbar only | 1.9:1 |
| `--pen` | #1D4BBE | Links, focus ring | 6.4:1 |
| `--pen-deep` | #163A93 | Link hover | 8.6:1 |
| `--hl` | #FFE14D | The highlighter (see budget) | ink on it 12.1:1 |
| pencil wash | rgba(98,91,80,.08) | Hover on rows, buttons, copy | |
| `--tape` | rgba(246,240,220,.62) | Tape strips | |

Rules:
- `--pencil-soft` and `--pencil-faint` are never used for text a student has to read.
- Locked weeks use `--pencil` in italic, not a fainter grey.
- **Highlighter budget.** Yellow means "the one thing to do now". Per page: one swept line, plus `.contents li.now` and at most one author `==mark==` per section. Never yellow for hover, tags, the current menu item, selected options or errors. Text selection may use it.

## Typography

| Role | Face | Size | Notes |
|---|---|---|---|
| Page title (h1) | Instrument Serif 400 | clamp(2.6rem to 3.9rem) | Brand face from the brochure |
| Section (h2) | Instrument Serif 400 | 2rem (1.75rem on phone) | More space above than below |
| Task heading (h3) | Literata 600 | 1.15rem | |
| Reading text | Literata 400 | 18px laptop, 17px phone | Line height 1.7, column about 41rem |
| Question of the week | Literata italic | 1.4rem | Max 34ch |
| Do-now line | Literata 500 | 1.22rem | Inside the highlighter |
| Big numerals (week number, contents) | **Literata 300, lining figures** | 5rem margin, 1.45rem contents | Instrument Serif's "1" reads as "l", so it never sets numbers on their own |
| Handwritten notes | Shantell Sans | **1.0625rem minimum** | Margin notes, tags, captions, dates, pager labels, footer only |
| Code and templates | Geist Mono | 0.92rem | Code only |

Floor: no text a student acts on goes under 17px. The wordmark subtitle (0.78rem caps) is the only exception.

## Layout

- Desktop: margin column 12.5rem for pencil notes, gap 3.5rem, reading column about 41rem. The margin is sticky.
- 960px and under: margin 9.5rem, gap 2.2rem, week numeral 4.2rem.
- 760px and under: one column. Margin notes become one row above the title (week, class date, cohort). Task tags sit before their heading. Menu links get 44px tap height.
- Lists of weeks and files use dotted leaders, like a contents page.
- **Week page order** (build.mjs enforces the first part): title, question, do-now line, **Have ready for class**, the intro and outcomes, Assignment, Before you submit, Resources, Files, Solutions, Class recording, Submit, pager.

## Elevation & Depth

Flat paper, plus one lift for things taped in.
- Taped-in figures, videos and templates: `--paper-light`, shadow `0 1px 1px rgba(80,55,20,.10), 0 10px 22px -14px rgba(80,55,20,.35)`, a translucent tape strip with a torn edge.
- No other shadows. No borders around content blocks except the dashed "pending" outline.

## Shapes

- Ink-ringed button: 2px ink border with the hand-drawn wobble radius.
- Taped-in pictures and video rotate slightly (-0.5deg, alternating +0.45deg). **Text-dense or interactive taped items do not rotate** (templates, code, forms).
- Pending things (a recording to come): 1.5px dashed `--pencil-faint`, radius 14px 6px 12px 8px.
- Current menu item: a 2px ink pencil line under the word, slightly tilted.
- Must-do tag: ink, underlined in ink. Stretch and other tags: pencil.

## Components

**Do-now line** (`.todo mark.sweep`). One sentence, swept once. On week pages it follows the date (app.js):
- Before class: "Before Sunday, January 3, get everything under Have ready for class done." with a link to that section.
- After class until Saturday: "Do the tasks below and send them by Saturday, 8 PM Eastern."
- Once the student marks the week sent: "Sent. Swarit will review it."
Status and errors never sit in the highlighter (`mark.plain`).

**Contents rows.** Number, title, dotted leader, a pencil note: "this week", "class Sun, Jan 3", "opens Mon, Nov 23", or "sent Tue, Nov 10". Hover is a pencil wash.

**Templates** (fill-in tables in code blocks). Copy button top right with room above the text, so it never covers a line. When a template is wider than the column, the right edge fades and a pencil note says "scroll sideways for more", until scrolled to the end. Prefer short templates; split wide ones.

**Resources list.** Every item is a link. An item named before its link exists shows "link coming before class" in pencil, so nothing looks clickable that is not.

**Submit.** "Send week N on WhatsApp" opens WhatsApp with "Week N work from Aarav:" already typed. A click records "sent" in that browser, shown under the button and in the contents row.

**Message pages** (lib/guard.js: locked week, locked solutions, private page). Same shell as every page: menu, a margin note with the opening date, a "See all weeks" button, and tappable WhatsApp and email. Sign-in problem pages hide the menu, since it would not open.

**Footer.** WhatsApp number and email are links.

**States to design for every new component:** loading, empty, error, locked, done, and the keyboard focus ring (2.5px pen outline, 3px offset, follows the shape).

## Do's and Don'ts

Do:
- Keep one thing yellow per page.
- Name every resource as a link, or mark it as coming.
- Put "Have ready for class" first on a week page.
- Keep motion to two moments: the highlighter sweep (1.1s, exponential ease-out, re-run when the line changes) and the page cross-fade (0.22s out, 0.32s in). Both off under reduced motion.
- Give images in figures an empty alt when the caption describes them, so screen readers read it once.
- Give task tags real text for screen readers (`.sr-only` "Must do:"), not only CSS content.
- Keep the skip link and `main#main`.
- Print cleanly: no paper texture, no menu, tables and templates in full, link addresses shown.

Don't:
- Use cards, tiles or progress bars.
- Use yellow for hover, tags, the menu or errors.
- Use `--pencil-soft` or `--pencil-faint` for text.
- Rotate text that a student reads or types into.
- Set numbers on their own in Instrument Serif.
- Put anything under 17px that a student acts on.
- Push a preview to `main`. Previews: `npx wrangler deploy -c wrangler.preview.jsonc --temporary`.

## Markdown extensions (build/build.mjs)

- `==text==` highlights (use sparingly, see the budget).
- A lone image becomes a taped-in figure; the alt text becomes the caption. Keep images in the week's `img/` folder.
- A lone YouTube link becomes a taped-in video.
- `### Must: ...`, `### Stretch: ...`, `### Optional: ...`, `### Bonus: ...` get a margin tag.
- Code blocks become a template with a copy button.
- `## Have ready for class` gets the `#have-ready` anchor and moves to the top.
