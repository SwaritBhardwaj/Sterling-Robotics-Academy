---
week: 10
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 10: Push recovery: tuning and debugging

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-10/index.md`.

**Driving question:** How do we make it stand back up after a push?

| | |
|---|---|
| Class length | 90 min, 80 min short |
| Robot by the end of the week | Stands 30 s, survives a push |
| Assignment due | Saturday, 8 PM ET |

## Goal

Robots stand for 30 seconds and recover from three taps. Students follow a tuning order, change one thing at a time, and diagnose problems with a checklist instead of guessing.

Students leave with:
- A tuning order they can repeat
- The push test
- The debugging checklist
- A robot that meets the final bar, or a clear list of what is left

## Before class

You prepare:
- Your robot set up twice: too little Kd, then the right Kd, for the same tap
- Three broken-robot videos: runs away, buzzes, collapses after a push
- Debugging checklist slide

Students bring:
- Robot fully charged at the start of class
- Tuning log from week 9

## Run of show (90 min)

### 0 to 10 min · Engage: Same robot, different behaviour

Show a tuning log where the same gains worked at the start of a session and failed 20 minutes later.

Ask:
- Nothing in the code changed. What did?

### 10 to 25 min · Explain: Tuning order and the push test

Push test: a one-finger tap at the top plate, then a 2 cm nudge, then a 5 cm push. Tuning order: (1) raise Kp until it shakes fast, then back off about 30%; (2) raise Kd until the shaking stops, and lower it if the robot starts to buzz; (3) add a little Ki only if a slow lean remains. Change one gain at a time and log every run. Demo your robot with too little Kd and the right Kd under the same tap.

Ask:
- Why change only one gain at a time?

### 25 to 60 min · Explore: Tuning lab

Breakout rooms of 6 to 8 with a mentor. Each student runs the tap test, logs, adjusts one gain and repeats. Others watch on camera and call it: lazy, shaky or good.

Ask:
- What did you change, and what did you expect to happen?

### 60 to 75 min · Explain: Debug clinic

Play the three broken-robot videos. The class diagnoses each one with the checklist.

Ask:
- What would you check first?
- What evidence would prove it?

### 75 to 85 min · Elaborate: Live attempts _(trim if short)_

Volunteers try the full bar on camera: 30 seconds and three taps.

### 85 to 90 min · Evaluate: Exit question and assignment



Ask:
- Your robot buzzes in place. Which gain do you change, and which way?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| If it worked yesterday, the code is fine today. | Battery charge changes behaviour. Tune on a charged battery and recheck later. |
| More printing helps debugging. | Printing every loop slows the loop and can break balance. Print every 20th loop. |
| Change everything at once to save time. | Then you can't tell what helped. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Tuning log with taps

At least 8 runs.

```
TUNING LOG (week 10)
Run | Kp | Kd | Ki | Battery (fresh / used) | Seconds | Tap 1 | Tap 2 | Tap 3
1   |    |    |    |                       |         |  Y/N  |  Y/N  |  Y/N
2   |    |    |    |                       |         |       |       |
3   |    |    |    |                       |         |       |       |
4   |    |    |    |                       |         |       |       |
5   |    |    |    |                       |         |       |       |
6   |    |    |    |                       |         |       |       |
7   |    |    |    |                       |         |       |       |
8   |    |    |    |                       |         |       |       |
```

### Must · T2: The bar, on video

Up to 45 s, one take: 30 seconds standing, then three taps.

### Must · T3: Bug story

Four to six lines: one problem you hit, the evidence that found it, and what fixed it.

### Must · T4: Commented code

Updated .ino with a comment on every gain line saying why you chose that value.

### Stretch · T5: How big a push?

Try the nudge and the push. Find the biggest push it survives and film it.

## What good looks like

- One video: 30 s standing plus three taps, single take
- Log shows one gain changed per run
- Bug story names the evidence, not only the fix

## 1:1 focus this week

Rescue session for anyone below 15 seconds. Week 11 is the deadline.

## Teacher notes

- Debugging checklist. Battery: charged? Tune on a fresh charge and recheck when it drops. Mechanics: wheels tight on their shafts, screws tight, board not wobbling, wires clear of wheels. Loop timing: no delay() in the loop, printing every 20th loop at most. Signs: tipping forward drives the wheels forward. Angle: does it still match the phone? Target: re-measure the balance point after any rebuild.

## Resources

- Debugging checklist
- Three broken-robot videos
- Push test card

---
Previous: [[week-09]] · Next: [[week-11]]
