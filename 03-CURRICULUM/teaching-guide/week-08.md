---
week: 8
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 8: Control: P and D

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-08/index.md`.

**Driving question:** How hard should the wheels push, and when?

| | |
|---|---|
| Class length | 90 min (keep it full length) |
| Robot by the end of the week | First stand |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students learn what feedback control is, complete the P line in the stub code, watch P alone overshoot and shake, then add D to calm it. Target for the class: a first hands-free stand of a few seconds.

Students leave with:
- Error, P and D in their own words
- A completed stub with P and D
- A tuning log of at least 8 runs
- A first stand on video

## Before class

You prepare:
- balance_stub sketch with blanks for error, P, D and the output limit
- Find working gains on your own robot first, and compare with the values in Elegoo's demo code
- Backup videos from your robot: P only shaking, and P plus D standing
- Lane-drifting and stop-line slides

Students bring:
- Robot fully charged (this matters from now on)
- Space on the floor, a soft surface nearby
- Tuning sheet with their forward sign from week 6

## Run of show (90 min)

### 0 to 10 min · Engage: Why the tilt follower failed

Replay two floor attempts from last week.

Ask:
- When you balanced the broom, did your hand move the same amount every time?
- So how should the wheel speed depend on the tilt?

### 10 to 25 min · Explain: Feedback control and P

Feedback control: measure, compare with the target, correct, repeat, hundreds of times a second. Error = target angle − measured angle. P pushes in proportion to the error, and Kp sets how hard. Analogy: drifting out of your lane, you steer back harder the further off you are. If anyone solved last week's smooth follower, show it. They invented P.

Ask:
- If the error doubles, what should happen to the push?
- What would Kp = 0 do?

### 25 to 45 min · Explore: P only

Fill in the error and P lines. Start with a small Kp. Hold the robot loosely between two fingers on the floor and never let go. Feel it push. Double Kp each run and log the result: lazy, fights back, or shakes hard. Everyone posts the Kp where shaking starts.

Ask:
- At what Kp does it start to shake?
- When it reaches upright the error is zero. Why does it keep swinging past?

### 45 to 60 min · Explain: D

D looks at how fast the robot is falling and pushes against that speed. Analogy: approaching a stop line, you brake before you reach it because you are moving fast. The gyro already measures how fast the robot tilts, so dTerm = Kd × gyro rate.

Ask:
- What does P look at? What does D look at?
- The robot is upright but swinging fast. What does P do? What does D do?

### 60 to 80 min · Explore: P plus D: first stand

Set Kp to about 60% of the value where shaking started. Raise Kd from small until the shaking calms. Then let go for a moment and catch it. Count the seconds. Celebrate any stand of 2 or 3 seconds. Mentors run breakout rooms. A robot that runs off in one direction is normal; park that for week 9. A robot that drives away from the lean has a sign error.

Ask:
- Did D calm it or make it worse? How can you tell?
- Which way did it run off? Every time?

### 80 to 90 min · Evaluate: Exit question and assignment



Ask:
- One sentence each: what does P do, and what does D do?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| Bigger Kp is always better. | Past a point it shakes and falls. The log shows where. |
| D makes the robot react faster. | D calms it by pushing against fast movement. |
| If it falls, the hardware is broken. | Usually it is a sign, a gain or the battery. Check those first. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Complete the stub

Fill in error, P, D and the output limit. Submit the .ino.

### Must · T2: Tuning log

At least 8 runs. Change one gain at a time.

```
TUNING LOG (week 8)
Run | Kp | Kd | What happened (lazy / fights / shakes / stands) | Seconds standing
1   |    |    |                                                 |
2   |    |    |                                                 |
3   |    |    |                                                 |
4   |    |    |                                                 |
5   |    |    |                                                 |
6   |    |    |                                                 |
7   |    |    |                                                 |
8   |    |    |                                                 |
```

### Must · T3: Video: P only

Up to 20 s. Robot held loosely, showing the shaking at a high Kp.

### Must · T4: Video: P plus D

Up to 20 s. Your best attempt with hands released.

### Must · T5: Explain it

Three sentences: what P does, what D does, and why P alone overshoots.

### Stretch · T6: Plot while balancing

Plot the angle in the Serial Plotter while it balances. Print only every 10th loop so printing doesn't slow it down.

## What good looks like

- At least 8 logged runs covering lazy, shaking and in between
- Wheels drive toward the lean (signs correct)
- Any hands-free stand on video counts this week

## 1:1 focus this week

Live tuning on camera. Watch them run, ask what they will change and why, then let them change one gain. This is the most important 1:1 of the course.

## Teacher notes

- Don't run this class short. Students need the full 40 minutes of hands-on tuning.
- Run the control code on a fixed timer, for example every 5 ms using millis(). Never use delay() inside the balance loop.
- Use the gyro rate for D directly. It is cleaner than subtracting one angle from the last.
- If D makes things worse, flip its sign. The gyro axis may point the opposite way to the angle.
- Keep your own gains private. Share a range in the 1:1 only after 8 or more honest runs.

**balance_stub: the part students fill in**

```
// runs every 5 ms
float angle = getAngle();       // filtered angle from week 6
float rate  = getGyroRate();    // degrees per second from week 5

float error = ________ ;        // how far from the target?
float pTerm = Kp * ________ ;
float dTerm = Kd * ________ ;   // hint: how fast is it falling?

int output = pTerm + dTerm;
output = constrain(output, ____, ____);
setBothMotors(output);
```

## Resources

- balance_stub sketch
- Tuning sheet
- Your backup videos

---
Previous: [[week-07]] · Next: [[week-09]]
