# Student platform (progress, rewards, submissions)

**PRD draft:** `09-GENERATED/reports/2026-10-15-student-platform-prd-v0.md`

## Brief
Give each child a record on the course site: tasks per week, submissions inside the site, Swarit's review, and check marks that show progress. Replaces submitting on WhatsApp or a form.

## Status
**Spec.** PRD v0 drafted 2026-10-15, waiting on Swarit's 6 decisions (section 12). No code yet.

## Code
Not started. Will live on `feature/student-platform`, branched off `redesign`. Never on `main` until approved.

## Swarit's vision (15 Oct 2026, second message)
- Child signs in, sees the current week at the top. Minimal, smooth, the eye is drawn subtly to what matters.
- Each week lists resources (blog, diagrams, video). Each opens its own page.
- Completing a resource earns rewards.
- Each assignment is broken into many small tasks that build slowly.
- Each task has hints. Opening a hint costs rewards (for example 20 earned, a hint costs 5).
- Student dashboard; also shown in live classes to keep kids engaged.
- Easy submission (WhatsApp, Drive, link or form were options; still open).
- Admin dashboards: every student's progress and their submissions.
- Each student sees only their own progress, with their name on the page.
- Super secure: no answers early, no GitHub access, no other students' data.

## Swarit's ask (15 Oct 2026, first message)
"I want database integrated, a few things for that is being saved for each child, like doing multiple tasks, etc. And giving them assignments in that way only, and they can submit it and uh, they should get a evaluator or a check mark that this much progress they have made till now." Content changes are also coming.

## What we already know (from the teaching guide and the site)
- Each week has 2 to 6 tasks marked Must, Stretch, Optional or Bonus.
- Assignments are due **Saturday 8 PM ET**.
- Review rule: **mark each Must task Done or Redo within 48 hours.** Deeper feedback goes in the 1:1.
- Late work: catch up in the 1:1, no penalty. **Week 11 is the hard deadline.**
- Submission types: code as `.ino` named like `W05_AnyaS.ino`; readings pasted as text in a given format; videos from the phone, landscape, under 60 seconds, whole robot in frame.
- Fill-in tables are already code blocks with a copy button on the week pages.
- Files up to 25 MB. Videos go to YouTube, never the repo.
- The teaching guide planned Google Classroom for posting and collecting work. The site replaces that.

## Constraints
- Keep Cloudflare Access sign-in. Students see only their own data. Admins see all.
- Stay on Cloudflare's free plan if possible. Likely D1 (database) and R2 (file storage), both on the current Worker.
- No notes about minors in logs.
- Must not break the 27 existing checks. Add tests for every new rule.
- Build minutes are limited: test with previews, merge in one push.

## Open questions for the PRD
1. Who marks a task done: only Swarit, or some automatic (for example, a file uploaded)?
2. Do parents see progress? Same view as the child, or a summary?
3. File types and size limits per task (`.ino`, photos, short video, text)?
4. Deadlines: shown only, or late flags? What happens after week 11?
5. Does Done or Redo carry a comment? Does the child get notified (email, WhatsApp, on the site only)?
6. Is there a score, or only Done / Redo / Not submitted?
7. Mentors: will they review too, and see only their students?
8. Does the 1:1 booking and its notes live in the same record?

## Milestones
- [ ] PRD agreed with Swarit
- [ ] Data model and storage choice
- [ ] Build on a feature branch with tests
- [ ] Preview and review
- [ ] Merge with the redesign in one push

## Next action
- Swarit answers the 6 decisions in the PRD. Then week 1 is rewritten in the new format as the sample.
