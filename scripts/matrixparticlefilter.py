#!/usr/bin/env python
#Author: Chris Archibald, for AI-Robotics Class
#Last Modified: April 7, 2016
import rospy
from geometry_msgs.msg import *
from sensor_msgs.msg import *
from nav_msgs.msg import *
from tf.transformations import euler_from_quaternion
import math
import random
import copy
import math
from labutils import *
from sensormodel import *
from motionmodel import *
from glue import *
import Image, ImageDraw

#####################
# BEGIN Global Variable Definitions
robot = [0,0,0]       #Robot real position (only used for display purposes)
got_laser = False     #Don't start until we get the laser
laser_data = None     #The current laser scan (and info)
particles = []        #Our list of particles
command = None        #Current drive command to the robot
delta_t = 0.5         #Keep track of how long between predictions
delta_t_sum = 0.0     #How long between predictions as an average of previous iteration lengths
delta_t_num = 0       #How many previous iterations went into the average
matrix_map = None
map_walls = []
# END Global Variable Definitions
#####################

##########################
# BEGIN ROS Topic Callback Functions [DON'T MESS WITH THIS STUFF]
##########################

#This class keeps track of our info for a single particle
class Particle:
    def __init__(self,x,y,theta,w=0.0):
        self.x = x
        self.y = y
        self.theta = theta
        self.w = w

    def display(self):
        print ' (',self.x,',',self.y,',',self.theta,')'

#Laser callback function, store as global variable
def laserCallback(data):
    global laser_data
    global got_laser
    laser_data = data
    got_laser = True

#Command callback, store as global variable
def commandCallback(data):
    global command
    command = data

#Robot position callback, extract pose and save as global
def robotCallback(data):
    #This function updates the robots position and yaw, based on the ground truth (this is simply to display the true robot location on the images)
    global robot
    [r,p,yaw] = euler_from_quaternion([data.pose.pose.orientation.x,data.pose.pose.orientation.y,data.pose.pose.orientation.z,data.pose.pose.orientation.w])
    robot = [data.pose.pose.position.x,data.pose.pose.position.y,yaw]

#Update all the particles, done once per iteration
def update_particles(iteration):

    # 1. Advance physics
    advance_particles()

    # 2. Get weights from sensor model
    get_particle_weights()

    # 3. Resample according to weights
    resample_particles()


def get_particle_weights():
    global particles

    #Cycle through each particle and assign it a weight
    #The weight should be stored in particles[i].w
    for i in range(len(particles)):
        #See if particle is in an obstacle or off the map, if it is, it gets weight of 0.0
        if particle_on_map(particles[i]):
            #ASSIGN PARTICLE i its WEIGHT (save in particles[i].w)
            particles[i].w = get_scan_prob(particles[i])
        else:
            particles[i].w = 0.0

def get_scan_prob(p):
    global laser_data

    current_angle = laser_data.angle_min
    
    total_prob = 1.0

    for i in range(len(laser_data.ranges)):
        #IN THIS LOOP, PROCESS THE INDIVIDUAL LASER SCANS, USING THE SENSOR MODEL

        current_angle = current_angle + laser_data.angle_increment

        expected_distance_given_particle = expect_distance_from_part(p.x, p.y, wrap_angle(current_angle+p.theta))        

        recieved_laser_distance = laser_data.ranges[i]
        
        total_prob *= sensor_model(expected_distance_given_particle, recieved_laser_distance, laser_data.range_max)


    #total_prob /= len(laser_data.ranges)

    #RETURN THE ACTUAL SCAN PROBABILITY
    return total_prob

# http://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines-in-python
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (x, y)

def expect_distance_from_part(x, y, t):
    global map_walls
    global laser_data

    particle_line = ((x, y),(x + math.cos(t) * laser_data.range_max, y - math.sin(t)*laser_data.range_max))

    cur_intersection_points = []

    for wall in map_walls:

        intersection = line_intersection(wall, particle_line)

        if intersection is not None:
            cur_intersection_points.append(intersection)

    if len(cur_intersection_points) == 0:
        return laser_data.range_max

    clostest_distance = laser_data.range_max
    for point in cur_intersection_points:

        (x1, y1) = point
        (x2, y2) = (x, y)
        dist = math.hypot((x1 - x2) , (y1 - y2))

        if dist < clostest_distance:
            clostest_distance = dist

    return clostest_distance


def resample_particles():
    global particles

    new_particles = []
    
    #TODO
    #PART C: RESAMPLE PARTICLES
    #Using the weights of the particles, resample a new set of particles, 
    #(the same number as were in the previous set of particles)
    #Each time you choose one from the old set (particles), create a new one and add it to the 
    #new_particles list.  
    #Make sure that you also add in some number of random particles at each iteration (you can play with how many)
    #Look at the initialize particles code to see how to get a random particles easily

    min_num_of_particles = 500
    #num_of_new_particles = int(min_num_of_particles/10)
    #num_of_new_particles = 10



    num_of_rand_needed = int(min_num_of_particles*.055)


    tot_w = 0

    for p in range(len(particles)):

        tot_w += particles[p].w

    for p in range(len(particles)):

        particles[p].w += particles[p].w/tot_w

    #print(tot_w)

    big_particle_array = []

    for p in range(len(particles)):

        num_to_add = int(round(particles[p].w*10000))

        for a in range(num_to_add):
            big_particle_array.append(p)


    for p in range(min_num_of_particles-num_of_rand_needed):
        new_particles.append(copy.deepcopy(particles[random.choice(big_particle_array)]))

    
    for p in range(num_of_rand_needed):
        new_particles.append(get_random_particle())

    
    #Set our new set of particles to be our set of particles
    particles = new_particles

#Initialize the global list of particles with n random particles
def initialize_particles(n):
    global particles
    
    for i in range(n):
        particles.append(get_random_particle())
    
def particle_on_map(p):
    global maze_map

    w = len(maze_map[0])
    h = len(maze_map)

    for row  in range(len(maze_map)):
        for col in range(len(maze_map[row])):

            if maze_map[row][col] != 0:
                continue

            center_location = matrix_to_world_coord(w, h, col, row)
            bottom_left_bound = (center_location[0] -1.5, center_location[1] -1.5)
            top_right_bound = (center_location[0] +1.5, center_location[1] +1.5)

            if p.x >= bottom_left_bound[0] and p.x <= top_right_bound[0]:
                if p.y >= bottom_left_bound[1] and p.y <= top_right_bound[1]:
                    return False


    return True

#This will create and return a random valid particle (on the map, not on an obstacle)
def get_random_particle():
    global maze_map


    width = len(maze_map[0])*3
    height = len(maze_map)*3

    #Declare variables that we will need
    px = 0
    py = 0
    ptheta = 0
    epsilon = 0.25 #Distance from edge of map not to create particles in
    valid = False

    #Keep generating random particles until one is valid
    while not valid:

        #Randomly generate x, y, and theta for this particle
        px = random.uniform(-width/2+epsilon,width/2-epsilon)
        py = random.uniform(-height/2+epsilon,height/2-epsilon)
        ptheta = random.uniform(0,2*math.pi)
        p = Particle(px,py,ptheta,0.0)

        #Check this particle in a valid location?
        if particle_on_map(p):
            valid = True
    
    #Found a valid particle, return it
    p = Particle(px,py,ptheta,0.0)
    return p

#Advance particles forward in delta_t in time, using motion model
def advance_particles():
    global particles
    global delta_t
    global command

    if command == None:
        print("WE AINT GOT NO COMMAND")
        return 

    #Create Control Object for motion model to use
    u = Control(command.linear.x, command.angular.z)

    #Create motionmodel params objec
    vp = VelocityParams(0.05,0.05,0.05,0.05,0.05,0.05,delta_t)

    #Advance each particle
    for i in range(len(particles)):
        old_pose = Pose(particles[i].x, particles[i].y, particles[i].theta)
        
        #Use motion model to get new pose
        new_pose = sample_motion_model_velocity(u, old_pose, vp)
        
        #Assign this new pose to the particle
        particles[i].x = new_pose.x
        particles[i].y = new_pose.y
        particles[i].theta = new_pose.theta


def draw_square(pixels, x, y, w, h, c):

    for i in range(w):    # for every pixel:
        for j in range(h):
            pixels[x+i,y+j] = c # set the colour accordingly

def generate_particle_image(step):
    global maze_map
    global robot
    global particles

    square_dimension = 40

    cur_pos = get_cell_based_on_posiiton(maze_map, robot[0], robot[1])

    img = Image.new( 'RGB', (len(maze_map[0])*square_dimension,len(maze_map)*square_dimension), "white") # create a new black image
    pixels = img.load() # create the pixel map


    for row in range(len(maze_map)):
        for col in range(len(maze_map[row])):

            pos = (col, row)
            if pos == cur_pos:
                draw_square(pixels, col*square_dimension, row*square_dimension, square_dimension, square_dimension, (0,0,255))

            if maze_map[row][col] == 0:
                draw_square(pixels, col*square_dimension, row*square_dimension, square_dimension, square_dimension, (50,50,50))

    for p in particles:

        p_x = int( (((len(maze_map[0])*(3.0/2.0)) + p.x)/ (len(maze_map[0])*3)) * (len(maze_map[0]) * square_dimension) )
        p_y = int( (((len(maze_map)*(3.0/2.0)) - p.y)/ (len(maze_map)*3)) * (len(maze_map) * square_dimension) )
        #p_y = int(((len(maze_map)*(3.0/2.0)) - p.y)* square_dimension)

        draw_square(pixels, p_x, p_y, 2,2, (0,255,0))

    mypath = os.path.dirname(os.path.abspath(__file__))
    img.save(str(mypath)+"/particle"+str(step)+".png")
    print("Image Saved!!!")


#Main loop
if __name__ == '__main__':

    #Initialize the ros node
    rospy.init_node('lab4', anonymous=True) 

    #Subscribe to the topics we need
    rospy.Subscriber("base_pose_ground_truth", Odometry, robotCallback) #Subscribe to the robot pose topic
    rospy.Subscriber("base_scan", LaserScan, laserCallback) #Subscribe to laser scan
    rospy.Subscriber("cmd_vel",Twist,commandCallback) #Subscribe to the command issued

    #Declare needed global variables
    global delta_t
    global distance_LUT
    global discrete_map
    global robot
    global laser_data
    global maze_map
    global map_walls

    #Process arguments and world file name
    args = rospy.myargv(argv=sys.argv)
    maze_map = get_map_matrix()


    w = len(maze_map[0])
    h = len(maze_map)
    # Get all walls from maze
    for row  in range(len(maze_map)):
        for col in range(len(maze_map[row])):

            if maze_map[row][col] != 0:
                continue

            # Get the center of the square
            center_location = matrix_to_world_coord(w, h, col, row)

            # Get the points around the square
            bottom_left_bound = (center_location[0] -1.5, center_location[1] -1.5)
            top_right_bound = (center_location[0] +1.5, center_location[1] +1.5)
            bottom_right_bound = (center_location[0] +1.5, center_location[1] -1.5)
            top_left_bound = (center_location[0] -1.5, center_location[1] +1.5)

            #Get the walls around the square
            walls = []
            walls.append( (bottom_left_bound, top_left_bound) )
            walls.append( (bottom_right_bound, top_right_bound) )
            walls.append( (top_left_bound, top_right_bound) )
            walls.append( (bottom_left_bound, bottom_right_bound) )

            for wall in walls:
                if wall not in map_walls:
                    map_walls.append(wall)

    map_walls.append(((-w/2, -h/2),(+w/2, -h/2)))
    map_walls.append(((-w/2, -h/2),(-w/2, +h/2)))
    map_walls.append(((+w/2, +h/2),(+w/2, -h/2)))
    map_walls.append(((+w/2, +h/2),(-w/2, +h/2)))

    #Initialize timing sum
    delta_t_sum = 0.0

    #Initialize particles 
    #We will start with 500 particles, but you can experiment with different numbers of particles
    initialize_particles(500)

    #Set iteration counter
    iteration = 0

    #Save an image of particles how often (in iterations)
    #Change this to influence how many images get saved out
    display_rate = 1

    #Main filtering loop
    while not rospy.is_shutdown():
        #Only proceed if we have received a laser scan
        if got_laser: 

            #Keep track of time this iteration takes
            before = rospy.get_rostime()
            
            #See if we should save out an image of the particles
            if (iteration % display_rate) == 0:
                print("Generating Particle Image")
                generate_particle_image(iteration)


            #Update the particles
            update_particles(iteration)

            #Increment our iteration counter
            iteration += 1
            
            #Figure our how long iteration took, keep track of stats
            #This gives us our delta_t for prediction step
            after = rospy.get_rostime()
            duration = after - before
            cur_delta_t = duration.to_sec()
            delta_t_sum = delta_t_sum + cur_delta_t
            delta_t = delta_t_sum / float(iteration)
