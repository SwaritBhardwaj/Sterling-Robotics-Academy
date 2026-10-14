# Design: the mentor's notebook

The course site is Swarit's own notebook, opened at this week. One continuous, unlined, slightly yellowed sheet. No cards, tiles or progress bars.

## World
- Paper: `--paper #F3ECD9`, with fine tooth and soft mottling from two SVG noise layers, and a faint warm vignette. No ruled lines.
- Ink: `--ink #26221D` for text. Pencil: `--pencil #625B50` for notes, `--pencil-soft` and `--pencil-faint` for locked items and dotted leaders.
- Pen: `--pen #1D4BBE` for links.
- Highlighter: `--hl #FFE14D`. Used only for the one thing to do now, the current week, the current nav item, "must do" tags and `==text==` in Markdown.
- Taped-in things: figures, videos and code templates sit on lighter paper (`--paper-light`) with a strip of translucent tape and a soft lift shadow. Slight rotation, alternating.

## Type
- Literata: reading text, 18px on laptop, 17px on phone.
- Instrument Serif: page titles, section titles, big week numbers. It is the brand face from the brochure, kept on purpose even though the detector flags it as common.
- Shantell Sans: handwritten margin notes, task tags, dates, captions only.
- Geist Mono: code only.

## Layout
- Desktop: a margin column (12.5rem) for pencil notes, then a reading column of about 41rem. Task tags ("must do", "stretch") sit in the margin beside their heading.
- Under 760px the margin notes move inline above the title and tags sit before the heading.
- Lists of weeks and files use dotted leaders, like a contents page.

## Motion
- One authored moment: the highlighter sweeps across the "do this now" line once (1.1s, exponential ease-out). The line is fully visible without it.
- Page changes cross-fade with view transitions; the running head stays still.
- Hover: soft highlighter wash on rows and buttons.
- All of it switches off under reduced motion.

## Markdown extensions (build/build.mjs)
- `==text==` highlights.
- A lone image becomes a taped-in figure; the alt text is the caption. Put images in a week's `img/` folder so they are not listed as files.
- A lone YouTube link becomes a taped-in video.
- `### Must: ...`, `### Stretch: ...`, `### Optional: ...`, `### Bonus: ...` get a margin tag.
- Code blocks become a taped-in template with a copy button.

## Previews
`PREVIEW=1 npm run build` writes `preview/` with relative links and sample student data (founding cohort, week 2). Previews are never pushed to `main`.
