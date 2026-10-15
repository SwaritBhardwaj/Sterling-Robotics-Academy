# Branches

All in `SwaritBhardwaj/Sterling-Robotics-Academy` (private).

| Branch | Holds | Deploys? |
|---|---|---|
| `main` | Live course site | **Yes.** Every push deploys via Workers Builds and uses build minutes. Only on Swarit's explicit yes |
| `redesign` | Site code with the notebook redesign | No |
| `feature/student-platform` | The student platform prototype (resources, quizzes, Volts, hints, submissions, review), branched off `redesign` | No |
| `feature/*` | Other new site features, branched off `redesign` | No |
| `vault` | **This vault.** Notes only, no code | **Never** |
| `reference` | Code for the entry test and the original HTML teaching guide | Never |
| `claude/*` | Claude Code session branches | No |

## Why the vault can't deploy
- `vault` and `reference` are orphan branches: no shared history with the site, no `wrangler.jsonc`, no `package.json`. The vault's `.gitignore` blocks both.
- Cloudflare Workers Builds deploys `main` only, and non-production branch builds are off. Even if a build ran on `vault`, it would fail with nothing to deploy.
- Never add build config to `vault`. Never merge `vault` into any code branch, or code into `vault`.

## The final merge
When Swarit says so: merge `redesign` (plus finished feature branches) into `main`, run `npm run build && npm test`, push once. The vault is never merged.

## Previews (no build minutes, no login)
```
git checkout redesign      # or a feature branch
npm install && npm run build
npx wrangler deploy -c wrangler.preview.jsonc --temporary
```
Gives a random `*.workers.dev` link that lasts about 60 minutes. The preview signs everyone in as the admin, so all weeks are open. Only sample student data is in the repo.
From a Claude cloud session the link can't be opened (Cloudflare bot check), so check the same build locally with `npx wrangler dev -c wrangler.preview.jsonc`.

## Working on the vault from Claude Code
```
git fetch origin vault
git worktree add ../sterling-vault vault
```
Edit there, commit, `git push origin vault`.
