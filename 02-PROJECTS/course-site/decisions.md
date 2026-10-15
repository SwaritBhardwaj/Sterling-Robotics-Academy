# Course site: decisions and history

## Why our own site (decided before Oct 2026)
For 2 to 10 students, course platforms cost $50 to $100 a month or take a 10% cut, and many assume adult or school accounts (awkward for under-13s). Checked:

| Platform | Why not |
|---|---|
| Thinkific | No free plan, $54/mo, live cohorts $109/mo |
| Skool | $9/mo + 10%, or $99/mo |
| GitHub Classroom | Shut down 28 Aug 2026 |
| Canvas Free-for-Teacher | Clunky |
| Google Classroom | Free, but students need Google accounts |
| Moodle | Self-host |

Swarit chose to build his own.

## Hosting
- **Cloudflare**, because it is the only free host with a login gate: Access with an emailed one-time PIN, free up to 50 users. Vercel Hobby is non-commercial and its password protection costs $20/project/month. GitHub Pages is public even from a private repo.
- Two layers of privacy: the private repo hides the files, Access hides the live site.
- First built for Cloudflare Pages, then converted to **Workers with Static Assets** (`run_worker_first: true`), because the Workers "Import a repository" flow ignores Pages Functions.
- Workers Builds deploys from `main`: build `npm run build`, deploy `npx wrangler deploy`, preview builds off.
- No custom domain for now.

## Cloudflare setup as done
1. Workers & Pages > Create > Import a repository > this repo, Worker name `academy` (must match `name` in `wrangler.jsonc`). Workers can't be renamed; the first one was `sterling-robotics-academy`, so a new one called `academy` was made.
2. Cloudflare One (Zero Trust) > Integrations > Identity providers > One-time PIN.
3. Reusable Access policy "Class families": Allow, Include Emails (every enrolled parent and student email, plus admins).
4. Access > Applications > Add > Self-hosted, hostname `academy.sterlingrobotics.workers.dev`, policy "Class families", One-time PIN only. Login page customised.
5. Team domain `sterlingroboticsacademy.cloudflareaccess.com` in `wrangler.jsonc` `vars.ACCESS_TEAM_DOMAIN`, with `keep_vars: true`. `ACCESS_AUD` optional.

## Problems hit and fixes
| Problem | Fix |
|---|---|
| Pages Functions skipped by the Workers import | Converted to a Worker with `run_worker_first` |
| Access AUD tag hard to find | Made `ACCESS_AUD` optional; the team domain is enough |
| Worker-level Access only offered "email domain" or "Cloudflare account" | Reusable email policy, then a self-hosted Access app on the hostname |
| One-time code emails not arriving | Policy mismatch; fixed by the self-hosted app with the email policy |
| "Almost ready" page after login | A Git deploy wiped the dashboard variable. Vars now live in `wrangler.jsonc` with `keep_vars: true` |
| No rename option for Workers | New Worker `academy` |
| Temporary Wrangler deploy from a Claude cloud workspace | Blocked earlier by the network proxy. **Worked on 2026-10-15** from a Claude Code cloud session |
| Opening the preview link from a Claude cloud session | Cloudflare shows a bot check to cloud IPs. Check the same build locally with `wrangler dev` instead |

## Rules
- Never probe the live site with curl. Swarit rejected that once.
- Every push to `main` costs build minutes. Batch changes.

## Git history
`main`: 94d4710 initial site · bc0e0eb run as a Worker · 7697112 Access tag optional · 4577f15 rename Worker to academy · d8431fb keep the sign-in setting.
`redesign`: d75389b notebook redesign · b7597f6 point Claude Code at design, product and project notes.
