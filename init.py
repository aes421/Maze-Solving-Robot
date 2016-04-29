import sys
import os.path
import Image
import subprocess
import pickle
from ImageProcessing import main as imgmain
import random
from scripts.glue import matrix_to_world_coord

def draw_square(pixels, x, y, w, h, c):

	for i in range(w):    # for every pixel:
	    for j in range(h):
	        pixels[x+i,y+j] = c # set the colour accordingly

def generate_image(matrix, image_name):

	square_dimension = 60

	print("Generating image..")
	img = Image.new( 'RGB', (len(matrix[0])*square_dimension,len(matrix)*square_dimension), "white") # create a new black image
	pixels = img.load() # create the pixel map

	for row in range(len(matrix)):
		for col in range(len(matrix[row])):

			if matrix[row][col] == 0:
				draw_square(pixels, col*square_dimension, row*square_dimension, square_dimension, square_dimension, (50,50,50))

	img.save("launch/"+str(image_name))

def get_random_grid_cell(matrix):

	'''
	Returns a random empty grid cell
	'''

	available = []

	for row in range(len(matrix)):
		for col in range(len(matrix[row])):

			if matrix[row][col] == 1:
				available.append((col, row))

	return random.choice(available)




def write_world_file(matrix, sim_name):

	if(matrix is None):
		print("Unable to create world file, the matrix you passed in was NONE")
		return

	matrix_width = len(matrix[0])
	matrix_height = len(matrix)
	image_name = str(sim_name)+"_maze.png"

	first_half = open('bitsnpieces/worldfirsthalf.txt', 'r').read()
	second_half = open('bitsnpieces/worldsecondhalf.txt','r').read()

	f = open('launch/simulation.world', 'w')
	
	f.write(first_half)
	f.write("\nmap\n(\n  name \""+str(sim_name)+"\"\n  size ["+str(matrix_width*4)+" "+str(matrix_height*4)+" 0.5]\n  pose [0 0 0 0]\n  bitmap \""+image_name+"\"\n)\n\n")
	f.write(second_half)

	# Find the goal in the matrix to write to the world config
	goal = None
	for row in range(len(matrix)):
		for col in range(len(matrix[row])):
			if matrix[row][col] == 2:
				goal = (row, col)

	# If we actually found a goal
	if goal != None:

		pos = matrix_to_world_coord(matrix_width, matrix_height, goal[1], goal[0])

		block = 'block (pose ['+str(pos[0])+' '+str(pos[1])+' 5 0] color "yellow")\n'
		#print(block +" for : "+str(goal))
		f.write(block)

	rnd_cell = get_random_grid_cell(matrix)
	spawn_pos = matrix_to_world_coord(matrix_width, matrix_height, rnd_cell[0], rnd_cell[1])

	f.write('turtlebot( pose ['+str(spawn_pos[0])+' '+str(spawn_pos[1])+' 0 180] color "black")')
	#f.write('turtlebot( pose [0 -29 0 180] color "red")')

	f.close()

	# Create that image now..
	generate_image(matrix, image_name)


def write_matrix_to_pickle(matrix, name_of_simulation):
	path_file = open("scripts/maze.pkl",'wb')
	pickle.dump(matrix,path_file)
	path_file.close()



if __name__ == '__main__':

	if len(sys.argv) != 3:
		sys.exit("Expecting 2 arguments (Name of Simulation, Maze Image name), but instead recieved "+str(len(sys.argv))+": "+str(sys.argv))
	

	name_of_simulation = sys.argv[1]
	name_of_maze_file = sys.argv[2]

	print("Extracting Information From Maze Image")

	# Grab a matrix using ashley's code
	matrix = imgmain(name_of_maze_file)

	print("Image successfuly parsed!")

	# Build a world file from the matrix
	write_world_file(matrix, name_of_simulation)

	# Save our maze to a pickle for our ros to use.
	write_matrix_to_pickle(matrix, name_of_simulation)

	print("Starting Ross...")
	subprocess.call(["roslaunch MazeSolvingRobot simulation.launch"], shell=True)
	print("Ross Has Ended!")