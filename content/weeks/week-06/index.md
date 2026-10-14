---
title: A clean tilt angle, and how distance is measured
short: Tilt angle and distance
kit: Kit needed
recording:
slides:
---

> How can the robot know its exact tilt when one sensor jitters and the other drifts?

## By the end of this week
- A tilt angle you trust, checked against a phone
- The idea behind the filter: trust the gyro now, let the accelerometer correct it slowly
- How the ultrasonic sensor turns an echo into centimetres, and where it fails

## Have ready for class
- Robot charged and connected
- phyphox installed
- Ruler, a pillow and a book

## Assignment

### Must: Tilt check
Compare the robot's filtered angle with the phone at each angle.

```
TILT CHECK
Phone angle (°) | Robot filtered angle (°) | Difference
0               |                          |
10              |                          |
20              |                          |
30              |                          |
-10             |                          |
-20             |                          |
```

### Must: Drift test
Leave the robot still for 2 minutes.

```
DRIFT TEST (2 minutes, robot still)
Gyro-only angle:  start ____  end ____
Filtered angle:   start ____  end ____
Why I think they differ:
```

### Must: Filter experiment
Run the sketch with 0.98, 0.80 and 1.00. Submit a Serial Plotter screenshot of each and one line on what changed.

### Must: Ultrasonic check
Measure with a ruler, then with the sensor.

```
ULTRASONIC CHECK
Real distance (cm) | Sensor reading (cm) | Difference
10                 |                     |
20                 |                     |
30                 |                     |
50                 |                     |

Surface test (real distance ____ cm)
Pillow: ____ cm   Tilted book: ____ cm   Hand: ____ cm
```

### Stretch: Two sensors, one decision
Print "TOO CLOSE" when something is nearer than 15 cm and the robot is tilted more than 20°. One if statement, two sensors.

## Before you submit, check
- Filtered angle within about 2° of the phone
- Filtered angle barely drifts in two minutes; the gyro-only angle drifts
- Ultrasonic within about 1 cm on a flat, hard wall

## Resources
- tilt_angle sketch
- ultrasonic sketch
- phyphox "Inclination"
