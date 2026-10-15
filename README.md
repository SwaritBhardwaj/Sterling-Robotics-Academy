# Reference code

Code and page sources that sit outside the course site. Orphan branch: no shared history with the site, nothing here is built or deployed by Cloudflare.

| Folder | What | Notes |
|---|---|---|
| `entry-test/` | Entry test slides and grader | `entry-app-src.html` + `entry-gen.js` (question generator), built by `python3 build.py` into `sterling-entry-test.html`. The live version runs as a Claude artifact (artifact database + Drive connector). Outside claude.ai it shows signed-out mode |
| `teaching-guide/` | Original HTML teaching guide | Kept for history. The Markdown copy on branch `vault` (`03-CURRICULUM/teaching-guide/`) is now the source |

Questions, rubric and lesson content live in the vault (branch `vault`). If a question changes there, change `entry-gen.js` here to match.

Never merge this branch into `main`.
