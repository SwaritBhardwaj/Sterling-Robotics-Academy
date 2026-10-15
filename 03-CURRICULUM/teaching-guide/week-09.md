---
week: 9
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 9: Balance point, safety cut-off and I

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-09/index.md`.

**Driving question:** Why does my robot keep running off in one direction?

| | |
|---|---|
| Class length | 90 min, 75 min short |
| Robot by the end of the week | Stands 15 s, stops safely |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students find their robot's real balance point and use it as the target, add a safety cut-off, add the dead-zone values from week 7, and test a small I term. Target: 15 seconds hands-free.

Students leave with:
- Their robot's balance point, measured and in the code
- A cut-off that stops the wheels when the robot falls
- Dead-zone compensation
- Their own evidence on whether I helps their robot

## Before class

You prepare:
- A sketch that prints only the angle with the motors off
- Three week 8 videos of robots that stood briefly, then ran away
- Stub additions for target angle, cut-off, dead zone and I

Students bring:
- Robot fully charged
- Week 7 dead-zone numbers and week 8 tuning log to hand

## Run of show (90 min)

### 0 to 10 min · Engage: Runaways

Show three week 8 videos where the robot stood for a moment, then ran off in one direction.

Ask:
- It runs off forward every time. If it were perfectly balanced, would it prefer a direction?
- What could make one side heavier?

### 10 to 25 min · Explore: Find the balance point

Motors off; the sketch only prints the angle. Hold the robot at the top with two fingertips, very lightly, and find the position where it feels weightless and doesn't want to fall either way. Read the angle. Do it three times and average.

Ask:
- Is your balance point at 0°? How far off is it?
- Why might two identical kits have different balance points?

### 25 to 35 min · Explain: The target angle

The sensor's zero is where the chip is flat, not where the robot balances. The battery, board and wires are never perfectly centred, so the robot balances a few degrees off. If the code aims for 0°, the robot always leans a little, keeps driving to catch itself, and runs away. Set targetAngle to the measured average and run again.

### 35 to 50 min · Explore: Safety cut-off and dead zone

Add a rule: if the angle is more than 35° from the target, stop the motors. Tip the robot over: the wheels must stop. Then add the dead-zone values from week 7, so small corrections actually turn the wheels.

Ask:
- Without a cut-off, what happens when the robot falls?
- Remember PWM 30 in week 7. Why does that matter for tiny corrections?

### 50 to 70 min · Explain: I: fixing a slow lean

If it still leans and creeps one way, I adds up the error over time, so a small lean that lasts grows into a firmer push. Analogy: a parent who notices you have been slouching for ten minutes reminds you a little more firmly each time. Keep Ki tiny and cap the total (anti-windup). Many robots need little or no I. Students test and decide.

Ask:
- Did I help or make it worse? What is your evidence?
- What happens if the total keeps growing while the robot lies on its side?

### 70 to 85 min · Elaborate: 15-second challenge _(trim if short)_

Breakout rooms. Everyone tries for a 15-second hands-free stand. Mentors log the times.

### 85 to 90 min · Evaluate: Exit question and assignment



Ask:
- Why does a robot run away when its target angle is wrong?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| The I term does the balancing. | P and D do the balancing. I only removes a slow, steady lean. |
| 0° is upright. | Upright is the robot's measured balance point. |
| The cut-off should be as small as possible. | Too small and it switches off during normal corrections. Start around 35° to 45°. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Balance point

Measure three times, then compare stand times before and after.

```
BALANCE POINT
Try 1: ____°   Try 2: ____°   Try 3: ____°   Average: ____°

Before (target 0°):        runs off toward ________ after ____ s
After (target = average):  stands ____ s
```

### Must · T2: Cut-off video

Up to 15 s. Tip the robot over and show the wheels stop.

### Must · T3: Dead zone and tuning log

Add dead-zone compensation. Log at least 6 runs.

```
TUNING LOG (week 9)
Run | Target (°) | Kp | Kd | Ki | Seconds standing | Notes
1   |            |    |    |    |                  |
2   |            |    |    |    |                  |
3   |            |    |    |    |                  |
4   |            |    |    |    |                  |
5   |            |    |    |    |                  |
6   |            |    |    |    |                  |
```

### Must · T4: 15-second video

Up to 30 s. The robot stands 15 seconds with no hands.

### Stretch · T5: Halving search

Find the balance point a second way: try a target, see which way it runs, then halve the step each time. Log each try and compare with your fingertip result.

## What good looks like

- Stands 15 seconds hands-free
- Wheels stop when it tips over
- Balance point recorded and used as the target

## 1:1 focus this week

Anyone under 5 seconds gets a fix session. Check in this order: target angle, signs, battery charge, loose wheels or screws.

## Teacher notes

- What "finding the balance point" means: the robot's weight is never perfectly centred over the axle, so it stands upright at an angle a few degrees away from the sensor's 0°. That angle is the balance point. Using it as the target stops the steady runaway.
- Without wheel encoders the robot will still drift slowly across the floor. That is expected in this cohort. The bar is standing, not staying in one spot.

**Additions to the stub**

```
float targetAngle = ____ ;               // your measured balance point

if (abs(angle - targetAngle) > 35) {      // fallen over
  setBothMotors(0);
  errorSum = 0;
  return;
}

errorSum += error * dt;
errorSum = constrain(errorSum, -____, ____);   // cap the total
float iTerm = Ki * errorSum;

int output = pTerm + dTerm + iTerm;
if (output > 0) output += deadZone;            // from week 7
if (output < 0) output -= deadZone;
output = constrain(output, -255, 255);
```

## Resources

- Angle-only sketch
- Stub additions
- Runaway videos from week 8

---
Previous: [[week-08]] · Next: [[week-10]]
