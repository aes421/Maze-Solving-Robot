from pathingImplementation import *
import pickle
import os
from os import listdir
from os.path import isfile, join

wall_representation = 0
path_representation = 1
goal_representaiton = 2


def get_map_matrix():

	# This will eventually be replaced with image processing code of maze
	mypath = os.path.dirname(os.path.abspath(__file__))
	#onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath,f))]
	#print("EVERYTHING IN DIRECTORY: ("+str(mypath)+")"+ str(onlyfiles))

	path_file = open(str(mypath)+"/maze.pkl",'rb')
	maze_map = pickle.load(path_file)
	path_file.close()

	return maze_map


def get_wall_cords_of_matrix(matrix):

	wall_cords = []

	for h in range(len(matrix)):

		for w in range(len(matrix[h])):

			if matrix[h][w] is wall_representation:

				wall_cords.append((w,h))

	return wall_cords


def get_goal_in_matrix(matrix):

	for h in range(len(matrix)):

		for w in range(len(matrix[h])):

			if matrix[h][w] is goal_representaiton:

				return (w,h)



def get_cell_based_on_posiiton(matrix, x, y):

	'''
	Determine what cell of the matrix your currentely in depending on
	your current position
	'''

	'''
	ros_pos_x = col - int(width/2)
	ros_pos_y = int(height/2) - row

	if width %2 == 0:
		
		if ros_pos_x < 0 :
			ros_pos_x += 0.5
		

	if height % 2 == 0:

		ros_pos_y -= 0.5

	ros_pos_x *= 2
	ros_pos_y *= 2
	'''

	'''
	map_dimension = [len(matrix[0]), len(matrix)]

	cell_x = int((int(map_dimension[0]/2) +x)/2)
	cell_y = int((int(map_dimension[1]/2) -y)/2)

	cell = (cell_x, cell_y)

	print "Where we think we are: " + str(cell)+", from: ("+str(x)+", "+str(y)+")"
	'''

	width = len(matrix[0])
	height = len(matrix)


	cell_x = x/2.0
	cell_y = y/2.0

	if width % 2 == 0:
		if cell_x < 0:
			cell_x -= 0.5

	if height % 2 == 0:
		cell_y += 0.5

	cell_x = int(cell_x + (width/2.0))
	cell_y = int((height/2.0) - cell_y)

	cell = (cell_x, cell_y)

	print "Where we think we are: " + str(cell)+", from: ("+str(x)+", "+str(y)+")"


	return cell


def matrix_to_world_coord(width, height, col, row):

	ros_pos_x = col - int(width/2)
	ros_pos_y = int(height/2) - row

	if width %2 == 0:
		
		if ros_pos_x < 0 :
			ros_pos_x += 0.5
		

	if height % 2 == 0:

		ros_pos_y -= 0.5

	ros_pos_x *= 2
	ros_pos_y *= 2

	return (ros_pos_x, ros_pos_y)


def get_next_cell_based_on_position(matrix, x, y):

	'''
	Determines which cell in our maze we should head towards next
	using a*, based on our current position
	'''

	cur_pos = get_cell_based_on_posiiton(matrix, x, y)

	came_from, cost_sofar = a_star_search(matrix_to_graph(matrix), get_goal_in_matrix(matrix), cur_pos)

	if cur_pos in came_from.keys():

		print("Next Waypoint: "+str(came_from[cur_pos]))

		return came_from[cur_pos]

	print("Failure grabbing waypoint, defaulting: (0,0)")

	print str(came_from)

	return (0,0)


def get_attractive_force_based_on_position(matrix, x, y):

	cell_to_move_towards = get_next_cell_based_on_position(matrix, x, y)

	if cell_to_move_towards is None:
		return [x,y]

	map_dimension = [len(matrix[0]), len(matrix)]

	return matrix_to_world_coord(map_dimension[0], map_dimension[1], cell_to_move_towards[0], cell_to_move_towards[1])


def matrix_to_graph(matrix):

	# TODO: Create a check making sure the matrix is rectangular

	# Create a graph of appropriate width and height
	graph = GridWithWeights(len(matrix[0]), len(matrix))
	graph.walls = get_wall_cords_of_matrix(matrix)
	return graph


#get_next_cell_based_on_position(get_map_matrix(), 4, 0)