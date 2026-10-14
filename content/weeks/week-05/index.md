---
title: Inside the motion sensor
short: The motion sensor
kit: Kit needed
recording:
slides:
---

> How does a chip smaller than a fingernail feel tilt and turning?

## By the end of this week
- What an accelerometer and a gyroscope each measure, and how
- Raw readings from your own robot in a fixed format
- An axis map: which axis is up, which is forward, which sign means tipping forward
- The idea that the gyro is never exactly zero

## Have ready for class
- Robot charged and connected
- Week 1 phone readings to hand

## Assignment

### Must: Six-position test
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

### Must: Convert to g
For two positions, divide each acceleration reading by 16384.

```
CONVERTED (g)
Position          | AccX (g) | AccY (g) | AccZ (g)
Upright           |          |          |
Lying on its back |          |          |
```

### Must: Axis map
Fill in the blanks. This decides the signs in your balance code.

```
AXIS MAP
The ____ axis points from the wheels to the top.
The ____ axis points out of the robot's front.
When the robot tips forward, Gyro____ goes ________ (positive / negative).
```

### Must: Gyro offset
Robot still for 10 seconds. Write the lowest and highest value you see on each gyro axis.

```
GYRO OFFSET (robot still, 10 s)
GyroX: lowest ____  highest ____
GyroY: lowest ____  highest ____
GyroZ: lowest ____  highest ____
Is the gyro ever exactly 0?
```

### Stretch: Shake video
15-second screen recording of the Serial Plotter showing one acceleration axis and one gyro axis while you shake the robot gently, then tilt it slowly. Two lines on what you see.

## Before you submit, check
- In each position one axis reads about ±16000 and the others are near 0
- Signs flip when the robot is upside down
- The axis map agrees with the readings

## Resources
- raw_imu sketch
- MEMS microscope image
- phyphox for comparison
