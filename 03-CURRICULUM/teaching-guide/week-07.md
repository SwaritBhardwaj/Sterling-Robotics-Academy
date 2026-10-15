---
week: 7
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 7: Actuators: PWM and the motor driver

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-07/index.md`.

**Driving question:** A pin can only be on or off. How does the Arduino make a motor go slowly?

| | |
|---|---|
| Class length | 90 min, 65 min short |
| Robot by the end of the week | Wheels follow tilt |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students understand PWM as fast on and off that gives an average voltage, why a motor driver is needed, and how to set each wheel's speed and direction in code. They measure each motor's dead zone and build a tilt follower that leads straight into control.

Students leave with:
- PWM, duty cycle and the average voltage formula
- Why the battery powers the motors through a driver, and what an H-bridge does
- Dead-zone numbers for both wheels (used again in week 9)
- A tilt follower, and first-hand proof that full speed or nothing can't balance

## Before class

You prepare:
- motor_test sketch with a setMotor(side, speed) helper, where negative speed means backward
- A box or stand so the robot's wheels spin in the air
- Tinkercad LED dimming demo
- H-bridge drawing with four switches

Students bring:
- Robot charged
- A box or a stack of books to lift the wheels off the table

## Run of show (90 min)

### 0 to 5 min · Engage: Show last week _(trim if short)_

Show the surface test results: which objects fooled the ultrasonic sensor?

### 5 to 15 min · Engage: On or off only

Pins give 0 V or 5 V, nothing in between. Yet the wheels turn slowly while balancing. Collect theories. Then flick your phone flashlight on and off quickly on camera.

Ask:
- How can a pin that only does on and off make a motor go slowly?
- What if I could flick the light 1,000 times a second?

### 15 to 30 min · Explain: PWM

PWM switches the pin on and off so fast that the motor only feels the average. Duty cycle is the share of time it is on. analogWrite(pin, value) takes 0 to 255. Average voltage = value ÷ 255 × 5 V, so 255 gives 5 V, 128 about 2.5 V and 64 about 1.25 V. Run two predictions, then dim an LED in Tinkercad. Link back to the ~ pins from week 3.

Ask:
- analogWrite(pin, 51) gives what average voltage?
- What value gives about 3 V?

### 30 to 40 min · Explain: The motor driver

An Arduino pin can safely give about 20 mA. A motor needs hundreds. Asking a pin to run a motor is like asking a phone charger to start a car. The driver chip is a gate: the small Arduino signal opens and closes it, and battery power flows through. Inside, an H-bridge has four switches. Close one diagonal pair and current flows one way (forward). Close the other pair and it flows back (reverse). Draw it.

Ask:
- Where does the power for the motors come from?
- Which switches would you close to reverse?

### 40 to 60 min · Explore: Wheels in the air

Robot on a box, wheels off the table, always. Upload motor_test. Run each wheel forward and back. Then the dead-zone hunt: sweep from 0 to 255 in steps of 5, print each value, and note when each wheel starts to turn.

Ask:
- At PWM 30, will the wheel turn? Predict first.
- Why do left and right start at different values?
- Why does it take more to start a wheel than to keep it turning?

### 60 to 80 min · Elaborate: Tilt follower _(trim if short)_

Combine with the week 6 angle. Above 2°, both wheels forward at 120. Below -2°, both back. Otherwise stop. Hold the robot and tilt it; the wheels chase the lean. Then let a few students try it on the floor with a hand ready to catch. It jerks and falls.

Ask:
- On the floor, will it balance? Predict.
- What is wrong with full speed or nothing?

### 80 to 90 min · Evaluate: Exit question and assignment



Ask:
- analogWrite(pin, 64): what share of full power is that?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| PWM 128 means half speed. | It means half the average voltage. Speed also depends on load, friction and the dead zone. |
| The Arduino powers the motors. | The battery does, through the driver. The Arduino only sends the signal. |
| Forward is the same for both motors. | The motors face opposite ways. One may need its direction flipped in code. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Motor dance

Wheels in the air. Both forward 2 s, both back 2 s, spin (one forward, one back) 2 s, stop. Submit a video of up to 30 s and the .ino file.

### Must · T2: Dead zone

Sweep each wheel and record the first value that moves it. Keep these numbers; you use them in week 9.

```
DEAD ZONE (wheels in the air)
Wheel | Forward: first PWM that moves | Backward: first PWM that moves
Left  |                               |
Right |                               |
```

### Must · T3: PWM math

Five questions on a 5 V pin.

```
PWM MATH (5 V pin)
1. value 255          → ____ V
2. value 64           → ____ V
3. value 200          → ____ V
4. You want 1 V       → value ____
5. You want 3 V       → value ____
```

### Must · T4: Tilt follower

Video of up to 45 s: you hold the robot and the wheels follow the tilt. Submit the .ino. Then one try on the floor; describe what happened in two lines.

### Stretch · T5: Smooth follower

Make wheel speed grow with tilt instead of jumping to 120: speed = angle × 10, limited to 255. Does it behave better on the floor?

## What good looks like

- PWM math answers: 5 V, 1.25 V, 3.92 V, 51, 153
- Dead-zone values recorded for both wheels in both directions
- Both wheels turn forward when the code says forward

## 1:1 focus this week

Check that a positive speed moves the robot forward on both wheels. Fix any flipped motor inside setMotor now.

## Teacher notes

- PWM numbers: 128 ÷ 255 × 5 V is about 2.5 V. 120 gives about 2.35 V. On the robot the driver applies that same percentage to the battery voltage, so 50% means about half the battery voltage at the motor.
- The Nano switches PWM about 490 times a second on most pins and about 980 on pins 5 and 6.
- Put the pin details inside setMotor(side, speed) so students can read the analogWrite and direction lines without fighting the pin map.
- The smooth follower stretch task is P control. Students who solve it have invented next week's lesson. Show their work in week 8.

## Resources

- motor_test sketch with setMotor helper
- H-bridge drawing
- Tinkercad LED dimming demo

---
Previous: [[week-06]] · Next: [[week-08]]
