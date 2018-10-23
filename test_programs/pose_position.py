import asyncio, functools, math, sys, cozmo, cv2, time, os, random
import numpy as np
import copy
from multiprocessing import Process
from matplotlib import pyplot as plt
from cozmo.util import degrees, distance_mm, radians, speed_mmps, Vector2
from cozmo.lights import Color, Light
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes
from PIL import Image, ImageColor, ImageDraw, ImageStat

def main(robot):
	print(robot.pose.position.x, robot.pose.position.y)
	robot.drive_straight(random.randint(10,30))
	robot.turn_in_place(degrees=random.randint(10,25))

cozmo.robot.Robot.drive_off_charger_on_connect = False
cozmo.run_program(main, use_viewer=True)
