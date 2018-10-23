import numpy as np
import cv2, math, copy, heapq, time
from tkinter import *
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

def flip(mat, bits=8):
	"""
	mat = 2D list of values
	returns bit flipped 2D list of values
	"""
	xor = [[j ^ 2**bits-1 for j in i] for i in mat] 
	return xor

def selective_flip(mat):
	xor = [[1 if j == 0 else 0 for j in i] for i in mat]
	return xor

def searchdict(dic, value):
	"""
	dic = dictionary containing pairs
	value = key to find
	returns the key in which the value appears
	"""
	for i in dic.keys():
		if dic[i] == value:
			return i
	return None

def compress(mat, threshold=255):
	"""
	mat = 2D list of values
	threshold = all values equal to or above this value are set to 1
	returns compressed 2D list of values
	"""
	result = [[1 if j >= threshold else 0 for j in i] for i in mat]
	return result

def placeobs(mat, objs, ref):
	"""
	mat = 2D list of values
	objs = dictionary containing positions of objects
	ref = reference for the integer assigned to each object
	returns 2D list now with objects placed according to ref
	"""
	for i in objs:
		idval = searchdict(ident, i)
		pos = objs[i]
		mat[pos[0]][pos[1]] = idval
	return mat

def search(mat, start, end):
	"""
	mat = compressed 2D list
	start = starting position (x,y)
	end = ending position (x,y)
	returns grid with value 8 for the path value
	"""
	# print(mat)
	grid = Grid(matrix=mat)
	start = grid.node(start[1], start[0])
	end = grid.node(end[1], end[0])
	finder = AStarFinder()
	path, runs = finder.find_path(start, end, grid)
	for i in path:
		mat[i[1]][i[0]] = 8
	print(grid.grid_str(path=path, start=start, end=end))
	# print(mat)
	return mat

def addpadding(array, blocks):
	pass

def draw(canvas, width, height, il, img, fills, dx, dy):
	tx, ty, z, canvas_x, canvas_y = 0, 0, 0, 0, 0
	for i in img:
		for j in i:
			fill = fills[j]
			dot[canvas_y][canvas_x] = canvas.create_rectangle(tx, ty, tx + dx, ty + dy, fill=fill, width=0)
			tx += dx
			z = z + 1
			if z >= il: 
				canvas_x = 0
				z = 0
				tx = 0
				ty += dy
			else:
				canvas_x += 1
		canvas_y += 1

image = 'maze3.png'						# Maze image to process
img = cv2.imread(image, 0)				# - Read image and convert it to np.array
img = img.tolist()						# - Convert array to 2D list
dot = copy.deepcopy(img)				# - Create a copy of the list, so we can assign new values to each pixel for tk later
il = len(img)							# - Find out the size of the image, so we can use the full scr width for tk
size = 2000								# Size (in mm) of the maze area
spacing = 32							# Safe spacing (in mm) between wall and Cozmo
sep = round(spacing/size*64)			# - Blocks of separation (integer part) between wall and Cozmo
width, height = 320, 320				# Tkinter window size
dx, dy = width // il, height // il		# Square size (x,y)

# Place objects on map and their fills
objects = {'charger': [1,1], 'cube': [35,60]}
ident = {0: 'wall', 1: 'space', 2: 'charger', 3: 'cube', 8: 'path'}
fills = {0: 'black', 1: 'grey', 2: 'green', 3: 'red', 8: 'blue'}

# img = placeobs(compress(flip(img)), objects, ident)
# print(img)
print(compress(flip(img))[3])
img = search(compress(img), objects['charger'], objects['cube'])
print(img[3])
img = placeobs(img, objects, ident)
root = Tk()
root.resizable(width=False, height=False)
canvas = Canvas(root, width=width, height=height)
canvas.configure(bd=0, highlightthickness=0)
canvas.pack()
draw(canvas, width, height, il, img, fills, dx, dy)
root.mainloop()