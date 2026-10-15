# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Primary: students in grades 6 to 12, mostly in US families of Indian origin, using a laptop at a desk beside their robot. They open the site to see what this week is about, what to have ready for Sunday's live class, what to build or code, and to submit work. Secondary: their parents, who check dates, progress and the mentor's notes.

## Product Purpose
The private course site for Sterling Robotics Academy's 12-week live cohort. Students build an Elegoo Tumbller self-balancing robot and write the code that keeps it standing and recovering from pushes. The site holds each week's question, tasks, files, recordings and a private page of 1:1 notes per student. Success: a student opens it, knows in seconds what to do this week, and finishes the work without asking.

## Positioning
One mentor (Swarit Bhardwaj, former robotics researcher at IIT Bombay) teaches every live class and gives every student a weekly 1:1. The course is inquiry-based: each week opens with a question about a real physical problem (why things fall, how a sensor feels tilt) before any code.

## Operating Context
- Live class every Sunday on Google Meet; recordings added after class (unlisted YouTube).
- A week opens the Monday before its class; solutions open the Saturday after.
- Founding cohort starts 15 Nov 2026, winter cohort 10 Jan 2027. 12 weeks each.
- Tools students use alongside: Arduino IDE 2, Wokwi, Tinkercad Circuits, phyphox on a phone.
- Sign-in by emailed one-time code (Cloudflare Access); the site checks the email against the class list.

## Capabilities and Constraints
- Static site built from Markdown in `content/`, served by a Cloudflare Worker that enforces sign-in and week locks. Updates ship by pushing to `main`.
- Build minutes are limited: design previews go to temporary Wrangler deployments, never to `main`.
- Pages will grow to include diagrams, videos, code files and fill-in tables.
- Files up to 25 MB; videos are YouTube embeds.

## Brand Commitments
- Name: Sterling Robotics Academy. Wordmark "Sterling" with "ROBOTICS ACADEMY".
- Site should feel like real, textured paper: one continuous unlined sheet, slightly yellowed, not modern or glossy. Important things marked with a highlighter. Organic, minimal, smooth, few animations, simple for students. (Stated by the owner.)
- Writing voice: plain, short sentences, no em dashes.

## Evidence on Hand
- 12 weeks of student-facing content in `content/weeks/`.
- No student photos, testimonials or class recordings yet. Do not invent them.

## Product Principles
1. This week first: the current week and its tasks are always one click away.
2. Doing over reading: tasks, tables and files are the core; prose stays short.
3. Calm and trustworthy for parents, inviting for a 12-year-old.
4. Nothing locked feels broken: locked weeks show when they open.

## Accessibility & Inclusion
Readable for ages 11 to 18: body text at least 17px on laptop, high contrast on the paper ground, keyboard focus visible, motion respects reduced-motion settings.
