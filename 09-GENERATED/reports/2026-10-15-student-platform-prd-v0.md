---
status: draft v1, for Swarit's review
project: 02-PROJECTS/progress-database
date: 2026-10-15
---
# Student platform PRD (draft v1)

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
4. **Resource page:** a short article, diagrams and/or a video. Every resource ends with a **quick quiz** of 2 or 3 questions, videos included (decided 2026-10-15). There is no "Mark as done" button. Pass the quiz, earn rewards, resource marked done. A wrong answer shows a short "look again at..." pointer and lets them retry.
5. **Task page:** what to do, the fill-in template, the hints, and the submit box.
6. **Hints:** each task has up to 3 hints, from a nudge to almost the answer. Each costs rewards. Opening one is permanent.
7. **Submit:** paste text or code, add a link (video, photo, Drive), press submit. The next task unlocks at once.
8. **Feedback:** Swarit marks it Done or Redo with a comment. Done earns rewards. Redo shows the comment and lets them resubmit.
9. **My progress page:** balance, week-by-week check marks, robot milestones reached, all feedback.

## 4. Rewards: how the economy works
**Name: to decide.** Gears is the fallback. Shortlist:

| Name | Why it could work | Watch out |
|---|---|---|
| **Volts** | The robot runs on its battery; earning charges you up, a hint drains a little. The balance can show as a battery meter | None real |
| **Sterlings** | "Sterling" is already a currency word (pound sterling), so the brand name doubles as the money. Parents get the pun | Can sound like real money next to the $600 fee |
| **Bolts** | Robot parts, short, fun to say | Generic |
| **Gyros** | The motion sensor at the heart of balancing; kids learn it in week 5 | Also a sandwich, kids will joke |
| **Gears** | Clear robot theme | Common in other kids' apps |

Recommendation: **Volts**, shown as a battery meter. A 12-year-old understands it at once and it ties to the robot.

"Starting values" means the numbers below: how many points each action earns or costs. We start with these, watch how kids use them in weeks 1 and 2, then adjust. The numbers live in one settings file, so changing them is a one-line edit.

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
- **Safety valve:** a kid who is struggling most has the fewest Gears and needs hints most. So hints for a week become free once that week's solutions open (the Saturday after class, **decided 2026-10-15**), and Swarit can gift Gears.

## 5. My recommendations (where I'd shape your idea)
1. **Prove resource completion with a quick quiz, not a "Mark as done" button. Decided 2026-10-15, for videos too.** A button gets clicked without reading. One question checks they read it and fixes the idea in their head. It also stops Gear farming.
2. **Unlock the next task on submit, not on approval.** Your review takes up to 48 hours. A kid shouldn't sit blocked waiting for it.
3. **Resources first, but softly.** Tasks show from the start. The highlighted "next step" points to unread resources first. A hard lock would stop the fast kid who already knows the topic.
4. **Submissions inside the site. Decided 2026-10-15.** One text box (code is text, so `.ino` files paste straight in) plus one link field (YouTube unlisted or Google Drive for videos and photos). Why: every submission sits next to its task, in one review queue, linked to the right child. WhatsApp, Drive folders and Google Forms all make you match files to kids by hand. No file uploads in v1, which keeps storage, cost and risk at zero. Add uploads later if links prove annoying.
5. **Class board for live classes: celebrate, never rank the bottom. Agreed 2026-10-15.** These are 11 to 17 year olds and parents are in the WhatsApp group. Show the class's robot milestones ("6 robots stood for 30 s"), each kid's check marks by first name, and this week's top three. Never show who is last or who spent Gears on hints. **Cost: $0.** It is one more page reading the same database. No extra server, no extra service.
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

## 8. Publishing without weekly work (automation)

Goal (Swarit, 15 Oct): new resources and tasks appear each week without him writing or pushing anything.

How it works:
1. **Write all 12 weeks before launch, once.** Claude drafts every week in the new format (resources, quizzes, tasks, hints, answers) from the teaching guide in the vault. Swarit reviews in a preview and asks for changes. One push to `main` before 9 Nov.
2. **The calendar publishes, not a person.** The site already releases each week on the Monday before its class, and solutions on the Saturday after. Hints turn free at the same moment. All 12 weeks sit in the site, locked, and open by themselves. No push.
3. **Weekly bits go through an admin page, not code.** Things that only exist after class (recording link), extra videos, a note to the class, class time and Meet link, and gifting Volts: Swarit pastes them into a form on the admin page. Saved in the database, live at once, no push, no build minutes.
4. **Adding a family from the admin page.** The roster moves from `students.json` into the database. With a Cloudflare API key stored as a secret on the Worker, the same form also adds their emails to the Access sign-in list. Then a new family takes one form, no dashboard visits. (v1.1, after launch, if the key setup is acceptable.)
5. **Fixes during the course.** Swarit tells Claude what to change ("week 6 task 2 is unclear"). Claude edits on the branch, checks it, and batches changes into one push a week at most.
6. **Later, optional:** a weekly Claude routine that reads next week's content each Thursday and drafts improvements for Swarit to approve. Not now (routines are parked).

Swarit's weekly job becomes: teach the class, paste the recording link, review submissions.

## 9. Security (every angle)
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

## 10. Tech plan (fits the current site)
- **Keep:** Cloudflare Worker, Access sign-in, Markdown content, the notebook design.
- **Add:** Cloudflare **D1** (a small SQL database) on the free plan: 5 GB, plenty for 20 students.
- **No R2 file storage in v1** (submissions are text and links), so no card or storage setup.
- **Tables:** `resource_done`, `rewards_ledger`, `hint_unlocks`, `submissions`, `reviews`, `week_extras` (recording links, notes), `settings` (class time, Meet link). Admins stay in `site.json`. The roster moves to the database in v1.1.
- **API (all behind the Worker guard):** `GET /api/me`, `GET /api/week/:n`, `POST /api/checkpoint`, `POST /api/hint`, `POST /api/submit`, and admin `GET /api/admin/roster`, `GET /api/admin/queue`, `POST /api/admin/review`, `POST /api/admin/gift`, `POST /api/admin/week-extra`, `POST /api/admin/settings`.
- **One-time setup by Swarit:** create the D1 database in his Cloudflare account (one command or a few clicks). I'll give exact steps.
- **Testing:** every rule gets a test. Local runs simulate the database, so I can build and screenshot without his account.

## 11. Timeline (founding cohort: week 1 opens Mon 9 Nov)
| By | What |
|---|---|
| 18 Oct | PRD agreed. Week 1 rewritten in the new format as the sample |
| 25 Oct | All 12 weeks drafted in the new format, Swarit reviewing |
| 29 Oct | Built on `feature/student-platform`, all tests green, local previews |
| 4 Nov | Swarit tests with his own account and a test student |
| 6 Nov | Merge `redesign` + platform into `main`, one push |
| 8 Nov | Weeks 1 and 2 content live |
| Later | Class board polish, streaks and badges, uploads if needed, mentor reviewers |

## 12. Out of scope for v1
File uploads · mentor accounts · email or WhatsApp notifications · streaks and badges · certificates · editing full lessons from the browser (short weekly extras are in, see section 8) · adding families from the admin page (v1.1).

## 13. Decisions

| # | Question | Answer |
|---|---|---|
| 1 | Currency name | **Open.** Shortlist in section 4, recommendation Volts |
| 2 | Quiz to finish a resource | **Yes, for every resource, videos too** (15 Oct) |
| 3 | Submissions inside the site, text + link | **Yes** (15 Oct) |
| 4 | Class board, celebrate, never rank the bottom | **Yes, if cheap.** It costs $0 (15 Oct) |
| 5 | Starting reward values | Explained in section 4. **Open:** OK to start with these? |
| 6 | Hints free once solutions open | **Yes** (15 Oct) |
| 7 | Weekly publishing automated | **Yes** (15 Oct). Plan in section 8 |

## Change log
- 2026-10-15 v0: first draft from Swarit's vision.
- 2026-10-15 v1: Swarit's answers; quiz for every resource; class board cost; reward values explained; currency shortlist; new section 8 on publishing without weekly work.
