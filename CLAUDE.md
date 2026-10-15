# Sterling Robotics Academy course site

Private course site on Cloudflare Workers (static assets + a Worker that runs first) for a 12-week robotics course (Elegoo Tumbller, grades 6 to 12, US families).

## Layout
- `content/` is the only place course material lives. Markdown with a small `---` header.
  - `weeks/week-NN/index.md` (+ files, `solutions/`), `resources/`, `students/students.json` + `students/<slug>.md`
  - `site.json` (links, admins), `schedule.json` (cohort dates, unlock rules)
- `build/build.mjs` turns content into `dist/`. `build/test.mjs` tests the access rules.
- `worker/index.js` (entry, config in `wrangler.jsonc`, `run_worker_first: true`) calls `lib/guard.js` + `lib/course.js`: sign-in (Cloudflare Access JWT), enrolment, week and solution locks, private student pages. `lib/me.js`: home page data at `/api/me`.
- `assets/`: site.css (the mentor's notebook look, see DESIGN.md) and app.js (signed-in details, highlighter sweep, copy buttons).

## Rules
- Never push to `main` without Swarit's approval: every push uses Workers build minutes. Work on a branch and merge in one push. Previews: `npx wrangler deploy -c wrangler.preview.jsonc --temporary`.
- Design rules live in DESIGN.md (the mentor's notebook). Product context in PRODUCT.md. Full project history in MEMORY.md one folder up, if present.
- Run `npm run build && npm test` before every push. All checks must pass.
- Student pages hold notes about minors: never print them in logs, commit messages or anywhere public.
- No secrets in the repo. Access settings are Cloudflare environment variables.
- Writing style: plain, short sentences, no em dashes.
