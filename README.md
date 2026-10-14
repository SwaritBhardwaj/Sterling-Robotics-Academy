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

1. **Create the Worker:** Workers & Pages > Create > Import a repository > pick this repo.
   - Build command: `npm run build`
   - Deploy command: `npx wrangler deploy`
   - Turn **Enable Preview builds** off.
   - Turn **Protect with Cloudflare Access** on.
   - Deploy.
2. **Sign-in method:** Zero Trust > Settings > Authentication > add **One-time PIN**.
3. **Access policy:** Zero Trust > Access > Applications > open the app created for the Worker. The policy should be Allow, Include **Everyone**. The site itself refuses anyone not in `students.json`, so the class list lives in one place. Copy the **Application Audience (AUD) tag**. Your team domain is under Zero Trust > Settings > Custom pages (`<team>.cloudflareaccess.com`).
4. **Connect them:** Worker > Settings > Variables and secrets, add:
   - `ACCESS_AUD` = the AUD tag
   - `ACCESS_TEAM_DOMAIN` = `<team>.cloudflareaccess.com`
   Then redeploy (Deployments > retry, or push any change).
5. **Test** in a private browser window: sign in with your email, then with an email that is not enrolled (it should be refused).

Until step 4 is done the site shows "Almost ready" to everyone. Never set `DEV_EMAIL` on the live Worker: it is for local testing only.

## Run locally

```
npm install
npm run build   # builds dist/
npm test        # checks sign-in, week locks and private pages
npx wrangler dev --var DEV_EMAIL:you@example.com   # run locally as that user
```
