# Sterling Robotics Academy course site

The private site students and parents use during the course: weekly pages, files, class recordings, homework links and a private page for each student.

Every push to `main` rebuilds the site on Cloudflare Pages in about a minute.

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
- `functions/_middleware.js` then checks that email against `students.json` and the admins in `site.json`, locks weeks until their date, and keeps each student page private.
- Admins see every week and every student page at any time.

## One-time Cloudflare setup

1. **Pages:** Cloudflare dashboard > Workers & Pages > Create > Pages > Connect to Git > pick this repo.
   Build command `npm run build`, output directory `dist`. Deploy and note the address, e.g. `sterling-robotics.pages.dev`.
2. **Zero Trust:** open Zero Trust in the dashboard, pick a team name (e.g. `sterling`) and choose the Free plan.
3. **Sign-in method:** Zero Trust > Settings > Authentication > add **One-time PIN**.
4. **Lock the site:** Zero Trust > Access > Applications > Add > Self-hosted.
   - Add two public hostnames: `sterling-robotics.pages.dev` and `*.sterling-robotics.pages.dev` (previews).
   - Policy: Allow, Include **Everyone**. The site itself refuses anyone not in `students.json`, so the class list lives in one place.
   - Save, then copy the **Application Audience (AUD) tag**.
5. **Connect them:** Pages project > Settings > Variables and secrets > Production, add:
   - `ACCESS_AUD` = the AUD tag
   - `ACCESS_TEAM_DOMAIN` = `sterling.cloudflareaccess.com` (your team name)
   Then redeploy.
6. **Test** in a private browser window: sign in with your email, then with an email that is not enrolled (it should be refused).

Until step 5 is done the site shows "Almost ready" to everyone.

## Run locally

```
npm install
npm run build   # builds dist/
npm test        # checks sign-in, week locks and private pages
```
