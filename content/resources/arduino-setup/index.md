---
title: Set up Arduino IDE 2
---

## Install
1. Download Arduino IDE 2 from [arduino.cc/en/software](https://www.arduino.cc/en/software) for your computer.
2. Install it and open it once before class.

## Connect the robot
1. Use a USB cable that carries data. Many phone charging cables only carry power, and the board will not show up.
2. Plug the robot's board into your laptop.
3. In **Tools > Board**, pick **Arduino Nano**.
4. In **Tools > Processor**, pick **ATmega328P (Old Bootloader)** if the normal option fails to upload.
5. In **Tools > Port**, pick the port that appears when you plug the robot in.

## If the upload fails
- **No port appears:** try another cable first. If it still fails, install the CH340 USB driver, which many Nano boards need.
- **"not in sync" or timeout errors:** switch the processor setting between the two ATmega328P options and try again.
- **Still stuck:** take a screenshot of the full error and post it on the class group.

Uploading your own code replaces Elegoo's demo. The demo code is in the week 2 files if you want it back.
