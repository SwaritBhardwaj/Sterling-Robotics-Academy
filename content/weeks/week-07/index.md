---
title: Actuators: PWM and the motor driver
short: Motors and PWM
kit: Kit needed
recording:
slides:
---

> A pin can only be on or off. How does the Arduino make a motor go slowly?

## By the end of this week
- PWM, duty cycle and the average voltage formula
- Why the battery powers the motors through a driver, and what an H-bridge does
- Dead-zone numbers for both wheels (used again in week 9)
- A tilt follower, and first-hand proof that full speed or nothing can't balance

## Have ready for class
- Robot charged
- A box or a stack of books to lift the wheels off the table

## Assignment

### Must: Motor dance
Wheels in the air. Both forward 2 s, both back 2 s, spin (one forward, one back) 2 s, stop. Submit a video of up to 30 s and the .ino file.

### Must: Dead zone
Sweep each wheel and record the first value that moves it. Keep these numbers; you use them in week 9.

```
DEAD ZONE (wheels in the air)
Wheel | Forward: first PWM that moves | Backward: first PWM that moves
Left  |                               |
Right |                               |
```

### Must: PWM math
Five questions on a 5 V pin.

```
PWM MATH (5 V pin)
1. value 255          → ____ V
2. value 64           → ____ V
3. value 200          → ____ V
4. You want 1 V       → value ____
5. You want 3 V       → value ____
```

### Must: Tilt follower
Video of up to 45 s: you hold the robot and the wheels follow the tilt. Submit the .ino. Then one try on the floor; describe what happened in two lines.

### Stretch: Smooth follower
Make wheel speed grow with tilt instead of jumping to 120: speed = angle × 10, limited to 255. Does it behave better on the floor?

## Before you submit, check
- PWM math answers: 5 V, 1.25 V, 3.92 V, 51, 153
- Dead-zone values recorded for both wheels in both directions
- Both wheels turn forward when the code says forward

## Resources
- motor_test sketch with setMotor helper
- H-bridge drawing
- Tinkercad LED dimming demo
