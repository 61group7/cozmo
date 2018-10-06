"""

Cozmo Cube Return (No Obstacle Detection)
	
	Copyright (C) 2018 -

	This program is part of the cie-111g7/cozmo project on GitHub.

	This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

	This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

	See <https://www.gnu.org/licenses/>.

"""
try:
	import asyncio, functools, math, sys, cozmo, cv2, time, os
	import numpy as np
	from matplotlib import pyplot
	from cozmo.util import degrees, distance_mm, radians, speed_mmps, Vector2
	from cozmo.lights import Color, Light
	from PIL import Image, ImageColor, ImageDraw, ImageStat
except ImportError:
	print("You are missing required packages!")
	print("You need: Cozmo, Matplotlib, Pillow, OpenCV")
	input()
	sys.exit()

def fip(robot, af):
	ok = False
	for i in range(10):
		try:
			FoundCube = robot.world.wait_for_observed_light_cube(timeout=1)
			if FoundCube not in af:
				ok = True
				break
			else:
				FoundCube = None
		except asyncio.TimeoutError:
			pass
		robot.turn_in_place(degrees(36)).wait_for_completed()
	return FoundCube, ok

def cube_return(robot):	
	
	robot.camera.color_image_enabled = True

	stordist = 200
	storstep = 50
	num_cubes = 3

	if robot.is_on_charger == False:
		robot.say_text("Place on charger!", voice_pitch=-1, duration_scalar=0.5).wait_for_completed()
		while robot.is_on_charger == False:
			time.sleep(1)

	charger = robot.world.charger
	
	robot.drive_off_charger_contacts().wait_for_completed()
	robot.drive_straight(distance_mm(120), speed_mmps(100)).wait_for_completed()
	cozmo.world.World.request_nav_memory_map(robot, 1)
	robot.set_lift_height(0.0).wait_for_completed()
	robot.set_head_angle(degrees(0.0)).wait_for_completed()

	af = list()

	for i in range(num_cubes):

		findcube, ok = fip(robot, af)
		af.append(findcube)
		
		if ok == True:
			robot.pickup_object(findcube, num_retries=3).wait_for_completed()
			robot.go_to_object(charger, distance_mm(75)).wait_for_completed()
			cozmo.robot.robot_alignment.RobotAlignmentTypes.Body = charger
			robot.turn_in_place(degrees(90)).wait_for_completed()
			robot.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()
			robot.turn_in_place(degrees(-90)).wait_for_completed()
			robot.drive_straight(distance_mm(stordist),speed_mmps(50)).wait_for_completed()
			robot.set_lift_height(0).wait_for_completed()
			robot.drive_straight(distance_mm(-stordist),speed_mmps(50)).wait_for_completed()
			stordist -= storstep

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(cube_return, use_viewer=True)