# RocketFlight
A simple Python 3 script to simulate the flight of a model rocket

## Usage
Simply execute `main.py` to get started -- no external dependencies. You will be prompted by default to enter various parameters, but you can uncomment a section of code at the top to fill them in programatically.

## Parameters
1. The rocket's mass without any motors
2. The rocket's [coefficient of drag](https://en.wikipedia.org/wiki/Drag_coefficient)
3. The rocket's frontal area
4. The parachute's frontal area
5. The local air density
6. The simulation time step
7. The number of clustered rockets
8. A [RASP](https://www.thrustcurve.org/info/raspformat.html) engine file

## Engine file
Find your motor on [thrustcurve.org](https://www.thrustcurve.org/), download the engine file in RASP format, and place it in the same directory as `main.py`. Any commented lines should start with `;`, the header line should have 7 values, and any data points should be indented with spaces.