# Course site: the mentor's notebook design

_Full spec lives with the code: `DESIGN.md` and `PRODUCT.md` on branch `redesign`. This note is the summary and the history._

## Swarit's brief (14 Oct 2026)
"A paper feeling attached to it with important things highlighted with a highlighter design, and it should feel very organic, very much like it's a real paper, and we are gonna add in diagrams, videos, etc."
"End-to-end, the website should be minimal, should have a few animation, very smooth, it should feel very smooth, cohesive, should not be very much complicated for the students."
Paper: "textured paper without any lines. Just a continue stretch of paper, not very modern, not very new kind of like a yellow."
Main user: students on laptops. He picked the "Mentor's notebook" direction and asked for the impeccable design skill throughout.

**15 Oct:** "I like the design." Not yet approved to merge.

## What it is
- One unlined, slightly yellowed paper sheet (`#F3ECD9`, two SVG noise layers, faint vignette). An early fibre layer made streaks that looked like lines, so it was removed.
- Yellow highlighter (`#FFE14D`) only for the one thing to do now, the current week, the current menu item, "must do" tags and `==text==`.
- Ink `#26221D` text, pencil `#625B50` notes, pen blue `#1D4BBE` links.
- Type: Literata for reading, Instrument Serif for titles (brand face from the brochure), Shantell Sans for handwritten margin notes, Geist Mono for code.
- Margin column with pencil notes (big week number, next class, cohort). Task tags sit in the margin.
- Taped-in figures, videos and code templates.
- Contents page with dotted leaders. Locked weeks in pencil grey with their opening date.
- Two animations: a highlighter sweep on the to-do line, and a fade between pages. Both off under reduced motion.

## Markdown extensions for week pages
- `==text==` highlights.
- A lone image becomes a taped-in figure; alt text is the caption. Keep images in the week's `img/` folder.
- A lone YouTube link becomes a taped-in video.
- `### Must: ...`, `### Stretch: ...`, `### Optional: ...`, `### Bonus: ...` get a margin tag.
- Code blocks get a copy button.

## Impeccable review, 15 Oct 2026
Score 27/40 (two independent reviews: design and detector). Strong, specific world; held back by states and content handling. Fixed on `redesign` (commit d01fc6a):
- Highlighter budget: yellow only for the one thing to do now. Menu, tags, hover, errors no longer yellow.
- Do-now line on week pages follows the date and links to Have ready for class, which now comes first.
- Templates: no rotation, bigger text, copy button never covers a line, "scroll sideways for more" when wide.
- Submit: WhatsApp opens with "Week N work from <name>:" typed in; a sent marker shows on the week and in the contents.
- Locked-week pages: menu, opening date, See all weeks, tappable contacts.
- 17px floor for handwritten text, locked weeks pass contrast, numerals in Literata (Instrument Serif's "1" read as "l"), 44px phone menu, skip link, screen-reader text for tags, print styles.
- DESIGN.md rewritten in the standard token format, with contrast table, type scale, states and week page order.
Not fixed (content work): week 8 and others name files that are not uploaded yet (now marked "link coming before class"); ASCII templates could become real tables; "Kit needed" says little.

## Brochure look (for comparison)
The brochure and the live `main` site use the "Lucid Machinery" look: white, ink `#1D1D1F`, one blue `#1F55D6`, Instrument Sans and Serif, Geist Mono.
