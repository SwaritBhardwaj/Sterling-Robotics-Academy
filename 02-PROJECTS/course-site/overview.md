# Course site

## Brief
The private website students and parents use during the course: this week's question, what to have ready, tasks, files, recordings, solutions after class, and a private page per student. Sign-in is an emailed one-time code. Built and run at no monthly cost.

## Status
**Live** on `main` (brochure look). **Notebook redesign built and liked, not merged** (branch `redesign`).

## Code
- Repo: `SwaritBhardwaj/Sterling-Robotics-Academy` (private)
- `main`: live site at https://academy.sterlingrobotics.workers.dev. Every push deploys and uses build minutes.
- `redesign`: the notebook redesign. Pushed to GitHub 2026-10-15.
- Branch map: `SYSTEM/branches.md`

## How it works
- `content/` holds all course material as Markdown: `weeks/week-NN/index.md` (+ files, `img/`, `solutions/`), `resources/`, `students/students.json` + `students/<slug>.md`, `site.json` (links, admins, email), `schedule.json` (cohort dates, unlock rules).
- `build/build.mjs` turns content into `dist/`. `PREVIEW=1` writes `preview/` with sample data.
- `build/test.mjs`: 27 checks (locked weeks, other students' pages, unknown emails, expired, tampered and faked tokens, the Worker serving pages and `/api/me`).
- `worker/index.js` runs before every request and calls `lib/guard.js`: verifies the Cloudflare Access token, checks the email against students and admins, locks weeks and solutions by date, keeps student pages private. `lib/me.js` serves `/api/me` for the home page.
- Unlock rules: a week opens 6 days before its class (the Monday before). Solutions open 6 days after class (the Saturday after). Times use US Eastern (-05:00).
- Admins (swarit000@gmail.com) see every week and every student page at any time.
- `DEV_EMAIL` is for local and temporary previews only. Never on the live Worker.

## Weekly routine (once classes start)
| When | What |
|---|---|
| Before class | Add files to `content/weeks/week-NN/` |
| After class | Paste the unlisted YouTube link into `recording:` |
| After class | Put solutions in `content/weeks/week-NN/solutions/` |
| After each 1:1 | Add notes to `content/students/<slug>.md` |

Batch these into one push a week to save build minutes.

## Add a family
1. Add their emails to the Cloudflare Access policy "Class families".
2. Add them to `content/students/students.json` (slug, name, grade, cohort, emails).
3. Create `content/students/<slug>.md` from the sample.

## Milestones
- [x] Site live with sign-in (Oct 2026)
- [x] Notebook redesign built, liked 2026-10-15
- [x] Redesign pushed to GitHub, temporary preview deployed 2026-10-15
- [x] 2026-10-15 Impeccable critique (27/40) and fixes on `redesign`: one highlighter, do-now line follows the date, Have ready first, template scroll hints, WhatsApp prefilled, locked pages with menu, 17px type floor, print styles. DESIGN.md rewritten.
- [ ] Swarit approves merging the redesign to `main`
- [ ] Progress database (see `../progress-database/overview.md`)
- [ ] Real families added, sample student removed (before 15 Nov)

## Next action
- Swarit reviews the preview and says merge or change.

Related: `decisions.md` (hosting, setup, problems hit) · `design.md` (notebook look) · `tasks.md`
