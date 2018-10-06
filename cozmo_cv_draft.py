"""

Computer Vision Test Program for Cozmo
	
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

"""
References:
	OpenCV: <https://docs.opencv.org/3.1.0/dd/d53/tutorial_py_depthmap.html>
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

def crim():
	pass

def map3d(robot):
	
	robot.camera.image_stream_enabled = True
	

	temp_folder = "\\cvim" 				# Change temp folder
	cpath = os.getcwd() + temp_folder	# Get Working Directory
	print(cpath)						# Debug
	if not os.path.exists(cpath):		# Create directory if it doesn't exist.	
		os.makedirs(cpath)

	cdtm = 150	# Charger distance to maze
	ilo = 0		# Img 1 angle (deg)
	ihi = 10	# Img 2 angle (deg)
	imq = 100	# Pillow Image Quality

	# Drive out into the maze area

	robot.drive_off_charger_contacts().wait_for_completed()
	robot.drive_straight(distance_mm(cdtm), speed_mmps(100)).wait_for_completed()
	robot.set_head_angle(degrees(0)).wait_for_completed()
	
	# Create stereo images by moving Cozmo's head up and down
	# Image order: Low A, High A, High B, Low B
	
	for i in range(6):
		
		time.sleep(0.25)
		imageA = robot.world.latest_image.raw_image
		imageA.save((cpath + "\\outA.png"), quality=imq)

		robot.set_head_angle(degrees(ihi)).wait_for_completed()

		time.sleep(0.25)
		imageB = robot.world.latest_image.raw_image
		imageB.save((cpath + "\\outB.png"), quality=imq)

		robot.turn_in_place(degrees(30)).wait_for_completed()

		cviA = cv2.imread((cpath + '\\outA.png'),0)
		cviB = cv2.imread((cpath + '\\outB.png'),0)
		disparity = cv2.StereoBM_create(numDisparities=16, blockSize=15).compute(cviA,cviB)
		pyplot.imshow(disparity,'gray')
		pyplot.show()
		time.sleep(60)

		time.sleep(0.25)
		imageD = robot.world.latest_image.raw_image
		imageD.save((cpath + "\\outD.png"), quality=imq)

		robot.set_head_angle(degrees(ilo)).wait_for_completed()

		time.sleep(0.25)
		imageC = robot.world.latest_image.raw_image
		imageC.save((cpath + "\\outC.png"), quality=imq)


# Run Function
cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(map3d)