---
title: Statements, variables and conditions
short: Code I
kit: Laptop only
recording:
slides:
---

> How does a robot decide what to do?

## By the end of this week
- Statements, variables and conditions, in blocks and in Arduino code
- The difference between = and ==
- A rough picture of digital pins, analog input (ADC) and PWM
- A tilt alarm that mimics what the robot will decide later

## Have ready for class
- Free Tinkercad account, logged in
- Robot not needed this week

## Assignment

### Must: Heartbeat LED
The LED blinks twice quickly, then rests for 1 second, like a heartbeat. Use variables named beatOn, beatOff and rest. Build it in blocks, then check the text view. Submit the Tinkercad link.

### Must: Button lamp
The LED is on only while the button is pressed. Use if and else. Submit the Tinkercad link.

### Must: Tilt alarm 2.0
Five zones from the potentiometer, written in text: above 800 "falling forward fast", 600 to 800 "leaning forward", 400 to 600 "balanced", 200 to 400 "leaning back", below 200 "falling back". Each zone lights a different LED combination. Submit the Tinkercad link.

### Must: Predict the output
For each snippet, write your prediction before you run it. Then run it and record what happened.

```
PREDICT THE OUTPUT
Snippet | My prediction | What happened | Right? (Y/N)
A       |               |               |
B       |               |               |
C       |               |               |
D       |               |               |
```

### Stretch: Toggle switch
Press the button once: LED on. Press again: LED off. You need a variable that remembers the state.

## Before you submit, check
- Named variables instead of repeated numbers
- else if checks run in order with no gaps between zones
- Code is indented so each block is easy to read

## Resources
- Tinkercad Circuits (tinkercad.com), three starter circuits
- Predict-the-output snippets A to D
- Pin tour slide
