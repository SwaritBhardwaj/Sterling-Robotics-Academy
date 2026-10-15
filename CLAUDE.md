# Sterling Robotics Academy: Business OS

> The constitution: identity, rules and where things live. Read first on every operation.
> Keep it thin. Live state (status, numbers, next actions) lives in the folder files, never here.

## Identity

- **Brand:** Sterling Robotics Academy
- **Legal entity:** none registered yet. Trade as "Sterling Robotics Academy" (decided 2026-10-15).
- **What we do:** a 12-week live online robotics course. Each child in grades 6 to 12 builds the Elegoo Tumbller self-balancing robot at home and writes the code that keeps it standing and recovering from pushes.
- **Who for:** mostly Indian-origin families in the US. Reach also goes through relatives in Canada and Dubai.
- **Tagline:** "Most kids follow the instructions. Yours will understand why they work."
- **Owner:** Swarit Bhardwaj (swarit000@gmail.com). Public email: hellosterlingrobotics@gmail.com.
- **Time zones:** logs in Asia/Kolkata (IST). The course runs on US Eastern (ET).
- **Currency:** USD for fees and revenue. INR for costs paid in India, converted at a stated rate.
- **North Star (confirmed 2026-10-15):** "Does this help a child understand why their robot works, or help a family decide to join?" If no, don't build it.

## Operating rules

- Never delete files. Archive with a timestamp in `SYSTEM/archive/`.
- Never send external communication without Swarit's review. Messages to families, brochure edits and shared artifacts are drafts until he approves them.
- Date-stamp generated files `YYYY-MM-DD`.
- Log every write to `SYSTEM/logs/operations.md` (append-only). Format: `YYYY-MM-DD HH:MM IST | actor | action | path | note`.
- Escalate to Swarit: money, refunds, promises to families, legal and tax filings, anything about a named child.
- When uncertain: put the output in `09-GENERATED/` and flag it for review.
- Named entities in updates (tools, vendors, programs, platforms) are researched on the web before logging. See `SYSTEM/auto-research-protocol.md`.
- Enrich, don't echo. Never fabricate. Log "research inconclusive" when a search is empty.
- Corrections are logged visibly ("was X, actually Y, because Z"), never silently overwritten.
- Artifacts and published pages are renderings of vault files, never the place a number lives.
- Update the vault at the end of every work session, in any branch: the project's `overview.md` and `tasks.md`, today's `07-DAILY/` note, and the operations log.

### Sterling-specific rules

- **This vault is never hosted or deployed.** The `vault` branch has no build config and must never get one. Code never goes in the vault. See `SYSTEM/branches.md`.
- **Site `main` is production.** Every push to `main` in the site code deploys the live site and uses Cloudflare build minutes. Never push or merge to it without Swarit's explicit approval. Previews use `npx wrangler deploy -c wrangler.preview.jsonc --temporary`.
- **Privacy of minors.** Notes about a child stay in the site's private student pages or the entry-test Sheet. Never put them in commit messages, logs or anything shared. The vault holds only a child's first name, grade and pipeline status.
- **Public claims.** Mentor wording follows `06-STRATEGIC/mentor-claims.md` exactly. Never name unconfirmed mentors, promise class times or state a seat number. Never invent testimonials or photos. The India phone number never appears in parent materials.
- **Writing style everywhere:** plain, short sentences. No em dashes. No AI-sounding words (delve, leverage, robust). No "not X, it's Y" lines. Lead with the point. Light mode for anything visual.
- **After any change,** summarise each change individually. When sharing several files, say which is which, what each is for and why it exists.

## Resolver

| Working on | Load |
|---|---|
| A family or lead | `01-FAMILIES/leads.md` (+ `01-FAMILIES/<family>.md`) |
| The course website (code, hosting, design) | `02-PROJECTS/course-site/overview.md` + `tasks.md` + `decisions.md` |
| Student platform: progress, rewards, submissions (next feature) | `02-PROJECTS/progress-database/overview.md` |
| Launch checklist (payments, booking, terms) | `02-PROJECTS/launch/overview.md` + `tasks.md` |
| Entry test (format, tool) | `02-PROJECTS/entry-test/overview.md` |
| What we teach, week by week | `03-CURRICULUM/overview.md` + `teaching-guide/` |
| Brochure | `04-CONTENT/brochure/README.md` |
| WhatsApp messages | `04-CONTENT/whatsapp/` |
| Entry test questions and rubric | `04-CONTENT/entry-test/` |
| Voice and tone | `04-CONTENT/voice.md` |
| Fees, revenue, costs | `05-FINANCE/pricing.md` + `revenue.md` + `expenses.md` |
| Payments, refunds, tax | `SYSTEM/billing-process.md` |
| Business, cohorts, mentor claims, growth | `06-STRATEGIC/` |
| Daily notes | `07-DAILY/` |
| Branches and what deploys | `SYSTEM/branches.md` |
| Published artifacts and links | `SYSTEM/artifacts.md` |
| Operations log | `SYSTEM/logs/operations.md` |
| Original handoff (Oct 15) | `SYSTEM/archive/2026-10-15-handoff/` |

**Roster** (names only, status lives in each file):
- **Cohorts:** Founding (Nov 2026) · Winter (Jan 2027)
- **Projects:** Course site · Progress database · Launch · Entry test
- **Content:** Brochure · WhatsApp messages · Entry test questions
- **Families:** none admitted yet

## Weekly Focus

_Week of 2026-10-12. Draft written 2026-10-15 from the handoff. Swarit to confirm or re-rank. Rewrite every Monday._

1. **Fill the founding cohort.** Enrolment closes 1 Nov (17 days). Send the referral messages and track every lead in `01-FAMILIES/leads.md`.
2. **Booking calendar for entry tests.** Without it, /book and /test can't be sent. Blocks step 1.
3. **Payment link.** Finish KYC, set the $150 link, run a $1 test. Blocks the first admission, and the $150 reserves fund the kit orders.
4. **Student platform PRD.** v0 drafted. Swarit decides 6 items, then build starts. Week 1 opens 9 Nov. See `02-PROJECTS/progress-database/overview.md`.
5. **Redesign decision.** Preview is on branch `redesign`. Merge to `main` only on Swarit's yes.
6. **Terms page and class time.** Both needed before families pay.

## Skills

70 skills vendored on this branch in `.agents/skills/`, symlinked into `.claude/skills/`, pinned in `skills-lock.json`. Copied 2026-10-15 from the Influenzo vault (same versions). Update with `npx skills update`. Full list and examples: `SYSTEM/skills.md`. gstack is not installed (it is per machine, see `TODOS.md`).

Route by intent:

| Work | Use |
|---|---|
| Product specs, what to build first | `prd-writing`, `mvp-scoping`, `roadmap-planning` |
| System design, picking tools | `architecture-design`, `tech-stack-eval` |
| Security of the site | `security-review` |
| Site and page design | `impeccable` (Swarit wants it for all site design) |
| Terms page, privacy, children's data | `terms-of-service`, `privacy-policy` |
| Family onboarding, parent FAQ, SOPs | `onboarding-flow`, `support-docs`, `process-docs` |
| The offer, pricing, guarantees | `hundred-million-offers` (default); `100m-offers`, `alex-hormozi-pitch` only for a second opinion |
| Where families come from, referrals | `100m-leads` |
| Writing an actual outreach message | `cold-outreach-board` |

Skill output that a family will see is a draft until Swarit approves it. Writing style rules above still apply to every skill's output.
