---
week: 5
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 5: Inside the motion sensor

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-05/index.md`.

**Driving question:** How does a chip smaller than a fingernail feel tilt and turning?

| | |
|---|---|
| Class length | 90 min, 75 min short |
| Robot by the end of the week | Reads raw motion data |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students learn what is inside the MPU6050 (an accelerometer and a gyroscope), read raw values from their robot, and work out by experiment which axis points where. The axis map they build here decides the signs in their balance code.

Students leave with:
- What an accelerometer and a gyroscope each measure, and how
- Raw readings from their own robot in a fixed format
- An axis map: which axis is up, which is forward, which sign means tipping forward
- The idea that the gyro is never exactly zero

## Before class

You prepare:
- raw_imu sketch: prints AccX, AccY, AccZ, GyroX, GyroY, GyroZ every 100 ms, tested with the library from Elegoo's pack
- Find the axis map on your own robot so you can check answers
- A microscope image of a MEMS accelerometer to show
- A box with a ball on rubber bands, or a sketch of one

Students bring:
- Robot charged and connected
- Week 1 phone readings to hand

## Run of show (90 min)

### 0 to 5 min · Engage: Show last week _(trim if short)_

Show one great bug log and ask its owner which bug took longest.

### 5 to 15 min · Engage: Back to the 9.8

Bring back the week 1 question: why does a still phone read 9.8? Collect theories. Then describe a closed box with a ball hanging inside on rubber bands. Tilt the box and the ball shifts toward the floor.

Ask:
- If you were in a closed box with no windows, how would you know which way is down?
- What would the ball do if the box were falling freely?

### 15 to 30 min · Explain: What is inside the chip

The accelerometer is a tiny mass on tiny springs, carved into silicon. When gravity or movement pulls the mass, the gap between tiny plates changes, and the chip measures that gap. On a table gravity pulls it down, so the axis pointing up reads 1 g (9.8 m/s²). The gyroscope has a tiny mass that vibrates. When the chip rotates, the vibrating mass gets pushed sideways, and that push tells it how fast it is turning, in degrees per second. The chip talks to the Arduino over two wires called I2C: one carries data (SDA), one keeps the beat (SCL).

Ask:
- Which sensor tells you which way is down?
- Which one tells you how fast you are turning?

### 30 to 55 min · Explore: Find your axes

Upload raw_imu. In raw numbers, about 16384 means 1 g and about 131 means 1 degree per second. Investigation 1: hold the robot upright, then lay it on its back, its front and each side. Each time, which axis reads about 16000? Investigation 2: robot still on the table. Is the gyro exactly zero? Now tip it forward slowly, then fast. Which gyro axis changes, and is it positive or negative?

Ask:
- Which axis points from the wheels to the top of the robot?
- Which axis points out of its nose?
- Tipping forward: which gyro axis moves, and with which sign?

### 55 to 70 min · Elaborate: Shake test

Students add conversion lines: divide acceleration by 16384 to get g, and gyro by 131 to get degrees per second. Open the Serial Plotter with one acceleration axis and one gyro axis. Tilt slowly, then tap the table, then shake the robot without tilting it.

Ask:
- You shook it without tilting it. Which line went wild?
- Which sensor would you trust to say the robot is falling?
- The accelerometer knows which way is down but jitters. The gyro is smooth but only knows turning speed. Could we combine them?

### 70 to 80 min · Explore: Gyro offset _(trim if short)_

Robot still. Average 100 gyro readings, then subtract that average from every reading after. Watch the still readings settle near zero.

### 80 to 90 min · Evaluate: Exit question and assignment



Ask:
- Robot lying perfectly still. What does the accelerometer say? What does the gyro say?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| Still means the accelerometer reads zero. | It reads gravity. Only in free fall would it read zero. |
| The gyro tells you the angle. | It tells you turning speed. To get an angle you add up speed over time, which is week 6. |
| Positive always means forward. | The sign depends on how the chip is mounted. That is why everyone makes an axis map. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Six-position test

Hold the robot still in each position for 3 seconds and copy one line of readings.

```
IMU RAW READINGS (raw units)
Position: upright (held still)
AccX: ______  AccY: ______  AccZ: ______
GyroX: _____  GyroY: _____  GyroZ: _____

Position: lying on its back
AccX: ______  AccY: ______  AccZ: ______
GyroX: _____  GyroY: _____  GyroZ: _____

Position: lying on its front
AccX: ______  AccY: ______  AccZ: ______
GyroX: _____  GyroY: _____  GyroZ: _____

Position: on its left side
AccX: ______  AccY: ______  AccZ: ______
GyroX: _____  GyroY: _____  GyroZ: _____

Position: on its right side
AccX: ______  AccY: ______  AccZ: ______
GyroX: _____  GyroY: _____  GyroZ: _____

Position: upside down
AccX: ______  AccY: ______  AccZ: ______
GyroX: _____  GyroY: _____  GyroZ: _____
```

### Must · T2: Convert to g

For two positions, divide each acceleration reading by 16384.

```
CONVERTED (g)
Position          | AccX (g) | AccY (g) | AccZ (g)
Upright           |          |          |
Lying on its back |          |          |
```

### Must · T3: Axis map

Fill in the blanks. This decides the signs in your balance code.

```
AXIS MAP
The ____ axis points from the wheels to the top.
The ____ axis points out of the robot's front.
When the robot tips forward, Gyro____ goes ________ (positive / negative).
```

### Must · T4: Gyro offset

Robot still for 10 seconds. Write the lowest and highest value you see on each gyro axis.

```
GYRO OFFSET (robot still, 10 s)
GyroX: lowest ____  highest ____
GyroY: lowest ____  highest ____
GyroZ: lowest ____  highest ____
Is the gyro ever exactly 0?
```

### Stretch · T5: Shake video

15-second screen recording of the Serial Plotter showing one acceleration axis and one gyro axis while you shake the robot gently, then tilt it slowly. Two lines on what you see.

## What good looks like

- In each position one axis reads about ±16000 and the others are near 0
- Signs flip when the robot is upside down
- The axis map agrees with the readings

## 1:1 focus this week

Go through the axis map line by line. The forward axis and its sign decide the signs in the balance code. A wrong sign here means a robot that runs away in week 8.

## Teacher notes

- Don't hand out the axis map. Finding it is the lesson.
- The raw scale assumes the default ranges: ±2 g (16384 per g) and ±250 degrees per second (131 per degree per second). If your library changes the range, change these numbers.

## Resources

- raw_imu sketch
- MEMS microscope image
- phyphox for comparison

---
Previous: [[week-04]] · Next: [[week-06]]
