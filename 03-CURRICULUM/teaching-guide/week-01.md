---
week: 1
kit: No kit needed
tags: [curriculum, teaching-guide]
---
# Week 1: Why is balancing hard?

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-01/index.md`.

**Driving question:** How do you keep something standing that wants to fall?

| | |
|---|---|
| Class length | 90 min, 65 min short |
| Robot by the end of the week | Explains sense, decide, act |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students feel the balancing problem with their own hands, see that their phone can sense tilt, and run their first code. By the end they can name what any balancing machine needs: a way to sense the tilt, a way to decide, and a way to move, all faster than the fall.

Students leave with:
- The sense, decide, act loop, in their own words
- phyphox installed and their first sensor readings
- Their first code running in Wokwi
- A plan for kit arrival, battery charging and software install

## Before class

You prepare:
- Your robot charged and running Elegoo's demo code, ready to balance on camera
- A broom and a 30 cm ruler beside you
- phyphox on your phone, shown through a second camera or screen mirroring
- Wokwi starter project (Arduino Nano, LED, MPU6050) with a share link ready for the chat
- A blank slide titled "Our question wall"
- Poll ready: "Which was easiest to balance?"

Students bring:
- A broom or mop, a 30 cm ruler and a pencil
- phyphox installed on a phone (free on iOS and Android)
- Laptop with Chrome open
- Camera on, phone nearby

## Run of show (90 min)

### 0 to 10 min · Engage: The robot reveal

Put your robot on the table, let it balance, then tap it once. Say nothing about how it works. Run a chat waterfall: everyone types an answer, nobody presses Enter until you say go. Copy their questions onto the question wall slide. You will answer these on demo day.

Ask:
- What do you notice?
- What do you wonder?

### 10 to 25 min · Explore: Broom challenge

Everyone balances the broom on an open palm for 10 seconds. Then the ruler. Then the pencil. Run the poll. Then ask them to try the broom with their eyes closed. It falls almost at once.

Ask:
- Which was easiest? Why would a longer object be easier?
- What were your eyes doing the whole time? What was your hand doing?
- Why did closing your eyes make it fail?

### 25 to 35 min · Explain: Name the loop

Draw three boxes: Sense (eyes), Decide (brain), Act (hand), with an arrow back to Sense. A short object falls faster, so the loop has to run faster. The robot runs this loop hundreds of times a second. Show a photo of the robot and let them guess which part is its eyes, brain and hand. Don't confirm yet. They find out in week 2.

Ask:
- Which part of the robot do you think is its eyes? Its hand?
- What would happen if the robot's loop ran slower than the fall?

### 35 to 45 min · Explore: Your phone feels tilt

Open phyphox, then "Acceleration with g". Phone flat on the table. Ask them to find the number near 9.8. Tilt slowly, stand the phone on its edge, flip it over. Leave the big question unanswered. It opens week 5.

Ask:
- The phone is not moving. Why does one number say 9.8?
- Where does the 9.8 go when you stand the phone up?

### 45 to 50 min · Explore: Gyroscope, quickly _(trim if short)_

Switch to the Gyroscope screen. A still phone reads near zero. Rotate it slowly, then fast.

Ask:
- What is this sensor measuring that the first one wasn't?

### 50 to 70 min · Elaborate: First code in Wokwi _(trim if short)_

Everyone opens the shared Wokwi link and presses play. The LED blinks. Before anyone edits, collect predictions in chat, then let them change 1000 to 100 and run. Then click the MPU6050 in the running simulation and drag its sliders while the Serial Monitor prints numbers. If short on time, set this as homework with your screen recording.

Ask:
- If I change 1000 to 100, what will the LED do? Type your guess first.
- Which slider changes which number?

### 70 to 80 min · Evaluate: Exit question and assignment

Exit question in chat. Then walk through the assignment on screen, task by task.

Ask:
- Name the robot's sense, decide and act parts. One word each.

### 80 to 90 min · Admin: Get ready for week 2

Kit tracking, battery charging (charge it the night before week 2), Arduino IDE 2 install. Anyone without a kit replies to the class post so you can chase it.

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| A phone lying still should read zero. | It measures gravity. Still on a table, the up axis reads about 9.8. Week 5 explains why. |
| Balancing means holding very still. | It means constant small corrections. Watch your hand on the broom: it never stops moving. |
| A short object is easier to balance because it is smaller. | Short objects fall faster, so you have less time to react. Compare the broom and the pencil. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Balance lab

Balance the broom, the ruler and a pencil. Three tries each. Time each try in seconds.

```
BALANCE LAB
Object  | Length (cm) | Try 1 (s) | Try 2 (s) | Try 3 (s)
Broom   |             |           |           |
Ruler   |             |           |           |
Pencil  |             |           |           |

My guess why the longer one is easier:
```

### Must · T2: Phone sensor readings

In phyphox, open "Acceleration with g". Hold each position still for 3 seconds and write the numbers, rounded to one decimal.

```
PHONE SENSOR (m/s², one decimal)
Position               | X    | Y    | Z
Flat, screen up        |      |      |
Flat, screen down      |      |      |
Standing on long edge  |      |      |
Upright, portrait      |      |      |

Which axis points out of the screen?
```

### Must · T3: Heartbeat blink

In the Wokwi project, make the LED stay on for 200 ms and off for 800 ms. Submit your Wokwi share link.

### Must · T4: Kit ready

Unbox the kit, check every part against the parts list, and post one photo of the parts laid out. Charge the battery the night before class. Install Arduino IDE 2.

### Stretch · T5: Balancing machines

Find three machines that balance themselves, for example a Segway, a drone or a landing rocket. For each, write one line naming its sense, decide and act parts.

## What good looks like

- The axis pointing up reads about +9.8 and flips to about -9.8 upside down
- The Wokwi link runs with 200 ms on and 800 ms off
- The parts photo shows a complete kit

## 1:1 focus this week

Confirm the kit arrived and the battery is charging. Check the laptop can install software. Ask what code they have written before, so you know who needs blocks first in week 3.

## Teacher notes

- Plan the wonder questions from the reveal into week 12. Students love seeing their first questions answered.

## Resources

- phyphox app (phyphox.org)
- Wokwi starter project (wokwi.com)
- Arduino IDE 2 (arduino.cc/en/software)
- Tumbller parts list from Elegoo's manual

---
Previous: [[00-overview]] · Next: [[week-02]]
