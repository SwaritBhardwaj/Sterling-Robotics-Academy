# Auto-Research Protocol

When Swarit briefs Claude Code on progress, he mentions things in passing : accelerators, tools, clients, models. Claude Code never just logs the raw words. It researches, enriches, and logs a complete contextual entry.

## Principle

**Swarit's input is brief and conversational. Vault entries are complete and contextual.** The gap between those two is filled by web research.

## Protocol

For every update that contains a named entity (company, program, model, tool, person, event):

1. **Identify** named entities in the update that warrant research.
2. **Web search** each entity for current, factual context.
3. **Extract**: what it is, current status/timeline, relevance to Sterling, key dates or numbers.
4. **Write** the vault entry with the enriched context, not the raw words.
5. **Flag** any key dates as potential `CLAUDE.md` additions (deadlines, result dates, batch starts).
6. **Confirm** to Swarit: "Logged. Here's what I found and added."

## Examples

| Swarit says | Claude Code does |
|---|---|
| "Thinking of Zoom Pro for classes" | Searches current Zoom Pro price, meeting length limits, recording, cloud storage. Logs a comparison with Google Workspace and OBS in the launch project |
| "Kits from Amazon US" | Searches the Elegoo Tumbller listing: price, stock, shipping time to the US and Canada. Logs in `05-FINANCE/expenses.md` and the launch tasks |
| "Use the Infinity app for payments" | Searches fees, payout times, refund handling, KYC needs. Logs in `SYSTEM/billing-process.md` |
| "A parent asked about Wokwi" | Searches what Wokwi is and what is free. Logs in the curriculum notes |

## Vendor or program entry format

```markdown
## [Program Name]

### What it is
[2-3 sentence description from research : not from Swarit's words]

### Program Details
- Type: [accelerator / grant / fellowship / competition]
- Equity / Funding: [amount and terms if known]
- Cohort / Batch: [which round applied to]
- Application submitted: [DATE]
- Application deadline: [DATE if found]
- Expected result date: [DATE if found]
- Program start date: [DATE if found]
- What they look for: [key criteria from research]

### Our Application
- Status: Applied / Under Review / Accepted / Rejected
- Key pitch angle used: [what we emphasized]
- Contact / portal: [link or email]
- Next action: [what we need to do and when]

### Notes
[anything relevant Swarit mentioned]
```

## Tool research entry format

```markdown
## [Model / Tool Name] : Research Brief
Date researched: YYYY-MM-DD

### What it is
[Description from web research : paper, GitHub, community]

### Relevance to Sterling
[How it fits the course, the site or the business]

### Current State
- Release date: [DATE]
- License: [MIT / Apache / commercial]
- GitHub stars / community activity: [from search]
- Known limitations: [from issues / benchmarks]
- Cost and plan limits: [price, free tier, limits]

### Decision
- Status: Evaluating / Adopted / Rejected / Watching
- Reason: [why]
- Next step: [what needs to happen before decision]
```

## What Claude Code Does NOT Do

- Does **not** fabricate details if search returns nothing : logs "Research inconclusive, manual lookup needed".
- Does **not** add speculation as fact : separates researched facts from inferred context.
- Does **not** override what Swarit said with contradicting research : flags conflicts, doesn't resolve them.
- Does **not** research private individuals, and never any child or parent.
