# Entry test: question bank

_A 4-digit test code picks the questions, so slides and grader always match. "New test" makes a new code for siblings and retests. Code: branch `reference`, `entry-test/entry-gen.js`. Converted 2026-10-15. If a question changes here, change the code too and log both._

## Generated each time (numbers change with the code)

**Part 2, robot path.** "You are the robot." Three moves of 2 to 5 steps with left or right turns, sometimes a final turn. Child says where they end up and which way they face. Answer: steps right or left and toward or away from the screen, plus facing.

**Part 2, number pattern.** Five numbers, find the next, then "How did you get that?" One of four families:
- Growing gaps (the gap grows by 1 or 2 each time)
- Times 2, then add 1, over and over
- Square numbers, sometimes plus a constant
- Each number is the two before it added together

Each has a hint ready, for example "Look at the gaps between the numbers."

**Part 3, gears.** A small gear (8, 10 or 12 teeth) and a big gear (2, 3 or 4 times as many).
- Small drives big: "How many times does the big gear turn? Which gear turns with more force?" (big turns fewer times, with more force; this is why the robot uses geared motors)
- Big drives small: "How many times does the small gear turn? Which gear spins faster?"

**Part 3, wheel distance.** "A robot wheel moves D cm forward every time it turns once" (D is 15 to 50). "How far in N turns? How many turns to go M metres?"

## Picked from a fixed list

## Part 3 bonus: physics stretch questions

1. **Q:** A toy car's wheels spin on a smooth floor, but the car barely moves. Why? What would you change?
   **Answer:** Not enough grip (friction). Rubber tyres, a rougher surface, or more weight on the wheels.
2. **Q:** You drop a cricket ball and a tennis ball from the same height at the same time. Which lands first, and why?
   **Answer:** About the same time. Gravity speeds both up equally. Air slows the light ball very slightly. Most kids say the heavy one.
3. **Q:** Same motor, bigger wheels. Does the robot go faster or slower? What is the catch?
   **Answer:** Faster, because each turn covers more ground. The catch: it needs more force, so it may struggle to start or climb.

## Part 4: draw a circuit

1. **Q:** Draw a battery, a switch and a bulb, so the switch turns the bulb on.
   **Look for:** One closed loop through all three parts.
2. **Q:** Draw one battery, one switch and two bulbs, so the switch turns both bulbs on together.
   **Look for:** The switch sits in the part of the loop both bulbs share.
3. **Q:** Draw one battery, two bulbs and two switches, so each switch controls its own bulb.
   **Look for:** Two separate branches, each with its own switch and bulb.

## Part 4: circuit question

1. **Q:** Two bulbs are in one loop, one after the other. One bulb breaks. What happens to the other one?
   **Answer:** It goes off too. The loop is broken, so no current flows.
2. **Q:** Two bulbs are each in their own loop on the same battery. One bulb breaks. What happens to the other one?
   **Answer:** It stays on. Its own loop is still complete.
3. **Q:** Your torch won't turn on. Name three things you would check.
   **Answer:** Battery dead or in backwards, the bulb, the switch, a loose wire or contact.

## Part 4 bonus: circuit stretch

1. **Q:** A motor spins one way. What happens if you swap its two wires?
   **Answer:** It spins the other way. The current flows backward through it.
2. **Q:** You put the battery into a toy car backwards. What does the motor do?
   **Answer:** It spins the other way, so the car drives backward.
3. **Q:** You connect an LED the wrong way round. What happens, and why?
   **Answer:** It doesn't light. An LED only lets current flow one way.

