---
status: draft v0, for Swarit's review
project: 02-PROJECTS/progress-database
date: 2026-10-15
---
# Student platform PRD (v0 draft)

_Swarit's vision from 15 Oct, shaped into a spec. Items marked **Decide** need his call. Nothing is built yet._

## 1. The one-line goal
A student signs in, sees their week, and always knows the one next step. They learn from short resources, build up to each assignment in small tasks, earn rewards, spend them on hints when stuck, and submit in the same place. Swarit sees every student's progress and reviews work from one screen.

North Star check: every feature below either helps a child understand why the robot works, or keeps them working on it.

## 2. Who uses it
| Who | Needs |
|---|---|
| Student (grades 6 to 12, laptop) | The next step, resources, tasks, hints, submit, see progress |
| Parent (same sign-in as the child) | See progress and feedback. Nothing else |
| Swarit (admin) | Every student's progress, a review queue, grant rewards, a class board for live classes |
| Mentors (later) | Review their own students only. Not in v1 |

## 3. The student journey
1. **Sign in** with the emailed code. Header shows their name ("Hi Aarav") and their reward balance.
2. **Home:** the current week at the top. One highlighted line: the next step ("Read: Why P overshoots"). Below it, the week's progress (resources 3 of 5, tasks 1 of 4) and the contents of all 12 weeks.
3. **Week page:** the driving question, then two lists:
   - **Resources** (articles with diagrams, videos, or both). Each opens its own page.
   - **Tasks**, in order. The assignment is broken into small steps that build on each other.
4. **Resource page:** a short article, diagrams and/or a video. Ends with a **checkpoint**: 1 or 2 quick questions. Answer correctly, earn rewards, resource marked done.
5. **Task page:** what to do, the fill-in template, the hints, and the submit box.
6. **Hints:** each task has up to 3 hints, from a nudge to almost the answer. Each costs rewards. Opening one is permanent.
7. **Submit:** paste text or code, add a link (video, photo, Drive), press submit. The next task unlocks at once.
8. **Feedback:** Swarit marks it Done or Redo with a comment. Done earns rewards. Redo shows the comment and lets them resubmit.
9. **My progress page:** balance, week-by-week check marks, robot milestones reached, all feedback.

## 4. Rewards: how the economy works
Proposed currency name: **Gears** (robot theme). **Decide** the name.

| Action | Gears (starting values, all in one config file) |
|---|---|
| Resource done (checkpoint answered) | +5 |
| Task submitted | +5 |
| Task marked Done | +10 |
| Stretch or Bonus task Done | +20 |
| Submitted before the Saturday 8 PM ET deadline | +5 |
| Hint 1 (a nudge) | -3 |
| Hint 2 (the approach) | -5 |
| Hint 3 (nearly the answer) | -8 |
| Gift from Swarit (any reason) | any |

Rules that keep it fair:
- Each resource and each task pays out once. Re-reading never farms Gears.
- Gears never affect the review. A task done with all 3 hints is still Done.
- The balance can't go below zero.
- **Safety valve:** a kid who is struggling most has the fewest Gears and needs hints most. So hints for a week become free once that week's solutions open (the Saturday after class), and Swarit can gift Gears.

## 5. My recommendations (where I'd shape your idea)
1. **Prove resource completion with a checkpoint question, not a "Mark as done" button.** A button gets clicked without reading. One question checks they read it and fixes the idea in their head. It also stops Gear farming.
2. **Unlock the next task on submit, not on approval.** Your review takes up to 48 hours. A kid shouldn't sit blocked waiting for it.
3. **Resources first, but softly.** Tasks show from the start. The highlighted "next step" points to unread resources first. A hard lock would stop the fast kid who already knows the topic.
4. **Submissions inside the site (decides your open question).** One text box (code is text, so `.ino` files paste straight in) plus one link field (YouTube unlisted or Google Drive for videos and photos). Why: every submission sits next to its task, in one review queue, linked to the right child. WhatsApp, Drive folders and Google Forms all make you match files to kids by hand. No file uploads in v1, which keeps storage, cost and risk at zero. Add uploads later if links prove annoying.
5. **Class board for live classes: celebrate, never rank the bottom.** These are 11 to 17 year olds and parents are in the WhatsApp group. Show the class's robot milestones ("6 robots stood for 30 s"), each kid's check marks by first name, and this week's top three. Never show who is last or who spent Gears on hints. **Decide.**
6. **Parents use the child's view.** Their email already maps to the child. No separate parent product.
7. **Keep writing content in Markdown in the repo.** You already work that way, and it costs build minutes only when content is pushed. Batch a week's content into one push.

## 6. Admin (Swarit)
- **Roster:** every student in a table: current week, resources done, tasks done, Gears, last active, waiting reviews. Sort by "needs attention" (behind, inactive 3+ days, Redo not resubmitted).
- **Review queue:** oldest first, so the 48-hour rule is visible. Open a submission, see the task, mark Done or Redo, write a comment, next.
- **Student detail:** everything one student did, all feedback, Gear history, gift Gears.
- **Class board:** full-screen view to share in Meet. First names only. No emails, no feedback text, no Gear spend.
- **Cohort switch:** founding and winter.

## 7. Content model (how you write a week)
```
content/weeks/week-08/
  index.md                    driving question, intro, order of resources and tasks
  resources/
    01-feedback-control.md    article + diagrams; front matter: title, type, minutes, checkpoint
    02-p-only-demo.md         a video page
  tasks/
    01-fill-the-error.md      steps, template, front matter: points, kind (must/stretch/bonus)
    02-p-only-runs.md
  private/                    never copied to the public site
    hints.md                  hints per task, in order
    answers.md                checkpoint answers
  solutions/                  opens the Saturday after class (as today)
  img/
```
Effort warning: **content is the real bottleneck, not code.** Each week needs about 3 to 5 resources, 3 to 6 small tasks, 2 to 3 hints per task and a checkpoint per resource. The teaching guide already holds most of the material. Week 1 and 2 must be ready by 9 Nov; later weeks can be written a week ahead.

## 8. Security (every angle)
| Threat | Defence |
|---|---|
| Someone not enrolled gets in | Cloudflare Access emailed code at the edge, then the Worker verifies the Access token signature, issuer and expiry on **every** request, pages and API alike (already built, 27 tests) |
| A student sees another student's work | The server takes identity only from the verified token, never from the URL or the request. Every query is filtered by that student. Tests for each endpoint |
| A student reads hints or answers early | Hints, checkpoint answers and solutions are **never in the public files**. Hints and answers are bundled inside the Worker code and sent one at a time, only after a valid unlock. Solutions stay date-locked |
| Viewing the page source or network tab | Only what that student has unlocked is ever sent. Nothing hidden with CSS or JavaScript |
| Faking Gears (calling the API by hand) | All Gears math happens on the server. A ledger with "pays once" rules enforced by the database. Hint purchase checks the balance and records the spend in one step |
| Access to GitHub | Repo stays private. Students never get GitHub accounts or links. No source maps. The build copies only public output |
| A student types code or HTML into a submission | Everything shown is escaped. Strict content security headers |
| Requests forged from another site | Write requests must come from the site itself (origin check) and be JSON |
| Shared family laptop | A visible "Sign out" link |
| Preview links leak real data | Previews sign everyone in as admin, so they must **never** connect to the real database. Previews use sample data only |
| Notes about minors in logs | Logs never record submission text, comments or emails |
| Losing data | Cloudflare's database has point-in-time restore. Weekly export as a backup |
| Children under 13 | US law (COPPA) has rules for collecting data from under-13s online. Collect the least we can and get a parent's consent at admission (add to the terms page). **Check with a lawyer**, this is not legal advice |

## 9. Tech plan (fits the current site)
- **Keep:** Cloudflare Worker, Access sign-in, Markdown content, the notebook design.
- **Add:** Cloudflare **D1** (a small SQL database) on the free plan: 5 GB, plenty for 20 students.
- **No R2 file storage in v1** (submissions are text and links), so no card or storage setup.
- **Tables:** `resource_done`, `gears_ledger`, `hint_unlocks`, `submissions`, `reviews`. Students and admins stay in `students.json` and `site.json` as today.
- **API (all behind the Worker guard):** `GET /api/me`, `GET /api/week/:n`, `POST /api/checkpoint`, `POST /api/hint`, `POST /api/submit`, and admin `GET /api/admin/roster`, `GET /api/admin/queue`, `POST /api/admin/review`, `POST /api/admin/gift`.
- **One-time setup by Swarit:** create the D1 database in his Cloudflare account (one command or a few clicks). I'll give exact steps.
- **Testing:** every rule gets a test. Local runs simulate the database, so I can build and screenshot without his account.

## 10. Timeline (founding cohort: week 1 opens Mon 9 Nov)
| By | What |
|---|---|
| 18 Oct | PRD agreed. Week 1 rewritten in the new format as the sample |
| 29 Oct | Built on `feature/student-platform`, all tests green, local previews |
| 4 Nov | Swarit tests with his own account and a test student |
| 6 Nov | Merge `redesign` + platform into `main`, one push |
| 8 Nov | Weeks 1 and 2 content live |
| Later | Class board polish, streaks and badges, uploads if needed, mentor reviewers |

## 11. Out of scope for v1
File uploads · mentor accounts · email or WhatsApp notifications · streaks and badges · certificates · editing content from the browser.

## 12. Decisions needed from Swarit
1. Currency name: Gears?
2. Checkpoint question to finish a resource (recommended), or a "Mark as done" button?
3. Submissions inside the site, text + link (recommended)?
4. Class board: milestones and top three, never the bottom (recommended)?
5. Starting Gear values in section 4: OK to start with these and tune?
6. Hints free once solutions open: yes?
