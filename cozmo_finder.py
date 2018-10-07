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
	print("You need: Cozmo, Matplotlib, Pillow, OpenCV")
	input()
	sys.exit()

locs = dict()
plstat = False

def handle_object_appeared(evt, **kw):
	global locs, plstat
	plt.clf()
	locs.update({evt.obj.object_id: [evt.obj.pose.position.x, evt.obj.pose.position.y]})
	plot_points = list()
	pts_x, pts_y = list(), list()
	for key in locs:
		pts_x.append(locs[key][0])
		pts_y.append(locs[key] [1])
	plt.scatter(pts_x, pts_y, label='Cozmo 2D Graph')
	plt.xlabel('xpos')
	plt.ylabel('ypos')
	plt.draw()
	plt.pause(0.001)
	# print(locs) # debug

def fip(robot, af):

	ok = False
	for i in range(10):
		
		try:
			FoundCube = robot.world.wait_for_observed_light_cube(timeout=0.5)
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

	robot.add_event_handler(cozmo.objects.EvtObjectAppeared, handle_object_appeared)
	# dropoff = robot.world.define_custom_cube(CustomObjectTypes.CustomType00, CustomObjectMarkers.Hexagons2, 44, 30, 30, True)
	# robot.camera.color_image_enabled = True

	stordist = 200
	storstep = 50
	num_cubes = 3

	if robot.is_on_charger == False:
		robot.say_text("Off charger.", voice_pitch=-1, duration_scalar=0.5).wait_for_completed()
		while robot.is_on_charger == False:
			time.sleep(1)

	charger = robot.world.charger
	
	robot.drive_off_charger_contacts().wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	cdpos = copy.deepcopy(robot.pose)
	print(type(locs))
	locs.update({"charger_dock": [robot.pose.position.x, robot.pose.position.y]})
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	drop = copy.deepcopy(robot.pose)
	locs.update({"drop": [robot.pose.position.x, robot.pose.position.y]})
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	robot.turn_in_place(degrees(-90)).wait_for_completed()
	robot.drive_straight(distance_mm(150), speed_mmps(100)).wait_for_completed()
	# cozmo.world.World.request_nav_memory_map(robot, 1)
	robot.set_lift_height(0.0).wait_for_completed()
	robot.set_head_angle(degrees(0.0)).wait_for_completed()
	
	af = list()
	
	for i in range(num_cubes):

		findcube, ok = fip(robot, af)
		af.append(findcube)
		
		if ok == True:
			#robot.go_to_pose(findcube).wait_for_completed()
			prev = copy.deepcopy(robot.pose)
			locs.update({"search_pos": [robot.pose.position.x, robot.pose.position.y]})
			x = robot.pickup_object(findcube, use_pre_dock_pose=False, in_parallel=False, num_retries=5).wait_for_completed()
			#robot.go_to_object(findcube, distance_mm(30.0)).wait_for_completed()
			#robot.drive_straight(distance_mm(10.0), speed_mmps(5)).wait_for_completed()
			#robot.set_lift_height(1.00).wait_for_completed()
			robot.go_to_pose(drop).wait_for_completed()
			robot.drive_straight(distance_mm(stordist),speed_mmps(100)).wait_for_completed()
			robot.set_lift_height(0.00).wait_for_completed()
			robot.drive_straight(distance_mm(-stordist),speed_mmps(100)).wait_for_completed()
			stordist -= storstep
			robot.go_to_pose(prev).wait_for_completed()
			
			#robot.go_to_object(charger, distance_mm(150.0)).wait_for_completed()
			#cozmo.robot.robot_alignment.RobotAlignmentTypes.Body = charger
			#robot.turn_in_place(degrees(90)).wait_for_completed()
			#robot.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()
			#robot.turn_in_place(degrees(-90)).wait_for_completed()

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(cube_return, use_viewer=True, use_3d_viewer=True)