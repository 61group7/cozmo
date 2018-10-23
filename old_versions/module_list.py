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