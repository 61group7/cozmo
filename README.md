Cozmo Cube Finding Project
------

This robot has about as much of a chance at changing the world as bitcoin does  
**This is a WIP project, and as such does not currently function.**
----
##### Hardware Requirements
- 2 Cozmo robots. One needs to be outfitted with rangefinding capabilities
- Rangefinding requires ESP8266 or equivalent Wi-Fi enabled microcontroller.
- iOS/Android device connected to Cozmo in SDK mode.
- x86-based machine with Python installed.
##### Software Requirements 
*Arduino IDE required for flashing microcontroller board.*  
*Tested only on Python 3.7.*  
Modules required:
`python-pathfinding`
`opencv-python`
`paho-mqtt`
`cozmo`
`numpy`
`tkinter`
`pillow`
---

#### Usage
1. Specify the length of the square maze to be explored, in mm.
2. Place the charger on the top-left side of the maze, then place the scouting, sensor-equipped Cozmo on it.
3. Once it's done searching, place the second rescue Cozmo on the charger.
4. If everything works out, Cozmo should return the cubes to the drop-off point.
---
This software is licensed under Version 3 of the GNU General Public License.
