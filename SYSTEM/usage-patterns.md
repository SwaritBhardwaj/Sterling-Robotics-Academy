# Usage patterns

Swarit gives a short update; Claude Code files it across the vault, commits to `vault` and logs it.

## New lead
> "New lead: Priya Shah, son Aarav, grade 7, Edison NJ, referred by Rohit."

- Adds a row to `01-FAMILIES/leads.md` (stage Messaged, date), updates the counts.
- Adds the referrer to the Referrers table.
- Commit: `families: new lead (Shah)`. No child details in the commit message.

## Test booked / done / result
> "Aarav's test done, admit, 8 out of 12."

- Moves the row to Test done or Admitted, with the date.
- Scores stay in the entry-test Sheet. The vault keeps the result band only.
- On Admit: creates `01-FAMILIES/<family>.md` from the template.

## Payment
> "Received $150 from the Shahs."

- Appends to `05-FINANCE/revenue.md`, updates the family file and the pipeline.
- Flags referral credits that are now owed.

## Site or code session
> "Finished the upload flow on feature/progress-db, blocked on R2 limits."

- Updates the project's `overview.md` (status, blocker, next step) and `tasks.md`.
- Adds the line to today's `07-DAILY/` note.

## Content change
> "Change the /fees reply to say..."

- Edits `04-CONTENT/whatsapp/quick-replies.md`, notes "not yet pasted into WhatsApp".
- Same for brochure text: edit source, rebuild, add a history row.

## Curriculum change
> "Week 8 should have a tuning video before class."

- Edits `03-CURRICULUM/teaching-guide/week-08.md` first, then notes that the student page in the site repo needs the same change.

## Draft a message
> "Draft the welcome message for class one."

- Uses `04-CONTENT/voice.md` and the facts in the vault. Saves to `09-GENERATED/drafts/YYYY-MM-DD-<slug>.md`. Never sends.

## Daily note
> "Today: two tests done, wrote the PRD."

- Writes `07-DAILY/YYYY-MM-DD.md`.
