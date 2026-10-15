---
title: Your first code in Wokwi
type: article
minutes: 5
---
Wokwi runs an Arduino inside your browser. No kit needed. The starter project has an Arduino Nano, an LED and a motion sensor.

## The two lines that matter
```
digitalWrite(LED_PIN, HIGH);  // LED on
delay(1000);                  // wait 1000 ms
digitalWrite(LED_PIN, LOW);   // LED off
delay(1000);                  // wait 1000 ms
```
`delay(1000)` makes the Arduino wait 1000 milliseconds. That is one second. The code then jumps back to the top and runs again, forever. That repeating part is called the **loop**, just like sense, decide, act.

## Predict, then run
Before you change a number, guess what will happen. Then press play and check. A wrong guess you test teaches you more than a right answer you are told.

## Quick quiz
1. What does `delay(1000)` do?
   - Waits 1 second
   - Waits 1000 seconds
   - Turns the LED on
2. You want the LED on for 200 ms and off for 800 ms. What do you change?
   - Both numbers to 500
   - The first delay to 200 and the second to 800
   - The LED pin number
