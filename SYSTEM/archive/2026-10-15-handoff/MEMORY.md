# Sterling Robotics Academy: project memory

Last updated 15 Oct 2026. Written for a fresh Claude Code session so it can pick up the work without the old chat.
Owner: Swarit Bhardwaj (swarit000@gmail.com, based in India, teaches US families).

Read this file first. Then `site/CLAUDE.md`, `site/DESIGN.md` and `site/PRODUCT.md` before touching the course site.

---

## 1. Hard rules (read before doing anything)

1. **Never push to `main` without Swarit's explicit approval.** Every push to `main` triggers a Cloudflare Workers Build, and build minutes are limited each month. Work on a branch. Batch changes. Merge in one push only when he says so.
2. **Previews never go to `main`.** Use `npx wrangler deploy -c wrangler.preview.jsonc --temporary` (no login, live 60 minutes, no build minutes). If that is blocked, publish the `preview/` build somewhere private.
3. Run `npm run build && npm test` before any push. All checks must pass (27 today).
4. Student pages hold notes about minors. Never print them in logs, commit messages, or anywhere public.
5. No secrets in the repo. Access settings live in `wrangler.jsonc` vars (the team domain is not a secret) or Cloudflare variables.
6. Do not probe the live site with curl. Swarit rejected that once.
7. Writing style everywhere (site, messages, docs, replies): plain, short sentences, no em dashes, no AI slop, light mode. Lead with the point. No words like delve, leverage, robust. No "not X, it's Y" lines.
8. When you change something, summarise each change individually. When you share several files or pages, say which is which, what it is for, and why it exists.
9. Visually check every design change (screenshots on laptop and phone) before saying it is done. He asked to "cross verify every time".

---

## 2. The business

- **What it is:** a 12-week live online robotics course. Each child builds the Elegoo Tumbller self-balancing robot at home and writes the code that keeps it standing and recovering from pushes.
  - No encoders, no speed loop, no sensor fusion with the ultrasonic. Ultrasonic and Bluetooth are optional extras.
- **Who for:** grades 6 to 12, mostly Indian-origin families in the US. Reach also goes through relatives and friends in Canada and Dubai (watch kit shipping and Sunday time zones there).
- **Tagline:** "Most kids follow the instructions. Yours will understand why they work."
- **Teaching approach:** inquiry-based. Each week opens with a question about a real physical problem, explored by hand before theory or code.
- **Price:** $600 total, robot kit included ("about $50 a week"). Includes the kit delivered, 12 live classes, a weekly 1:1, all recordings, demo day and a certificate.
- **Payment flow:** free entry test first. Once admitted, $150 to reserve (counts toward the $600). The $450 balance is due a week before class one, then the kit ships. "You pay nothing until your child is admitted."
  - Payment portal: the Infinity app. The payment link is not set yet. KYC for an international bank account is in progress (Oct 2026). Suggested: ask a CA about a GST LUT (avoids 18% IGST on export of services) and keep a FIRA per foreign payment.
- **Refunds:** full refund before the enrolment deadline, $75 back before kits ship, no refund after kits ship.
- **Referral:** $50 + $50. The referred family gets $50 off and the referrer gets $50 once the child is admitted.
- **Cohorts:**
  - **Founding:** first class Sunday 15 Nov 2026. Enrolment closes 1 Nov. Balance due and kit ships 8 Nov. Demo day 31 Jan 2027. No breaks for November or Thanksgiving.
  - **Winter:** first class Sunday 10 Jan 2027. Enrolment closes 20 Dec. Balance due 3 Jan. Demo day 28 Mar 2027.
- **Seats:** do not state a number. Since 15 Oct the wording is "Limited seats only". (Earlier versions said 10 seats for the founding cohort. 50 and 60 were removed even earlier.) Swarit will launch even with two students; the target is 10.
- **Weekly format:** one live class every Sunday (60 to 90 minutes; the teaching guide allows 40 to 90), a 30-minute 1:1 with Swarit or a mentor he trains, 1 to 4 hours of tasks, a class WhatsApp group with parents, every class recorded. Class times are **not promised yet** ("Every Sunday, at a time confirmed before class one"). A suggested slot was 11am Eastern (8am Pacific), not confirmed.
- **Mentors:** mentors from TUM, CMU and IITs are planned but unconfirmed. Never name them.
- **Kit:** Elegoo Tumbller, delivered before week 2 (must arrive before 22 Nov for the founding cohort). The child keeps it. Parts list used in the brochure: control board (the brain), ultrasonic (sees ahead), motion sensor (feels tilt), geared motors (drive it), chassis plates, wheels, rechargeable battery pack, standoffs and tools. Sourcing plan not final (Elegoo US or Amazon US, shipped after the balance is paid).
- **Contact:**
  - WhatsApp (US): +1 754 279 2415. The India number must never appear in parent materials.
  - WhatsApp Business short link (every CTA uses it): https://wa.me/message/O2K3UG6UWJEBJ1
  - Public email since 15 Oct: **hellosterlingrobotics@gmail.com** (the brochure uses it). The course site still shows swarit000@gmail.com in `content/site.json` `email`; ask Swarit before changing it. Admin sign-in stays swarit000@gmail.com.
  - Booking calendar link for entry tests: not provided yet.
- **Distribution:** the brochure is shared as a PDF on WhatsApp, mostly through referrals. Send the message with the link first, then the PDF: links inside PDFs are not tappable in Samsung's viewer, but links in WhatsApp chats always work.

### Mentor claims

Allowed (exact brochure wording):
- "Taught by Swarit Bhardwaj, former robotics researcher at IIT Bombay."
- Industry: autonomous vehicles, Swaayatt Robots.
- Gold medalist, IndiaSkills Mechatronics (never add "State").
- Gold medalist, Mechatronics Engineering (university).
- Postgraduate studies, LaunchPilot Singapore.
- 100+ students taught, 1,000+ hours of teaching, 3 years, "the US and India" (that order).
- Logos: IIT Bombay, Swaayatt Robots, the full LaunchPilot wordmark.

Not allowed: MBA, "business school", master's; "LaunchPilot Singapore" text in the logo row; "India and the US"; unconfirmed mentor universities; promised class times; invented testimonials or photos.

---

## 3. What exists and where

| Thing | Where | Status |
|---|---|---|
| Course website code + content | `site/` (git repo, branch `redesign` checked out) | Live on `main`; redesign waiting for approval |
| Brochure (8-page A4) | `reference/brochure/` | Current. PDF regenerated 15 Oct |
| Entry test (slides + grader) | `reference/entry-test/` | Working, in use |
| Teaching guide (12 weekly lesson plans) | `reference/teaching-guide/sterling-teaching-guide.html` | Reference for writing week pages |
| GitHub repo | https://github.com/SwaritBhardwaj/Sterling-Robotics-Academy (private) | `main` deploys the live site |
| Live site | https://academy.sterlingrobotics.workers.dev | Sign-in by emailed code |

Claude artifacts (private, on claude.ai, Swarit's account):
- Brochure: https://claude.ai/artifact/Q9fNLPL7SbDxC75f2SAJut (v23, 15 Oct: limited seats, new email)
- Entry test: https://claude.ai/artifact/P6tyeW61bCXgLd8hDTSLMU (v8, slides + grader, saves to the artifact database and Google Sheets)
- Teaching guide: https://claude.ai/artifact/4CNP5VB8fC8kFUujdU56ZX
- Site redesign preview: https://claude.ai/artifact/RMtiqvR8evo1BJu66egK5e
- Old, do not use: Graphite edition 7PsC56C75inX8hjhT9NgwQ, Swiss edition 6wAJUgBMxSafwiEb5pxHoU, brochure rebuild 1g3BwDavsKFRytEU2w1ebM, old brochure QnuJoNBfbtxBva4tK9kDJR, cover page 47EheLfT5o4DWFg5aR41Gd, cover options 6udqnXGXPmoZkV8WfPRHtz, standalone test slides 6L3EuGAKC7LeWm9vAfdCpd.

Google Drive: folder "Sterling Entry Tests" (https://drive.google.com/drive/folders/1eNm7EW-4b8BPIHc2K0IOIVtLC7drGqxV) holds the entry-test results Sheet. The Sheet is rebuilt on every sync, so always open the folder.

---

## 4. Course website

### Why our own site
For 2 to 10 students, course platforms cost $50 to $100 a month or take a 10% cut, and many assume adult or school accounts (awkward for under-13s). Checked: Thinkific (no free plan, $54/mo, live cohorts $109/mo), Skool ($9/mo + 10% or $99/mo), GitHub Classroom (shut down 28 Aug 2026), Canvas Free-for-Teacher (clunky), Google Classroom (free, but students need Google accounts), Moodle (self-host). Swarit chose to build his own.

### Hosting decisions
- No custom domain for now (about $10 a year, can come later).
- **Cloudflare**, because it is the only free host with a login gate: Cloudflare Access emailed one-time PIN, free up to 50 users. Vercel Hobby is non-commercial and its password protection costs $20/project/month on Pro. GitHub Pages is public even from a private repo.
- Content lives in the **private** GitHub repo. Two layers of privacy: the private repo hides the files, Access hides the live site.
- Built first for Cloudflare Pages, then converted to **Cloudflare Workers with Static Assets** (`run_worker_first: true`), because the Workers "Import a repository" flow ignores Pages Functions.
- Workers Builds deploys from `main`: build `npm run build`, deploy `npx wrangler deploy`, preview builds off.
- Weekly resources are updated by pushing Markdown and files to the repo. Every push costs build minutes, so batch them.

### Cloudflare setup as finally done
1. Workers & Pages > Create > Import a repository > this repo, Worker name `academy` (must match `name` in `wrangler.jsonc`). Workers cannot be renamed; the first Worker was `sterling-robotics-academy`, so a new one called `academy` was created.
2. Cloudflare One (Zero Trust) > Integrations > Identity providers > **One-time PIN**.
3. Reusable Access policy **"Class families"**: Allow, Include **Emails** (every enrolled parent and student email, plus admins).
4. Zero Trust > Access controls > Applications > Add > **Self-hosted**, hostname `academy.sterlingrobotics.workers.dev`, policy "Class families", login method One-time PIN only. The login page was customised.
5. Team domain **sterlingroboticsacademy.cloudflareaccess.com**, set in `wrangler.jsonc` `vars.ACCESS_TEAM_DOMAIN` with `"keep_vars": true`. `ACCESS_AUD` is optional.
6. Test in a private window: admin email works, an unknown email is refused.

To add a family: add their emails to the "Class families" policy **and** to `content/students/students.json`.

### Problems hit and fixes (so they are not repeated)
| Problem | Fix |
|---|---|
| Pages Functions skipped by the Workers import | Converted to a Worker with `run_worker_first` |
| Access AUD tag hard to find | Made `ACCESS_AUD` optional; the team domain is enough |
| Worker-level Access only offered "email domain" or "Cloudflare account" | Made the reusable "Class families" email policy, then a self-hosted Access app on the hostname |
| One-time code emails not arriving | Policy mismatch; fixed by the self-hosted app with the email policy |
| "Almost ready" page after login | A Git deploy wiped the dashboard variable. Vars now live in `wrangler.jsonc` with `keep_vars: true` |
| No rename option for Workers | New Worker `academy` |
| Temporary Wrangler deploy from the Claude cloud workspace | Blocked by its network proxy (api.cloudflare.com). Works from Swarit's laptop |

### How the code works
- `content/`: the only place course material lives. Markdown with a small `---` header.
  - `weeks/week-NN/index.md` (+ files, `img/` for diagrams, `solutions/`), `resources/`, `students/students.json` + `students/<slug>.md`.
  - `site.json` (links, admins, email), `schedule.json` (cohort dates, unlock rules).
- `build/build.mjs`: content to `dist/`. `PREVIEW=1` writes `preview/` with relative links and sample data.
- `build/test.mjs`: 27 checks (locked weeks, other students' pages, unknown emails, expired/tampered/faked tokens, worker serving pages and `/api/me`).
- `worker/index.js` runs first and calls `lib/guard.js`: verifies the Access JWT (team domain issuer, signature from `/cdn-cgi/access/certs`, expiry, optional AUD), checks the email against students and admins, locks weeks and solutions by date, keeps student pages private. `lib/me.js` serves `/api/me` (name, cohort, dates, which weeks are open, the week question).
- `assets/site.css` and `assets/app.js`: the look and the signed-in bits (dates, locks, home page, submit links, copy buttons).
- Schedule: a week opens 6 days before its class (the Monday before; founding week 1 opens 9 Nov). Solutions open 6 days after class (the Saturday after). Times use US Eastern (-05:00).
- Admins (swarit000@gmail.com) see every week and every student page at any time.
- `DEV_EMAIL` is for local and temporary previews only. Never set it on the live Worker.

### Week page format (Markdown)
- First line after the header: `> the driving question` (shown big under the title).
- Sections: "By the end of this week", "Have ready for class", "Assignment" (`### Must: ...`, `### Stretch: ...`, `### Optional: ...`, `### Bonus: ...`), "Before you submit, check", "Resources".
- Fill-in templates go in code blocks (they get a copy button).
- `==text==` highlights. A lone image line becomes a taped-in figure (alt text = caption); keep images in the week's `img/` folder so they are not listed under Files. A lone YouTube link becomes an embedded video.
- Header fields: `title`, `short`, `kit`, `recording` (unlisted YouTube link after class), `slides`.
- Week content was written for students from the teaching guide. Teacher-only notes stay out.

### The 12 weeks (site title | driving question | kit)
1. Why is balancing hard? | How do you keep something standing that wants to fall? | No kit (broom balance, phyphox, Wokwi)
2. Build the robot | What does each part of the robot do in the sense, decide, act loop? | Kit
3. Statements, variables and conditions | How does a robot decide what to do? | Laptop only
4. Loops, the Serial Monitor and debugging | How do we see what the robot is thinking, and fix it when it is wrong? | Kit
5. Inside the motion sensor | How does a chip smaller than a fingernail feel tilt and turning? | Kit
6. A clean tilt angle, and how distance is measured | How can the robot know its exact tilt when one sensor jitters and the other drifts? | Kit
7. Actuators: PWM and the motor driver | A pin can only be on or off. How does the Arduino make a motor go slowly? | Kit
8. Control: P and D | How hard should the wheels push, and when? | Kit
9. Balance point, safety cut-off and I | Why does my robot keep running off in one direction? | Kit
10. Push recovery: tuning and debugging | How do we make it stand back up after a push? | Kit
11. Submission week | Can I explain every line of what my robot is doing? | Kit
12. Iterate, final video and demo day | What can you show, and explain, to someone who has never seen this before? | Kit

Parent-facing names used in the brochure: Why things fall, Build the robot, First real code, Make it talk back, The robot's inner ear, Which way is up, Wheels that obey, How drones stay steady, Standing tall, Bounce back, Finish line, Demo day.

Coding weeks come before kit-heavy weeks because kits may arrive late. Control is P+D in week 8; balance point, cut-off, dead zone and I in week 9; push recovery in week 10.

### Git history
`main`: 94d4710 initial site, bc0e0eb run as a Worker, 7697112 Access tag optional, 4577f15 rename Worker to academy, d8431fb keep the sign-in setting.
`redesign` (local only, in this zip, **not pushed**): d75389b notebook redesign.

---

## 5. The redesign: "Mentor's notebook" (branch `redesign`)

Swarit's brief (14 Oct): "a paper feeling attached to it with important things highlighted with a highlighter design, and it should feel very organic, very much like it's a real paper, and we are gonna add in diagrams, videos, etc." Then: "end-to-end, the website should be minimal, should have a few animation, very smooth, it should feel very smooth, cohesive, should not be very much complicated for the students." Paper: "textured paper without any lines. Just a continue stretch of paper, not very modern, not very new kind of like a yellow." Main user: students on laptops. He picked the "Mentor's notebook" direction and asked for the impeccable design skill to be used throughout.

On 15 Oct he said: "I like the design." He has not yet said to merge it.

What was built (full detail in `site/DESIGN.md`):
- One unlined, slightly yellowed paper sheet (SVG noise texture, faint vignette). An early fibre layer made streaks that looked like lines, so it was removed.
- Yellow highlighter only for the one thing to do now, the current week, the current menu item, "must do" tags and `==text==`.
- Handwritten margin notes (big week number, next class date, cohort). Task tags sit in the margin.
- Taped-in figures, videos and code templates.
- Contents page with dotted leaders; locked weeks in pencil grey with their opening date.
- Two animations: a highlighter sweep on the to-do line, and a fade between pages. Both off under reduced motion.
- Restyled sign-in and lock message pages.
- A sample sense, decide, act diagram added to week 2, plus one `==highlight==`.
- `preview/` is git-ignored.

impeccable skill notes: PRODUCT.md and the surface brief `.impeccable/surfaces/assets-site-css.md` exist. The concept roll ran degraded (the impeccable server was unreachable). The detector flagged only Instrument Serif; it is kept because it is the brand font from the brochure.

To show Swarit a preview without build minutes, from his laptop or any machine that can reach Cloudflare:
```
cd site
npm install
npm run build
npx wrangler deploy -c wrangler.preview.jsonc --temporary
```
The preview Worker signs everyone in as swarit000@gmail.com (admin), so all weeks are open. The link lasts 60 minutes.

To merge (only when he says so): merge `redesign` into `main`, run `npm run build && npm test`, push once.

---

## 6. What Swarit wants next on the site (15 Oct, not started)

His words: "I want database integrated, a few things for that is being saved for each child, like doing multiple tasks, etc. And giving them assignments in that way only, and they can submit it and uh, they should get a evaluator or a check mark that this much progress they have made till now." He also has content changes coming.

So, to plan with him before building:
- A database with a record per child (likely Cloudflare D1 or KV, which fits the current Worker; keep it on the free plan).
- Assignments made of several tasks per week, each task tracked per child.
- Submission inside the site (links, photos, filled tables) instead of WhatsApp or a form. File uploads would need storage (Cloudflare R2) and a size limit.
- An evaluator view for Swarit (check, comment, mark done) and a progress view for the child and parent (check marks, "X of Y tasks done", per week and overall).
- Must keep: Access sign-in, students only see their own data, admins see all, no notes about minors in logs.
- Ask him about: who marks tasks done (him, or auto for some), whether parents see progress, file types and sizes, and whether submissions need deadlines.

---

## 7. Entry test (live 10-minute video call)

Why: admission and placement that a child cannot hand to AI. Checks what they have built, reasoning, physics and circuits. Experience alone does not decide it.

Format: video call only, no written test. Background answers come from the WhatsApp default message, but Part 1 still asks about builds on the call (Swarit asked for this).

Timing: Part 1 at 0:00 (2.5 min), Part 2 at 2:30 (2 min), Part 3 at 4:30 (2.5 min), Part 4 at 7:00 (2.5 min), wrap-up at 9:30.

Parts, each scored 0 to 3:
1. **What they have built.** "Tell me about something you built or made yourself." "Show it on camera." "What went wrong and how did you fix it?" "Have you written code? What did you make?" If Arduino: "What did you connect, and to which pin?" Rubric: 0 nothing; 1 kits, Lego or block code; 2 own build or text code and names a real fix; 3 working electronics or robot project explained in their own words.
2. **Thinking puzzles.** A robot path puzzle ("You are the robot...") and a number pattern, then "How did you get that?" Rubric: 0 neither even with a hint; 1 one with a hint; 2 both, or one unaided with clear reasoning; 3 both quickly with clear steps.
3. **Wheels and motion** (replaced a ruler-balancing question because it repeated week 1). Gear ratio turns and force, wheel distance per turn, a bonus. Rubric: 0 nothing sensible; 1 some right but guessing; 2 first two right with reasons; 3 bonus too with a reason.
4. **Circuits on paper.** Draw a circuit and hold it to the camera, a circuit question, a bonus. Rubric: 0 no closed loop even with help; 1 a working loop with help; 2 correct drawing plus the next question; 3 bonus too, with why.

Randomness: a 4-digit test code seeds the generator (`entry-gen.js`, `makeTest(code)`, mulberry32). Same code gives the same questions on slides and grader. "New test" makes a new code (siblings, retests).

Integrity: "Signs of outside help" ticks (eyes on another screen, long silence then a textbook answer, can't explain their own answer, whispering or typing off camera, words they can't explain). "Good signs" ticks for borderline calls.

Result bands (out of 12): 7+ Admit; 4 to 6 Admit with prep (Wokwi "Blink" task, about 30 min); 3 or less Not ready yet; 2+ outside-help ticks means Retest.

Architecture (Claude artifact, one page with two views):
- On the PC choose **Slides** and share only that window in Meet. On the phone choose **Grader**. The grader follows the live slide. The phone does not drive the slides (he said no to a remote).
- Each test saves on every tap to the artifact database (owner-only read and write). Past tests list, Settings (payment link, "send after a parent books" message).
- Google Sheets via the claude.ai Drive connector: on Finish or "Sync now" a fresh results Sheet is built in the "Sterling Entry Tests" folder and the old one is trashed. Columns: Date, Child, Parent, Grade, Cohort, Test code, Experience, Thinking, Physics, Circuits, Total, Result, Outside help, Good signs, Comment for parent, Private notes. CSV export too.
- "Finish and make report" makes a one-page PDF report (jsPDF) and the WhatsApp message for the parent.
- Signed out of Claude: the page says so and offers a test-code box to see answers, but saves nothing. Check the top bar says "Saved" after the first tap.
- Only one live test at a time.
- **Rejected:** a Google Apps Script version. "I do not want to create an app script for this... I'm fine with like signing in and then doing everything." It was deleted. Do not propose it again.
- Slides style (14 Oct, he said "PERFECT"): blueprint dot grid, part pills (01 You, 02 Puzzles, 03 Motion, 04 Circuits), a line-art swaying robot on the title slide.
- Advice still open: set the artifact to private so nobody can see the answers.

Files: `reference/entry-test/entry-app-src.html` + `entry-gen.js`, built by `python3 build.py` into `sterling-entry-test.html` (it replaces `/*__GEN__*/`). The live version runs as a Claude artifact because it uses artifact database and Drive capabilities. Outside claude.ai it shows the signed-out mode.

---

## 8. WhatsApp Business setup and messages

Set up by Swarit on 14 Oct ("I've set up the WhatsApp automation"). WhatsApp Business has no bots, so tests are booked through a calendar link sent with /book. Menus: Settings > Business tools > Greeting message / Quick replies / Short link > Default message.

Tone he wants: "gentle, polite, welcoming". Use his drafts as the base. Never say "reasoning test" (the test is only a 10-minute call).

**Greeting (final, his):**
```
Thanks for reaching out to Sterling Robotics Academy.

I'll reply within a few hours with a booking link for your child's free entry test: a 10-minute call.

If you haven't already, please share your name, your child's name, grade and city, and who referred you, if anyone.
```

**Default message on the short link (final, his format plus the referral line):**
```
Hi Swarit, I'd like to book the free Sterling entry test.
Parent name:
Child's name and grade:
City and state:
Cohort: November or January
Referred by (name or number, if anyone):
```

**/book** (needs the real booking link):
```
Thanks for waiting. Here's the link to book [Child]'s free entry test. It's a 10-minute video call with me, and you can pick any time that suits you:
[booking link]

If none of the times work, just reply here and I'll find one.
```

**/test** (needs the booking link):
```
The entry test is free. It's a 10-minute video call with me: a few puzzles, simple physics and circuits. It shows me how your child thinks, so I can make sure the course is the right level. No preparation needed.

Book a time here: [booking link]
```

**/fees:**
```
The course is $600 in total, robot kit included. That's about $50 a week.

• Entry test: free
• $150 to reserve a seat, only after your child is admitted. It counts toward the $600.
• $450 balance a week before class one. The kit ships after that.

Refunds: full refund before the enrolment deadline, $75 back before kits ship, no refund after kits ship.

If a family you refer joins, you each get $50.
```

**/dates** (updated 15 Oct to drop "10 seats"; Swarit must paste this into WhatsApp):
```
Two start dates. Seats are limited in both.

Founding cohort
Starts 15 Nov. Enrolment closes 1 Nov. Balance due 8 Nov. Demo day 31 Jan 2027.

Winter cohort
Starts 10 Jan. Enrolment closes 20 Dec. Balance due 3 Jan. Demo day 28 Mar 2027.

Both run for 12 Sundays with one live class each Sunday. I'll confirm the class time before class one.
```

**/week:**
```
Each week your child gets:
• One live class with me (60 to 90 minutes)
• A 30-minute 1:1 with me or a mentor I train
• Weekly tasks (1 to 4 hours)

Every class is recorded, and the robot is theirs to keep.
```

**After a parent books** (also in the grader Settings):
```
Hi [Parent], thanks for booking the entry test for [Child]. It's a 10-minute video call with me, and no preparation is needed.

Please have ready:
• A laptop or phone with a camera
• A pen and a few sheets of blank paper
• Anything [Child] has built (optional)

[Child] should sit at a desk alone with the camera on. You're welcome to stay nearby.
```

**Reminder on the day:**
```
Hi [Parent], a quick reminder that [Child]'s entry test is today at [time, time zone].

Here's the video call link: [Meet link]

Please have a pen and paper ready, with the camera on. See you soon.
```

**Result messages** (Admit, Admit with prep, Not ready yet) are generated by the grader with names, dates and the payment link filled in. They do not need to be quick replies.

### Referral messages (relatives and friends in the US, Canada, Dubai)
Swarit's direction: ask them to refer other families rather than to enroll their own kids. Send 1 or 2, then 3. "10 seats" was replaced with limited-seat wording on 15 Oct.

1. With reward:
```
Hi [Name], hope everyone at home is well.

I've started an online robotics course for kids in grades 6 to 12. Over 12 Sundays, each child builds a real self-balancing robot at home and codes it to stand on its own. I teach every live class. $600, robot kit included.

I need your help with one thing. You know far more families there than I do. If you know parents whose kids love building, coding or science, could you forward them the brochure and the message below?

For every family that joins through you, they save $50 and you get $50.

First batch starts 15 Nov and seats are limited. Second starts 10 Jan.
```
2. As a favour (close family):
```
Hi [Name], hope everyone at home is well.

I've started an online robotics course for kids in grades 6 to 12. Over 12 Sundays, each child builds a real self-balancing robot at home and codes it to stand on its own. I teach every live class.

I'd really value your help getting the word out. If you know parents whose kids love building, coding or science, could you forward them the brochure and the message below? Any family you send gets $50 off.

First batch starts 15 Nov and seats are limited. Second starts 10 Jan.

Thank you, this means a lot.
```
3. Ready to forward (put the relative's name in [Name] to track referrals):
```
Sharing this for parents of kids in grades 6 to 12.

Sterling Robotics Academy runs a 12-week live online course. Kids build a self-balancing robot at home and code it to stand and recover from pushes. Taught by Swarit Bhardwaj, former robotics researcher at IIT Bombay.

• $600, robot kit included
• Live class every Sunday
• Batches start 15 Nov and 10 Jan. Limited seats.
• Free entry test first. You pay only after admission.

Mention [Name] when you book to get $50 off.

Book the free test: https://wa.me/message/O2K3UG6UWJEBJ1
```
Current student's parent:
```
Hi [Name], hope you're doing well. [Child] has been doing really well in our sessions.

I'm starting a 12-week live online robotics course for kids in grades 6 to 12. Each child builds a self-balancing robot at home and writes the code that keeps it standing and recovering from pushes. I teach every live class. $600, robot kit included.

The founding batch starts 15 Nov and seats are limited. The next batch starts 10 Jan.

If you know parents whose kids would enjoy this, could you forward them the brochure? If they join, they save $50 and you get $50.

The entry test is free: https://wa.me/message/O2K3UG6UWJEBJ1
```
Reminder before 1 Nov:
```
Hi [Name], a quick reminder. Enrolment for the founding robotics batch closes on 1 Nov, and classes start 15 Nov. Seats are limited.

If [Child] wants to join, book the free entry test here: https://wa.me/message/O2K3UG6UWJEBJ1

The January batch is open too if November is too soon.
```

---

## 9. Brochure

- 8 A4 pages: Cover, The course, How it works, The kit, Your mentor, Cohorts, Admission, Questions.
- Look: light, Apple/B&O style. White, ink #1D1D1F, greys #86868B and #5E5E63, line #E2E2E6, panel #F5F5F7, one blue #1F55D6. Fonts Instrument Sans, Instrument Serif, Geist Mono. One blue pill button style. Design philosophy name: "Lucid Machinery".
- Every CTA links to https://wa.me/message/O2K3UG6UWJEBJ1. Page 8 also says "Button not opening? Save +1 754 279 2415 and send "Entry test" on WhatsApp."
- Decisions: no QR code, no India number, no header section numbers, no class times, no "reasoning test", big one-word page titles, parent-friendly week names, generous white space, readable on a phone but fonts "not too big".
- 15 Oct changes: founding cohort label "Limited seats only"; "A small class, so more questions get answered live."; email hellosterlingrobotics@gmail.com.
- A separate phone edition was made and **rejected** ("stick to the original layout"). Do not make one again.
- Weakest point: no testimonials or student photos yet. Swarit said they are coming. Never invent them.
- Files: `reference/brochure/brochure-src.html` (edit this), `assets/` (images, fonts, headshot source), `build.py` (builds the self-contained `sterling-brochure.html` and the PDF with its title metadata). Needs `pip install pillow playwright pypdf`.

---

## 10. Teaching guide

`reference/teaching-guide/sterling-teaching-guide.html`: 12 weeks of 5E inquiry lesson plans for Swarit (teacher-facing), with a short-class toggle and copy buttons. Each week has: driving question, goal, what students leave with, teacher prep, student prep, class flow, common misconceptions, tasks, checks, 1:1 focus, notes and resources. Week pages on the site were written from it in student language.

---

## 11. Launch checklist (status 15 Oct)

Done:
- Brochure (current, 15 Oct).
- WhatsApp greeting, default message and quick replies (set up by Swarit).
- Entry test and grader (working).
- Course site live with sign-in.
- Notebook redesign built and liked, not merged.

Before the first parent pays:
1. Payment link: finish KYC, paste the $150 link into the grader Settings, run a $1 test, decide how refunds are paid. **Pending.**
2. Booking calendar for 10-minute test slots in US evenings, then put it in /book and /test. **Pending.**
3. Terms page: refunds, consent to record classes, 1:1s with minors only with a parent's knowledge, WhatsApp group rules. **Not started.**
4. Tax and banking: GST LUT and FIRA. **Unknown.**

Before 1 Nov:
5. Fix the Sunday class time across US time zones. **Pending.**
6. Kit plan: sourcing, price check, shipping addresses collected at payment. **Pending.**
7. Weekly 1:1s: 10 students is 5 hours a week. Needs a 1:1 booking link. **Pending.**
8. Fill seats: send the referral messages; track leads (messaged, test booked, test done, admitted, paid). Lead tracker not built.
9. Trust: 2 or 3 testimonials and student photos. **Pending.**

Before 15 Nov:
10. Class setup: Google Meet (free Meet ends group calls at 60 minutes, so paid Workspace, Zoom Pro, or record with OBS), recordings, Drive folder, class WhatsApp group.
11. Site: fill `content/site.json` (classTime, meetLink, homeworkForm, oneOnOneLink are empty); add each family to `students.json` and the Access policy; remove the sample student; merge the redesign if approved. Until a homework form is set, Submit opens WhatsApp.

Can wait until December: certificate template, demo day plan, naming mentors.

---

## 12. How Swarit likes to work

- Blunt, first-principles, founder-mode. Lead with the point. Concrete facts and numbers.
- No em dashes, no AI-sounding phrases, no decorative bold or emoji headings, no recap endings.
- Light mode for anything visual. Simple, easy UX. Comprehensible at a glance.
- Summarise each change individually after an update.
- When sharing several outputs, say which is which, what it is for, and why it was made.
- Cross-check every change visually and against the original design rules.
- Fewer setup steps beats clever setups (he rejected Apps Script).
- Read his messages for intent, and ask one short question only when a wrong guess would be costly.
- He wants the impeccable design skill used for site design work.
