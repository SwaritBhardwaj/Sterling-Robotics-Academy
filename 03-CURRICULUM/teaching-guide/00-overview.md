---
tags: [curriculum, teaching-guide]
---
> Teacher-facing. Converted from `sterling-teaching-guide.html` (the HTML teaching guide) on 2026-10-15. This Markdown copy is now the source; the HTML is kept in the `reference` branch.

# How this cohort is taught

By week 11, every robot stands on its own for 30 seconds and recovers from three taps.
Not in this cohort: wheel encoders, speed control, driving around. Optional in week 12: stopping with the ultrasonic sensor, and Bluetooth control. Without encoders the robot drifts slowly while balancing. That is expected; the bar is standing, not staying in one spot.

## The robot, week by week

- **Week 1:** Explains sense, decide, act (Why balancing is hard)
- **Week 2:** Robot built and running (Build the robot)
- **Week 3:** Writes variables and if/else (Code I)
- **Week 4:** Loops, prints and fixes errors (Code II)
- **Week 5:** Reads raw motion data (The motion sensor)
- **Week 6:** Knows its tilt and distance (Tilt angle and distance)
- **Week 7:** Wheels follow tilt (Motors and PWM)
- **Week 8:** First stand (Control: P and D)
- **Week 9:** Stands 15 s, stops safely (Balance point and I)
- **Week 10:** Stands 30 s, survives a push (Push recovery)
- **Week 11:** Submitted (Submission)
- **Week 12:** Final video and demo day (Demo day)

## How we teach

Every class is inquiry-led. Students meet a puzzle, try things, and form ideas before we name the concept. Use these five rules in every class.

- **Ask before you tell.** Show the thing happening, ask "What do you notice? What do you wonder?", and only then name the idea.

- **Predict before every run.** Students type a prediction in chat before code runs or a demo starts. A wrong prediction followed by a test teaches more than a right answer given.

- **Answer a question with a question, for 30 seconds.** "What did the Serial Monitor say?" "What changed since it last worked?" Then help.

- **Treat wrong answers as data.** Don't say "no". Say "If that were true, what would we see? Let's test it."

- **Name the concept after they have felt it.** The broom comes before the control loop. The flashlight comes before PWM.

## The five phases in each run of show

- **Engage:** A puzzle, a demo or a failure that makes them curious

- **Explore:** Hands on: they try, measure and predict

- **Explain:** You name what they found, with an analogy

- **Elaborate:** They apply it to the robot

- **Evaluate:** Exit question, then the assignment

## Running a class of 50 online

- **Chat waterfall.** Everyone types an answer, nobody presses Enter until you say go. Every student answers, not only the fastest.

- **Polls** for every prediction with a clear set of answers.

- **Second camera.** Students join from their phone as well, muted, pointing at their hands and robot.

- **Checkpoint photos** in the chat during builds and hands-on blocks, so you can see who is stuck.

- **Breakout rooms** of 6 to 8 with a mentor for build, coding practice and tuning.

- **Record every class.** Students who miss one, or whose kit arrives late, catch up from the recording and their 1:1.

## The weekly rhythm

Sunday**Live class**Up to 90 minutes, recorded

Sunday evening**Assignment posted**Tasks, formats and starter files

Mon to Fri**30-minute 1:1**With you or a mentor

Saturday 8 PM ET**Submission due**Two or three strong ones are shown next class, with permission

## How assignments work

### Sharing

- One post per week in Google Classroom, up by Sunday evening.

- Each post has the task list, the formats to copy, and the starter files.

- Tasks are small. Plan for 1 to 4 hours a week: Must tasks first, then optional Stretch tasks.

### Submitting

- Code as an .ino file named like W05_AnyaS.ino.

- Readings pasted as text in the given format, not screenshots, unless the task asks for one.

- Videos uploaded straight from the phone: landscape, under 60 seconds unless stated, whole robot in frame.

### Reviewing

- Mark each Must task Done or Redo within 48 hours.

- Give the deeper feedback in the 1:1.

### Late work

- Catch up in the 1:1, no penalty.

- Week 11 is the hard deadline.

## Class length

Every plan runs 85 to 90 minutes. Blocks marked "Trim if short" can go when a class has 50 to 60 minutes; switch on "Short class" at the top to see that version with its timings. Weeks 2 and 8 should not run short. Below 45 minutes, move the Elaborate block into the 1:1.

Holiday breaks: post an optional challenge and no new content. Restart with a 5-minute recap of the last class.

## Tools

| Tool | Used in | Cost |
|---|---|---|

| phyphox app | Weeks 1, 6 | Free |

| Wokwi (browser Arduino simulator) | Week 1 | Free |

| Tinkercad Circuits (blocks and text) | Weeks 3, 7 | Free, account needed |

| Arduino IDE 2 | Weeks 2 to 12 | Free |

| Elegoo Tumbller manual and code pack | Weeks 2, 5, 7 | Comes with the kit |

| Google Classroom | Every week | Free |

## Starter files to prepare

Write and test each one on a real Tumbller before its week. Pin numbers and libraries come from Elegoo's code pack.

| Week | File | What it does |
|---|---|---|

| 1 | Wokwi starter | Nano, LED and MPU6050; blinks and prints sensor values |

| 2 | hello | Proves an upload works |

| 3 | Three Tinkercad circuits, snippets A to D | LED, button, potentiometer tilt alarm; predict-the-output |

| 4 | Two bug hunt sketches | Five bugs each, one of them a logic bug |

| 5 | raw_imu | Prints six raw sensor values every 100 ms |

| 6 | tilt_angle, ultrasonic | Three angles for the plotter; distance in cm |

| 7 | motor_test | setMotor(side, speed) helper and a PWM sweep |

| 8 | balance_stub | Control loop with blanks for error, P, D and the limit |

| 9 | Stub additions, angle-only sketch | Target angle, cut-off, dead zone, I |

## Weeks

- [[week-01|Week 1: Why is balancing hard?]]
- [[week-02|Week 2: Build the robot]]
- [[week-03|Week 3: Statements, variables and conditions]]
- [[week-04|Week 4: Loops, the Serial Monitor and debugging]]
- [[week-05|Week 5: Inside the motion sensor]]
- [[week-06|Week 6: A clean tilt angle, and how distance is measured]]
- [[week-07|Week 7: Actuators: PWM and the motor driver]]
- [[week-08|Week 8: Control: P and D]]
- [[week-09|Week 9: Balance point, safety cut-off and I]]
- [[week-10|Week 10: Push recovery: tuning and debugging]]
- [[week-11|Week 11: Submission week]]
- [[week-12|Week 12: Iterate, final video and demo day]]
