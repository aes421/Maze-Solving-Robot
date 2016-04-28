import sys
import Image
import subprocess
from ImageProcessing.py import main as imgmain

def draw_square(pixels, x, y, w, h):

	for i in range(w):    # for every pixel:
	    for j in range(h):
	        pixels[x+i,y+j] = (50, 50, 50) # set the colour accordingly

def generate_image(matrix, image_name):

	square_dimension = 60

	print("Generating image..")
	img = Image.new( 'RGB', (len(matrix[0])*square_dimension,len(matrix)*square_dimension), "white") # create a new black image
	pixels = img.load() # create the pixel map

	for row in range(len(matrix)):
		for col in range(len(matrix[row])):

			if matrix[row][col] == 0:
				draw_square(pixels, col*square_dimension, row*square_dimension, square_dimension, square_dimension)

	img.save("launch/"+str(image_name))


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
	f.write("\nmap\n(\n  name \""+str(sim_name)+"\"\n  size ["+str(matrix_width*2)+" "+str(matrix_height*2)+" 0.5]\n  pose [0 0 0 0]\n  bitmap \""+image_name+"\"\n)\n\n")
	f.write(second_half)

	f.close()

	# Create that image now..
	generate_image(matrix, image_name)


if __name__ == '__main__':

	if len(sys.argv) != 3:
		sys.exit("Expecting 2 arguments (Name of Simulation, Maze Image name), but instead recieved "+str(len(sys.argv))+": "+str(sys.argv))
		

	name_of_simulation = sys.argv[1]
	name_of_maze_file = sys.argv[2]

	print("Extracting Information From Maze Image")

	# Grab a matrix using ashley's code
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

	sample_matrix = imgmain(name_of_maze_file)

	print("Image successfuly parsed!")

	# Build a world file from the matrix
	write_world_file(sample_matrix, name_of_simulation)

	print("Starting Ross...")
	subprocess.call(["roslaunch MazeSolvingRobot sample.launch"], shell=True)
	print("Ross Started!")