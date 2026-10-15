# Entry test

## Brief
A free, live 10-minute video call that admits and places each child. A child can't hand it to AI: it checks what they have built, how they reason, physics and circuits. Experience alone does not decide it.

## Status
**Live and in use.**

## Code
Branch `reference`, folder `entry-test/` (slides and grader page, question generator, build script). The live version runs as a Claude artifact because it uses the artifact database and the Drive connector: https://claude.ai/artifact/P6tyeW61bCXgLd8hDTSLMU (v8).

## Content
Questions, rubric and result bands: `04-CONTENT/entry-test/`.

## How it works
- **On the PC** choose Slides and share only that window in Meet. **On the phone** choose Grader. The grader follows the live slide. The phone does not drive the slides (Swarit said no to a remote).
- A 4-digit test code seeds the question generator. Same code, same questions on slides and grader. "New test" makes a new code (siblings, retests).
- Every tap saves to the artifact database (owner-only). Past tests list. Settings hold the payment link and the "after a parent books" message.
- On Finish or "Sync now", a fresh results Sheet is built in the Drive folder "Sterling Entry Tests" and the old one is trashed. Always open the folder, not an old Sheet link. CSV export too.
- "Finish and make report" makes a one-page PDF and the WhatsApp message for the parent.
- Signed out of Claude, the page offers a test-code box to see answers but saves nothing. Check the top bar says "Saved" after the first tap.
- Only one live test at a time.
- Slides style (Swarit: "PERFECT", 14 Oct): blueprint dot grid, part pills (01 You, 02 Puzzles, 03 Motion, 04 Circuits), a line-art swaying robot on the title slide.

## Decisions
- **Rejected: a Google Apps Script version.** "I do not want to create an app script for this... I'm fine with like signing in and then doing everything." It was deleted. Don't propose it again.
- Part 3 is wheels and gears. It replaced a ruler-balancing question because that repeated week 1.
- No written test. Background answers come from the WhatsApp default message, but Part 1 still asks about builds on the call.

## Open
- Set the artifact to private so nobody can see the answers.
- Payment link still empty in Settings.
