---
week: 4
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 4: Loops, the Serial Monitor and debugging

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-04/index.md`.

**Driving question:** How do we see what the robot is thinking, and fix it when it is wrong?

| | |
|---|---|
| Class length | 90 min, 75 min short |
| Robot by the end of the week | Loops, prints and fixes errors |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students use for loops, print labelled values from their real robot to the Serial Monitor, read compiler errors, and debug with a four-step method. Everyone moves to Arduino code from this week.

Students leave with:
- for loops they can read and write
- Their robot printing to the Serial Monitor and the Serial Plotter
- The four-step debugging method
- The habit of checking that code which compiles still does the right thing

## Before class

You prepare:
- Bug hunt sketch with five bugs for class, and a second one for homework, both tested
- Your robot connected to Arduino IDE and screen-shared
- Three for loops ready for the prediction poll

Students bring:
- Robot charged and connected by USB
- Arduino IDE 2 open

## Run of show (90 min)

### 0 to 5 min · Engage: Show last week _(trim if short)_

Replay one predict-the-output snippet from week 3 that most of the class got wrong.

### 5 to 15 min · Engage: Blink five times, then stop

Challenge: make the LED blink exactly five times, then stay off. Let them suggest answers. Most will copy the same four lines five times.

Ask:
- What if I wanted 500 blinks?
- loop() already repeats forever. Why would we need another loop inside it?

### 15 to 30 min · Explain: The for loop

Write for (int i = 1; i <= 5; i++) and label its three parts: where to start, keep going while, how to step. Show three loops and poll the output of each before running: i < 5 against i <= 5, i += 2, and counting down from 10.

Ask:
- Starting at 1, how many times does i < 5 run?
- How would you count down from 10 to 1?

### 30 to 50 min · Explore: The robot talks back

Real robot on USB. Upload Serial.begin(9600); and Serial.println("Hello from Anya's robot"); plus a for loop that prints a counter. Then set the Serial Monitor to 115200 on purpose. The text turns into nonsense. Let them work out why before you explain: both sides must agree on the speed, called the baud rate. Then print variables with labels: Serial.print("i = "); Serial.println(i);

Ask:
- The message turned into nonsense. What changed?
- Why print "i = " before the number?

### 50 to 75 min · Explore: Bug hunt

Teach the method first. (1) Read only the first red error. (2) Go to its line and the line above. (3) If it compiles but behaves wrong, print the values you think you know. (4) Change one thing and run again. Then hand out a sketch with five bugs: a missing semicolon, serial.begin in lowercase, a misspelled variable, a missing closing bracket, and a loop that prints 1 to 9 instead of 1 to 10. The last one compiles fine. Breakout rooms fix one bug at a time.

Ask:
- Which bug did the compiler not catch? Why not?
- The error points at line 12, but the mistake is on line 11. How can that happen?

### 75 to 85 min · Elaborate: A line that moves _(trim if short)_

Print a number that rises from 0 to 100 and falls back, forever, then open the Serial Plotter. Tell them: "Next week this line is your robot's tilt."

### 85 to 90 min · Evaluate: Exit question and assignment



Ask:
- Your code compiles but the robot does the wrong thing. What do you do first?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| No red error means the code is right. | The compiler checks grammar, not meaning. Bug 5 proves it. |
| The mistake is always on the line the error names. | Often it is the line above, as with a missing semicolon. |
| Printing costs nothing. | Printing takes time. In week 10, printing every loop can stop a robot balancing. |
| i++ is a special word. | It means "add 1 to i". i = i + 1 does the same. |

## Assignment (due Saturday 8 PM ET)

### Must · P1: Countdown

On the robot, print 10 down to 1, then "Liftoff!", once. Hint: code in setup() runs once.

### Must · P2: Times table

Print the 7 times table from 7 x 1 = 7 to 7 x 12 = 84 using one for loop.

### Must · P3: Bug hunt 2

Fix the homework sketch. Submit the fixed code and a bug log.

```
BUG LOG
# | Line | First line of the error message | What was wrong | How I fixed it
1 |      |                                 |                |
2 |      |                                 |                |
3 |      |                                 |                |
4 |      |                                 |                |
5 |      |                                 |                |
```

### Must · P4: Plotter wave

Print a value that rises from 0 to 100 and falls back, forever. Submit a screenshot of the Serial Plotter.

### Stretch · P5: Prime finder

Print every prime number below 100. You will need a loop inside a loop.

## What good looks like

- The bug log quotes the compiler's real words
- The logic bug is found and explained
- Every Serial print has a label

## 1:1 focus this week

Share a fresh broken sketch on screen and watch them debug it. Coach the four steps. Don't fix it for them.

## Teacher notes

- Plant the printing-costs-time idea now. It saves a lot of 1:1 time in week 10.

## Resources

- Bug hunt sketches (class and homework)
- Four-step debugging card

---
Previous: [[week-03]] · Next: [[week-05]]
