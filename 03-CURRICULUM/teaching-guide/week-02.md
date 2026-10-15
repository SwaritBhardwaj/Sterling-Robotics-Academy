---
week: 2
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 2: Build the robot

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-02/index.md`.

**Driving question:** What does each part of the robot do in the sense, decide, act loop?

| | |
|---|---|
| Class length | 90 min (keep it full length) |
| Robot by the end of the week | Robot built and running |
| Assignment due | Saturday, 8 PM ET |

## Goal

Every robot assembled, powered and running Elegoo's demo. Students can name each main part's job, and every board connects to a laptop and accepts an upload.

Students leave with:
- A built robot they have seen balance
- A 10-second video of it balancing
- The proof that power off means it falls, so the code does the balancing
- A working upload from Arduino IDE

## Before class

You prepare:
- Your own unbuilt kit for the live build, under an overhead or phone camera
- Practise the build once and split Elegoo's manual into four stages
- Record your full build in advance for students whose kit arrives late
- Mentors assigned to breakout rooms, about one per 8 students
- A photo of the screws sorted by size
- Hello sketch ready to upload

Students bring:
- Kit unboxed and checked, battery charged
- A clear table, the screwdriver from the kit, a small bowl for screws
- Phone joined to the call as a second camera pointing at their hands, muted
- Laptop with Arduino IDE 2 installed and a USB cable that carries data

## Run of show (90 min)

### 0 to 8 min · Engage: Guess the parts

Lay the parts out on camera. Hold up each main part: control board, motion sensor (on the board), motors, battery, ultrasonic sensor. Students guess its job in chat. Don't correct anyone yet.

Ask:
- Which part is the robot's eyes? Brain? Hands?
- Which part is the heaviest? Where should it go?

### 8 to 15 min · Explain: Build rules

Battery out during the build. Don't overtighten screws into acrylic; it cracks. Keep every wire away from the wheels. Post a checkpoint photo in the chat after each stage. Anyone who falls behind goes to a breakout room with a mentor.

### 15 to 65 min · Explore: Build-along in four stages

Build your own kit on the overhead camera, one stage at a time, about 12 minutes each. Split Elegoo's manual at natural breaks: (1) motors and wheels on the base, (2) standoffs and control board, motor cables plugged in, (3) upper plates and ultrasonic sensor, (4) battery, wire tidy and final check. Confirm this order against your practice build. Ask one question per stage while hands are busy.

Ask:
- Why do the motors sit at the very bottom?
- The motion sensor must never wobble. Why might that matter?
- Remember the broom. Would a taller robot be easier or harder to balance?
- Why only two wheels? What would a third wheel change?

### 65 to 75 min · Elaborate: Power on

Battery in, switch on, Elegoo's demo runs and the robot balances. Everyone records a 10-second video now, before uploading anything new. Then switch it off, stand it up and let go. It falls at once.

Ask:
- It balances with power on and falls with power off. So what is doing the balancing?
- Every moment, what does the code need to know?

### 75 to 85 min · Evaluate: Connect to the laptop

In Arduino IDE, select the board and port as Elegoo's tutorial says (some Nano boards need "ATmega328P (Old Bootloader)"). Warn them first: uploading replaces Elegoo's demo, which stays in the resource pack. Upload the hello sketch. Checkpoint: "Done uploading" on screen.

### 85 to 90 min · Evaluate: Assignment

Walk through the tasks. Close with: "Next week we start writing our own robot brain. By week 10 yours will balance with code you wrote."

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| The robot balances because it is built well. | Switch it off and let go. It falls instantly. The code does the balancing. |
| The ultrasonic sensor helps it balance. | It only measures distance ahead. The motion sensor on the board does the balancing work. |
| Tighter screws are always better. | Acrylic cracks. Snug is enough. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Build photos

Front, side and top photos. Whole robot in frame, good light.

### Must · T2: Demo video

10 seconds of the robot balancing on Elegoo's demo, recorded in class. If you missed it, re-upload Elegoo's code from the resource pack and record it.

### Must · T3: Label the robot

For each part, say which job it does in the loop and what you think it does.

```
LABEL THE ROBOT
Part           | Sense / Decide / Act / Power | What I think it does
Control board  |                              |
Motion sensor  |                              |
Motor driver   |                              |
Motors         |                              |
Battery        |                              |
Ultrasonic     |                              |
```

### Must · T4: Upload proof

Screenshot of "Done uploading" in Arduino IDE.

### Stretch · T5: Fall test

Power off, stand the robot upright and let go five times while filming in slow motion. Estimate how long each fall takes. Compare with the broom from week 1.

## What good looks like

- Photos show wires clear of the wheels and no loose plates
- Every row of the label table has a guess
- Upload screenshot shows "Done uploading"

## 1:1 focus this week

Fix anything the photos show: loose screws, wires near wheels, a wobbling board. Students whose kit arrived late build here with your recorded build video.

## Teacher notes

- Don't run this class short. The build needs the full 50 minutes.
- Common upload problems: a charge-only USB cable, a missing USB driver (many Nano boards use a CH340 chip), the wrong processor setting.
- Check whether your Tumbller came with the demo preloaded. If not, run a guided upload of Elegoo's demo at the start of the Power on block, which adds about 10 minutes.

## Resources

- Elegoo Tumbller manual and code pack
- Your recorded build video
- Hello sketch

---
Previous: [[week-01]] · Next: [[week-03]]
