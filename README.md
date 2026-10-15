# Sterling Robotics Academy: Business OS

Plain-Markdown vault for Sterling Robotics Academy. Knowledge lives here in Git. Claude Code reads it, updates it and commits. Swarit reads and edits it in Obsidian.

**Read `CLAUDE.md` first.** It is the constitution.

This vault lives on the `vault` branch of the course-site repo. It shares no history with the code. It is never built, hosted or deployed. See `SYSTEM/branches.md`.

## Layers

| Layer | Tool | Role |
|---|---|---|
| Knowledge | This vault (branch `vault`) | Source of truth, version controlled |
| Intelligence | Claude Code | Reads the vault, applies updates, writes drafts, commits |
| Automation | Not set up yet | Routines come later |

## Structure

```
CLAUDE.md        constitution, read first
README.md        this file
TODOS.md         deferred work with enough context to pick up cold
00-INBOX/        raw captures, processed within 7 days
01-FAMILIES/     leads pipeline and one file per admitted family
02-PROJECTS/     one folder per project: overview.md + tasks.md
03-CURRICULUM/   what we teach: course map and the teacher's guide, week by week
04-CONTENT/      everything families see: brochure, WhatsApp messages, entry test questions, voice
05-FINANCE/      pricing, revenue, expenses, monthly briefs
06-STRATEGIC/    the business, cohorts, mentor claims, platform choice, growth
07-DAILY/        YYYY-MM-DD.md daily notes
08-QUEUE/        reserved for routines, not active
09-GENERATED/    Claude outputs: briefings/, reports/, drafts/ (drafts until approved)
SYSTEM/          branches, setup guide, usage patterns, protocols, artifacts, logs, archive
```

## Principles

- Don't delete. Archive with a timestamp.
- Date-stamp generated files `YYYY-MM-DD`.
- Log every write to `SYSTEM/logs/operations.md`.
- Anything a family will see is a draft until Swarit approves it.
- No code in the vault. Code lives in its own branches.

Setup steps: `SYSTEM/setup-guide.md`.
