# Sterling Robotics Academy course site

The private site students and parents use during the course: weekly pages, files, class recordings, homework links and a private page for each student.

Every push to `main` rebuilds the site on Cloudflare Workers in about a minute.

## Weekly routine

| When | What to change |
|---|---|
| Before class | Add files (code, PDFs, images) to `content/weeks/week-NN/`. They appear under **Files** on that week's page. |
| After class | Paste the unlisted YouTube link into `recording:` at the top of `content/weeks/week-NN/index.md`. |
| After class | Put solution files in `content/weeks/week-NN/solutions/`. Students can open them from the Saturday after class. |
| After each 1:1 | Add notes to `content/students/<slug>.md`. Only that student and you can see it. |

Files must be under 25 MB each. Put videos on YouTube as unlisted, never in the repo.

## Add a student

1. Add them to `content/students/students.json`:
   ```json
   { "slug": "aarav-mehta", "name": "Aarav Mehta", "grade": "7", "cohort": "founding", "emails": ["parent@email.com", "kid@email.com"] }
   ```
   `cohort` is `founding` or `winter`. Any email in the list can sign in.
2. Create `content/students/aarav-mehta.md` for their notes (copy `sample-student.md`).
3. Remove the sample student before class one.

## Settings

- `content/site.json`: class time, Google Meet link, homework form link, 1:1 booking link, admin emails.
- `content/schedule.json`: first class date for each cohort, how many days before class a week opens (6 = the Monday before) and when solutions open.

## How access works

- Cloudflare Access asks for an email and sends a one-time code. No passwords.
- `worker/index.js` runs before every file is served. Using `lib/guard.js`, it checks the Access sign-in token, checks the email against `students.json` and the admins in `site.json`, locks weeks until their date, and keeps each student page private.
- Admins see every week and every student page at any time.

## One-time Cloudflare setup

1. **Create the Worker:** Workers & Pages > Create > Import a repository > pick this repo. Build command `npm run build`, deploy command `npx wrangler deploy`, preview builds off. Deploy.
2. **Email codes:** Cloudflare One (Zero Trust) > Integrations > Identity providers > add **One-time PIN**.
3. **Lock the Worker:** Workers & Pages > sterling-robotics-academy > **Access** tab > Protect this Worker behind Access > **All traffic** > policy: Allow, Include Everyone (login method One-time PIN) > Apply Access. The site itself refuses anyone not in `students.json`.
4. **Team domain:** Cloudflare One > Settings > Team domain, e.g. `sterling.cloudflareaccess.com`.
5. **Variables:** Worker > Settings > Variables and secrets, add `ACCESS_TEAM_DOMAIN` (Text) = the team domain. Optional but stronger: `ACCESS_AUD` = the application's AUD tag. Deploy.
6. **Test** in a private window: your email works, an unenrolled email is refused.

Until step 5 is done the site shows "Almost ready" to everyone. Never set `DEV_EMAIL` on the live Worker: it is for local testing only.

## Run locally

```
npm install
npm run build   # builds dist/
npm test        # checks sign-in, week locks and private pages
npx wrangler dev --var DEV_EMAIL:you@example.com   # run locally as that user
```
