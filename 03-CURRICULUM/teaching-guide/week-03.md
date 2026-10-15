---
week: 3
kit: Laptop only
tags: [curriculum, teaching-guide]
---
# Week 3: Statements, variables and conditions

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-03/index.md`.

**Driving question:** How does a robot decide what to do?

| | |
|---|---|
| Class length | 90 min, 70 min short |
| Robot by the end of the week | Writes variables and if/else |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students write programs that run instructions in order (statements), store values (variables) and make choices (if, else if, else). They build each idea in blocks first, then read and write the same program as Arduino code. A short tour of the board's pins sets up weeks 5 and 7.

Students leave with:
- Statements, variables and conditions, in blocks and in Arduino code
- The difference between = and ==
- A rough picture of digital pins, analog input (ADC) and PWM
- A tilt alarm that mimics what the robot will decide later

## Before class

You prepare:
- Tinkercad Circuits starters: (a) LED on pin 13, (b) pushbutton and LED, (c) potentiometer and three LEDs (the tilt alarm)
- Predict-the-output snippets A to D for the assignment
- Pin tour slide: digital, analog in, PWM
- A cup of water on your desk for "Be my robot"

Students bring:
- Free Tinkercad account, logged in
- Robot not needed this week

## Run of show (90 min)

### 0 to 5 min · Engage: Show last week _(trim if short)_

Show two or three strong label tables from week 2, with permission. Settle the answers: the board decides, the motion sensor senses, the motor driver and motors act, the battery powers.

### 5 to 15 min · Engage: Be my robot

You are the robot. Students type instructions in chat to make you pick up the cup and drink. Follow each instruction exactly as written and nothing more. "Pick up the cup" while your hand is nowhere near it means your hand closes on air. Let it be funny.

Ask:
- What went wrong?
- What does a computer need from us that a person doesn't?

### 15 to 25 min · Explain: The board's pins

A quick tour using analogies only. Digital pins are light switches: on (5 V) or off (0 V). Analog input pins read a dimmer knob: the ADC turns 0 to 5 V into a number from 0 to 1023. PWM pins (marked ~) fake a dimmer by flicking a switch very fast, using a value from 0 to 255. Tell them analog input returns in week 5 and PWM in week 7.

Ask:
- Is the motion sensor an input or an output? The motors?
- A dimmer knob turned halfway: what number would the ADC give?

### 25 to 45 min · Explore: Statements and variables, blocks first

Tinkercad circuit (a). Build "on, wait 1 s, off, wait 1 s" in blocks. Then make a variable called waitTime and use it in both waits. Switch to Blocks + Text and read the generated code line by line: int waitTime = 1000; then digitalWrite(13, HIGH); then delay(waitTime); Point out the semicolons and curly brackets. Tinkercad uses an Uno; the code is the same on the robot's Nano.

Ask:
- If I swap the order of the two wait blocks, what changes?
- Why use a variable instead of typing 1000 twice?
- What does loop() do when it reaches its last line?

### 45 to 65 min · Explore: Conditions: the tilt alarm

Circuit (c). The knob pretends to be the robot's tilt. Read it with int tilt = analogRead(A0); If tilt is above 600, red (falling forward). Else if it is below 400, blue (falling back). Else green (balanced). Build it in blocks, then everyone retypes it in text.

Ask:
- What happens at exactly 600? Predict, then test.
- How would you make the green "balanced" zone narrower?
- Why does the order of the if and else if checks matter?

### 65 to 80 min · Elaborate: Write it from scratch _(trim if short)_

New text-only project. Students type the tilt alarm without copying. Breakout rooms of 6 to 8 with a mentor. Blocks-first students keep the blocks open beside them.

### 80 to 90 min · Evaluate: Exit question and assignment

Poll, then walk through the five problems.

Ask:
- What is the difference between = and ==?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| = and == mean the same thing. | = stores a value. == asks a question. if (tilt = 600) compiles and is always true. |
| All the code runs at once. | It runs top to bottom, one line at a time, then loop() starts again. |
| else needs its own condition. | else catches everything the checks above it missed. |
| Blocks are not real code. | Blocks + Text shows they turn into the same Arduino code. |

## Assignment (due Saturday 8 PM ET)

### Must · P1: Heartbeat LED

The LED blinks twice quickly, then rests for 1 second, like a heartbeat. Use variables named beatOn, beatOff and rest. Build it in blocks, then check the text view. Submit the Tinkercad link.

### Must · P2: Button lamp

The LED is on only while the button is pressed. Use if and else. Submit the Tinkercad link.

### Must · P3: Tilt alarm 2.0

Five zones from the potentiometer, written in text: above 800 "falling forward fast", 600 to 800 "leaning forward", 400 to 600 "balanced", 200 to 400 "leaning back", below 200 "falling back". Each zone lights a different LED combination. Submit the Tinkercad link.

### Must · P4: Predict the output

For each snippet, write your prediction before you run it. Then run it and record what happened.

```
PREDICT THE OUTPUT
Snippet | My prediction | What happened | Right? (Y/N)
A       |               |               |
B       |               |               |
C       |               |               |
D       |               |               |
```

### Stretch · P5: Toggle switch

Press the button once: LED on. Press again: LED off. You need a variable that remembers the state.

## What good looks like

- Named variables instead of repeated numbers
- else if checks run in order with no gaps between zones
- Code is indented so each block is easy to read

## 1:1 focus this week

Ask them to read their tilt alarm aloud and explain each line. If they can, they drop blocks from week 4. If not, they keep blocks and text side by side for one more week.

## Teacher notes

- Keep the pin tour to 10 minutes. It is a map, not a lesson. ADC gets its depth in week 5 and PWM in week 7.

## Resources

- Tinkercad Circuits (tinkercad.com), three starter circuits
- Predict-the-output snippets A to D
- Pin tour slide

---
Previous: [[week-02]] · Next: [[week-04]]
