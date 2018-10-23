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
	import copy
	from multiprocessing import Process
	from matplotlib import pyplot as plt
	from cozmo.util import degrees, distance_mm, radians, speed_mmps, Vector2
	from cozmo.lights import Color, Light
	from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
	from PIL import Image, ImageColor, ImageDraw, ImageStat
except ImportError:
	print("You are missing required packages!")
	print("You need: Cozmo, Matplotlib, Pillow, OpenCV, Numpy")
	input()
	sys.exit()

locs = dict()
plstat = False

def handle_object_appeared(evt, **kw):
	
	# Locs is Cozmo's global object location database.
	# Plstat is for multithreading in future;
	# where it will wait for this value to be True before pinging the robot.
	global locs, plstat
	
	# Clear the graph. Quick and dirty solution, doesn't seem to work with annotation.
	plt.clf()

	# Update the location database with the new observed object (why this function was called).
	locs.update({evt.obj.object_id: [evt.obj.pose.position.x, evt.obj.pose.position.y]})
	plot_points = list()
	pts_x, pts_y = list(), list()

	# Create x and y plots for matplotlib.
	for key in locs:
		pts_x.append(locs[key][0])
		pts_y.append(locs[key][1])

	# Create a scatter plot using the points we made, label the x and y axes, draw the graph, and pause for 1ms.
	# Since we only have asyncio to work with at the moment, this isn't an ideal solution, but it is the only one that doesn't pause Cozmo.
	plt.scatter(pts_x, pts_y, label='Cozmo 2D Graph')
	plt.xlabel('xpos')
	plt.ylabel('ypos')
	plt.draw()
	plt.pause(0.001)
	
	# Debugging code:
	# print(locs)

# FIP - Find In Place
def fip(robot, af):

	# Status flag.
	ok = False
	
	"""
	We wait for Cozmo to find a cube in its view for 500ms.
	If that is unsuccessful, we turn the robot so its camera view is moved by 36 degrees,
	and we try this again and again until we find cubes.
	"""

	for i in range(10):
		
		# If Cozmo does not find a light cube an exception occurs, so we catch that and say no cubes were found.
		try:
			FoundCube = robot.world.wait_for_observed_light_cube(timeout=0.5)
			# We want the cubes we find to be ones we didn't return yet, so we exclude the ones in the af list we made.
			if FoundCube not in af:
				ok = True
				break
			else:
				FoundCube = None
		except asyncio.TimeoutError:
			pass
		robot.turn_in_place(degrees(36)).wait_for_completed()
	return FoundCube, ok

# Main program to return the cubes to base.
def cube_return(robot):

	# Call functions every time an event happens.
	robot.add_event_handler(cozmo.objects.EvtObjectAppeared, handle_object_appeared)
	
	# Testing variables
	# dropoff = robot.world.define_custom_cube(CustomObjectTypes.CustomType00, CustomObjectMarkers.Hexagons2, 44, 30, 30, True)
	# robot.camera.color_image_enabled = True

	# Maximum storage distance from the storage position for the cubes.
	stordist = 200
	
	# Separation distance between each of the stored cubes.
	storstep = 50
	
	# Number of cubes to pick up.
	num_cubes = 3

	# Check if robot is on charger, our designated starting point.
	if robot.is_on_charger == False:
		robot.say_text("Off charger.", voice_pitch=-1, duration_scalar=0.5).wait_for_completed()
		
		# Wait until robot is on charger.
		while robot.is_on_charger == False:
			time.sleep(1)

	# Abbreviate 'robot.world.charger' to 'charger'.
	charger = robot.world.charger
	
	# Drive off the charger and save the position for docking back into the charger later.
	robot.drive_off_charger_contacts().wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	cdpos = copy.deepcopy(robot.pose)
	locs.update({"charger_dock": [robot.pose.position.x, robot.pose.position.y]})

	# Move to the dropping position (predefined) and save this position for later.
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	drop = copy.deepcopy(robot.pose)
	locs.update({"drop": [robot.pose.position.x, robot.pose.position.y]})

	# Go to the scanning point and put the lift and head into their resting positions.
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	robot.set_lift_height(0.0).wait_for_completed()
	robot.set_head_angle(degrees(0.0)).wait_for_completed()
	
	# The list of already found objects.
	af = list()
	
	# Finding subroutine
	# Repeat the finding subroutine for the cube count.
	
	for i in range(num_cubes):

		"""
		Run the Find In Place subroutine.
		We need to pass 'robot' and 'af' so fip();
		can control the robot directly (robot),
		and knows what it's already found (af).
		"""

		findcube, ok = fip(robot, af)
		af.append(findcube)
		
		if ok == True:
			# If cubes are found, we remember where we were standing last so we can search for the rest.
			prev = copy.deepcopy(robot.pose)
			locs.update({"search_pos": [robot.pose.position.x, robot.pose.position.y]})

			# Call the pickup_object subroutine (self-explanatory).
			x = robot.pickup_object(findcube, use_pre_dock_pose=False, in_parallel=False, num_retries=5).wait_for_completed()
			
			# Go to the drop off point and drive in using the stor parameters we defined earlier.
			robot.go_to_pose(drop).wait_for_completed()
			robot.drive_straight(distance_mm(stordist),speed_mmps(100)).wait_for_completed()
			robot.set_lift_height(0.00).wait_for_completed()
			robot.drive_straight(distance_mm(-stordist),speed_mmps(100)).wait_for_completed()
			stordist -= storstep
			
			# Return to the previous position.
			robot.go_to_pose(prev).wait_for_completed()

# End of function definitions.

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(cube_return, use_viewer=True, use_3d_viewer=True)