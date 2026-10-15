---
week: 6
kit: Kit needed
tags: [curriculum, teaching-guide]
---
# Week 6: A clean tilt angle, and how distance is measured

> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. Student version of this week lives in the site repo: `content/weeks/week-06/index.md`.

**Driving question:** How can the robot know its exact tilt when one sensor jitters and the other drifts?

| | |
|---|---|
| Class length | 90 min, 75 min short |
| Robot by the end of the week | Knows its tilt and distance |
| Assignment due | Saturday, 8 PM ET |

## Goal

Students run the tilt-angle code you give them, check it against their phone, and understand why we mix the two sensors. In the second half they learn how the ultrasonic sensor times an echo to measure distance.

Students leave with:
- A tilt angle they trust, checked against a phone
- The idea behind the filter: trust the gyro now, let the accelerometer correct it slowly
- How the ultrasonic sensor turns an echo into centimetres, and where it fails

## Before class

You prepare:
- tilt_angle sketch printing three angles (accelerometer only, gyro only, filtered), comma-separated for the Serial Plotter
- ultrasonic sketch
- phyphox "Inclination" on your phone
- Ruler or tape measure, a flat wall or a piece of cardboard

Students bring:
- Robot charged and connected
- phyphox installed
- Ruler, a pillow and a book

## Run of show (90 min)

### 0 to 5 min · Engage: Agree on the axis map _(trim if short)_

Show two students' axis maps. Agree as a class which axis is forward on the Tumbller and which sign means tipping forward.

### 5 to 15 min · Engage: Two witnesses

Witness A saw the accident but is shaky and exaggerates every detail. Witness B is calm and precise but slowly forgets. Who do you believe?

Ask:
- Who would you trust from moment to moment?
- Who would you use to correct the other over a longer time?

### 15 to 35 min · Explore: Three lines on the plotter

Upload tilt_angle. The Serial Plotter shows three lines: angle from the accelerometer only, angle from the gyro only, and the filtered angle. Three experiments: hold the robot still at a tilt; leave it still on the table for two minutes; tap and shake it gently.

Ask:
- Describe each line in one word.
- Which line drifts when nothing moves?
- Which line would you want controlling the motors? Why?

### 35 to 50 min · Explain: How the filter works

Accelerometer angle: the chip works out the angle from how gravity splits between two axes. Gyro angle: add up turning speed × time, every loop. Filter: new angle = 98% of (old angle + gyro change) + 2% of the accelerometer angle. It trusts the gyro from moment to moment and lets the accelerometer pull it back slowly. Then let them change 0.98 to 0.5 and to 1.0 and watch.

Ask:
- What happens at 1.0? At 0.5?
- Why 98 and 2, and not 50 and 50?

### 50 to 60 min · Elaborate: Check against the phone _(trim if short)_

Lay the phone, running phyphox "Inclination", against the robot. Tilt both together to 0, 10, 20 and 30 degrees and compare.

### 60 to 80 min · Explore: Ultrasonic: how a bat sees

Ask how bats fly in the dark. The sensor's speaker sends a 40 kHz chirp humans can't hear, and its microphone listens for the echo. The Arduino times the round trip. Sound travels about 343 metres a second, which is 0.0343 cm per microsecond, so distance = time × 0.0343 ÷ 2. Upload the ultrasonic sketch. Measure a wall at 10, 20 and 30 cm, then try a pillow, a book held at an angle, and a hand.

Ask:
- Why divide by 2?
- Which surfaces fool it? Why?

### 80 to 90 min · Evaluate: Exit question and assignment



Ask:
- Why can't the robot balance using only the accelerometer?

## Common wrong ideas

| Students often think | What we show them |
|---|---|
| The filtered angle is the average of the two. | It trusts the gyro for quick changes and uses the accelerometer to correct drift slowly. |
| The ultrasonic sensor sees everything in front of it. | It sees a cone. Soft or angled surfaces absorb or deflect the echo. |
| 0° on screen means the robot is balanced. | The robot's balance point is usually a few degrees off zero. We find it in week 9. |

## Assignment (due Saturday 8 PM ET)

### Must · T1: Tilt check

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

### Must · T2: Drift test

Leave the robot still for 2 minutes.

```
DRIFT TEST (2 minutes, robot still)
Gyro-only angle:  start ____  end ____
Filtered angle:   start ____  end ____
Why I think they differ:
```

### Must · T3: Filter experiment

Run the sketch with 0.98, 0.80 and 1.00. Submit a Serial Plotter screenshot of each and one line on what changed.

### Must · T4: Ultrasonic check

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

### Stretch · T5: Two sensors, one decision

Print "TOO CLOSE" when something is nearer than 15 cm and the robot is tilted more than 20°. One if statement, two sensors.

## What good looks like

- Filtered angle within about 2° of the phone
- Filtered angle barely drifts in two minutes; the gyro-only angle drifts
- Ultrasonic within about 1 cm on a flat, hard wall

## 1:1 focus this week

Confirm which sign the angle takes when tipping forward and write it on their tuning sheet. Week 8 depends on it.

## Teacher notes

- Students don't derive the filter. They use it, test it and explain the idea in their own words.

**The three lines that matter in tilt_angle**

```
accAngle  = atan2(accY, accZ) * 180 / PI;   // axes depend on your axis map
gyroAngle = gyroAngle + gyroRate * dt;      // drifts over time
angle     = 0.98 * (angle + gyroRate * dt) + 0.02 * accAngle;

// ultrasonic
distanceCm = durationMicros * 0.0343 / 2;
```

## Resources

- tilt_angle sketch
- ultrasonic sketch
- phyphox "Inclination"

---
Previous: [[week-05]] · Next: [[week-07]]
