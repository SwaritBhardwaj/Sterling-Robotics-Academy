# Hints (private: never copied to public files)

## 01-balance-lab
1. Keep your eyes on the top of the object, not on your hand. Start the timer when you take your other hand away.
2. Use your phone's stopwatch. If a try lasts under 1 second, write 0.5. Every number counts, even short ones.
3. For your guess: a longer object tips over more slowly, so your hand has more time to move under it. Write that idea in your own words.

## 02-phone-sensor-readings
1. Press the play triangle in phyphox first. The numbers only move while it is recording.
2. In each position, one axis shows about 9.8 or -9.8 and the other two stay near 0. That axis is the one pointing up or down.
3. Flat and screen up, Z is about +9.8. Screen down, Z is about -9.8. So Z points out of the screen.

## 03-run-the-starter
1. The play button is the green triangle at the top of the simulation. To share, use the Save button, then Share, then copy the link.
2. 100 ms is ten times shorter than 1000 ms. So the LED will blink ten times faster.
3. Change both `delay(1000)` lines to `delay(100)`. The LED flickers fast. Write your guess first, then what you saw.

## 04-heartbeat-blink
1. There are two `delay` lines. One is after the LED turns on, one is after it turns off.
2. The delay after `HIGH` is the "on" time. The delay after `LOW` is the "off" time.
3. Set the first `delay` to 200 and the second to 800. Press play, check it, then Save and Share.

## 05-kit-ready
1. The parts list is in the Elegoo manual that comes in the box (and as a PDF on Elegoo's site).
2. Lay every part on a plain table so they don't overlap, then take the photo from above.
3. Charge with the cable in the box until the light changes colour. Arduino IDE 2 is free from arduino.cc/en/software.

## 06-balancing-machines
1. Think of anything that stays upright or level by itself: a Segway, a hoverboard, a drone, a SpaceX booster landing, even a cat.
2. Sense: what does it measure? Decide: what works out the correction? Act: what moves?
3. Example: a drone. Sense: a motion sensor feels tilt. Decide: a small computer works out the correction. Act: the propellers speed up or slow down.
