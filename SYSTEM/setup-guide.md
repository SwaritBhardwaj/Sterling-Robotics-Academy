# Setup guide

What's needed to read and edit the vault day to day. Routines are not set up yet (see `TODOS.md`).

## 1. Obsidian on desktop and phone
1. Create a fine-grained GitHub token: repository `SwaritBhardwaj/Sterling-Robotics-Academy` only, Contents read and write.
2. In Obsidian: create an empty vault (for example "Sterling").
3. Install the community plugin **GitHub Gitless Sync** (works on mobile, no git needed).
4. Settings: owner `SwaritBhardwaj`, repo `Sterling-Robotics-Academy`, **branch `vault`** (not `main`), the token. Sync every 5 minutes, Pull on Startup on.
5. Run a first sync. The folders from `README.md` should appear.

Check the branch setting carefully. Pointing the plugin at `main` would sync the site code instead, and any push there would deploy the live site.

## 2. Day to day
- Talk to Claude Code: "Log today...", "New lead...", "Admitted...". See `usage-patterns.md`.
- Quick notes from the phone go in `00-INBOX/`.

## Later
- Routines, email digests and the queue: when the course is running.
