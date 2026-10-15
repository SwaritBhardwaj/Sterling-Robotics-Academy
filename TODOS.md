# TODOS: Sterling Robotics Academy

Deferred work with enough context to pick up cold. Live priorities live in `CLAUDE.md` Weekly Focus. This file is what we decided not to do yet.

---

## Routines (morning digest, weekly review, check-ins)
**Deferred 2026-10-15.** Swarit: "an overkill right now."
**What:** the scheduled Claude Code jobs from the Influenzo setup kit.
**When to revisit:** once the founding cohort is running and there is weekly state worth summarising.
**Notes:** routines must run on branch `vault` here (not `main`, which is the live site). Use `TZ='Asia/Kolkata'` for dates. Cron is UTC.

## Custom domain
**Deferred.** About $10 a year. The site runs on `academy.sterlingrobotics.workers.dev` for now.

## Certificate template, demo day plan, naming mentors
**Can wait until December** (from the Oct 15 launch checklist).

## Testimonials and student photos
**Waiting on Swarit.** Never invent them. The brochure's weakest point.

## Mirror of student week pages in the vault
**Not done on purpose (2026-10-15).** Student pages live in the site repo `content/weeks/`, which is what deploys. A second copy here would drift. The teacher guide in `03-CURRICULUM/teaching-guide/` is the source they are written from. Revisit if Swarit wants them readable in Obsidian.

## gstack in every cloud session
**Installed by hand in the 2026-10-15 session.** Cloud sessions start fresh, so it disappears. To keep it, Swarit pastes this into the cloud environment's Setup script (environment menu in the session title bar, then Edit):
```
[ -d ~/.claude/skills/gstack ] || git clone --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup --no-browser -q
```
On his laptop, the same without `--no-browser`.
