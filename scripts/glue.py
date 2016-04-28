from pathingImplementation import *
import pickle

wall_representation = 0
path_representation = 1
goal_representaiton = 2


def get_map_matrix():

	# This will eventually be replaced with image processing code of maze
	sample_matrix = [
		[0,0,0,1,0,1,1,0],
		[1,1,1,1,0,0,1,0],
		[0,1,0,0,0,0,1,0],
		[0,1,0,2,1,1,1,0],
		[0,1,1,1,1,0,1,0],
		[0,0,1,0,0,0,1,1],
		[0,0,1,1,0,0,0,0],
		[0,0,1,0,0,0,0,0]
	]

	return sample_matrix


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

				return (w+1,h+1)



def get_cell_based_on_posiiton(x, y):

	'''
	Determine what cell of the matrix your currentely in depending on
	your current position
	'''

	map_dimension = [16, 16]

	cell = (int((map_dimension[0]/2 +x)/2), int((map_dimension[1]/2 -y)/2))

	print "Where we think we are: " + str(cell)+", from: ("+str(x)+", "+str(y)+")"

	return cell


def get_next_cell_based_on_position(matrix, x, y):

	'''
	Determines which cell in our maze we should head towards next
	using a*, based on our current position
	'''

	cur_pos = get_cell_based_on_posiiton(x, y)

	came_from, cost_sofar = a_star_search(matrix_to_graph(matrix), get_goal_in_matrix(matrix), cur_pos)

	

	return came_from[cur_pos]


def get_attractive_force_based_on_position(matrix, x, y):

	cell_to_move_towards = get_next_cell_based_on_position(matrix, x, y)

	if cell_to_move_towards is None:
		return [x,y]

	map_dimension = [16, 16]

	return ((cell_to_move_towards[0]*2)-(map_dimension[0]/2), (cell_to_move_towards[1]*2)-(map_dimension[1]/2))


def matrix_to_graph(matrix):

	# TODO: Create a check making sure the matrix is rectangular

	# Create a graph of appropriate width and height
	graph = GridWithWeights(len(matrix[0]), len(matrix))
	graph.walls = get_wall_cords_of_matrix(matrix)
	return graph


#get_next_cell_based_on_position(get_map_matrix(), 4, 0)