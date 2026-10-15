# Sterling Robotics Academy: handoff

Start here. This folder carries everything from the earlier Claude chat.

1. Read `MEMORY.md`: the business, every decision and why, what is done, what is next, and how Swarit likes to work.
2. `DESIGN.md`: the course site design (the mentor's notebook). The same file is in `site/DESIGN.md`; edit that one.
3. `site/`: the course website git repo. Branch `redesign` is checked out and holds the notebook redesign, not yet pushed. `main` matches what is live.
4. `reference/`: brochure, entry test and teaching guide sources, each with a `build.py`.

Hard rules:
- Never push to `main` without Swarit's explicit approval. Each push uses Cloudflare build minutes.
- `cd site && npm install && npm run build && npm test` before any push.
- Plain, short sentences. No em dashes.
