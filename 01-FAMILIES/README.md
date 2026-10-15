# 01-FAMILIES

Every family from first message to demo day.

```
leads.md            pipeline: one row per family, from first message to kit shipped
<family-slug>.md    one file per admitted family (create on admission)
```

## Privacy

- Keep only what running the course needs: parent name, contact, child's first name, grade, city, cohort, referral source, payment status.
- **No notes about the child here.** 1:1 notes go in the site's private student page (`content/students/<slug>.md` in the site repo). Entry test scores stay in the "Sterling Entry Tests" Google Sheet.
- Never copy any of this into commit messages, logs, artifacts or anything shared.

## Family file template

```markdown
# [Parent surname] family

- **Parent:** [name] · WhatsApp [number] · [email]
- **Child:** [first name], grade [N]
- **City, state:** ...
- **Cohort:** Founding / Winter
- **Referred by:** [name or none] (referral credit: owed / paid / none)
- **Site sign-in emails:** [parent], [child] (added to Access policy: yes/no, students.json: yes/no)

## Status
- Entry test: YYYY-MM-DD, result [Admit / Admit with prep / Not ready yet / Retest]
- Reserve $150: paid YYYY-MM-DD / pending
- Balance $450: paid YYYY-MM-DD / due YYYY-MM-DD
- Kit: shipped YYYY-MM-DD / delivered YYYY-MM-DD
- Shipping address collected: yes/no

## Open items
- ...
```
