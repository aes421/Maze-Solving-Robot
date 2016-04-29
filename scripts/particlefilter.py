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
from labutils import *
from sensormodel import *
from motionmodel import *
from discretemap import *
from distancelut import *

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
distance_LUT = None   #This is our look-up table for distances from obstacles
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

############################
##### END CALLBACK FUNCTIONS  
############################

##########################
# BEGIN PARTICLE FILTER CODE
##########################

#Initialize the global list of particles with n random particles
def initialize_particles(n):
    global particles
    
    #TODO
    #PART A: INITIALIZE n PARTICLES TO A RANDOM LOCATION ON THE BOARD
    # particles is a list of particles (initially empty) it should be appended to
    # get_random_particle() is a function (defined) below, that will return a
    # particle at a random location on the map

    for i in range(n):
        particles.append(get_random_particle())
    
    
#This will create and return a random valid particle (on the map, not on an obstacle)
def get_random_particle():
    global discrete_map

    #Declare variables that we will need
    px = 0
    py = 0
    ptheta = 0
    epsilon = 0.25 #Distance from edge of map not to create particles in
    valid = False

    #Keep generating random particles until one is valid
    while not valid:

        #Randomly generate x, y, and theta for this particle
        px = random.uniform(-discrete_map.map_width/2+epsilon,discrete_map.map_width/2-epsilon)
        py = random.uniform(-discrete_map.map_height/2+epsilon,discrete_map.map_height/2-epsilon)
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
                       
#Check to see if a particle is on the map
def particle_on_map(p):
    global discrete_map
    epsilon = 0.05

    if p.x < -discrete_map.map_width/2.0 + epsilon or p.x > discrete_map.map_width/2.0 - epsilon:
        return False
    if p.y < -discrete_map.map_height/2.0 + epsilon or p.y > discrete_map.map_height/2.0 - epsilon:
        return False

    (gx,gy) = discrete_map.map_to_grid((p.x,p.y))
    if (gx,gy) in discrete_map.occupied:
        return False
    
    return True

#Assign each particle its weight
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

#Get the probability of the current laser scan, for particle p
def get_scan_prob(p):
    global laser_data
    global distance_LUT

    #TODO
    #PART B: GET AND RETURN THE PROBABILITY OF THE CURRENT LASER SCAN
    # stored in (laser_data) for the input particle p
    
    #To get the expected distance, call distance_LUT.distance(x,y,angle), where x,y is the location to start from, and angle is the map angle direction to travel.  
    #This will return the distance from the look-up-table (LUT) that we expect an obstacle to be.
    #To use the sensor model, simply call sensor_model(expected_distance, measured_distance, maximum_range) 
    #where expected distance is the distance to the expected obstacle, measured_distance is the distance that the laser measured
    # (stored in laser_data.ranges[]), and maximum_range is the maximum range reading of the laser scanner (stored in laser_data.range_max)
    
    #This variable will have the angle from the robot that the current scan is pointing
    #To get global angle to pass to LUT from this, do wrap_angle(current_angle + p.theta), where p.theta is the heading of the current particle
    current_angle = laser_data.angle_min
    
    total_prob = 1.0

    for i in range(len(laser_data.ranges)):
        #IN THIS LOOP, PROCESS THE INDIVIDUAL LASER SCANS, USING THE SENSOR MODEL

        current_angle = current_angle + laser_data.angle_increment

        expected_distance_given_particle = distance_LUT.distance(p.x, p.y, wrap_angle(current_angle+p.theta))        

        recieved_laser_distance = laser_data.ranges[i]
        
        total_prob *= sensor_model(expected_distance_given_particle, recieved_laser_distance, laser_data.range_max)


    #total_prob /= len(laser_data.ranges)

    #RETURN THE ACTUAL SCAN PROBABILITY
    return total_prob

#Get the next set of particles
#By resampling current ones according to weights, with replacement
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

    min_num_of_particles = 1500
    #num_of_new_particles = int(min_num_of_particles/10)
    #num_of_new_particles = 10


    num_of_rand_needed = 0

    if len(particles) == min_num_of_particles:

        '''
        cent_x = 0
        cent_y = 0

        #Get center of particles
        for p in range(len(particles)):

            cent_x += particles[p].x
            cent_y += particles[p].y

        cent_x /= len(particles)
        cent_y /= len(particles)


        avg_dist = 0

        #Get avg distance From Center
        for p in range(len(particles)):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   0cles)):
            avg_dist += math.hypot(particles[p].x- cent_x, particles[p].y - cent_y)

        avg_dist /= len(particles)

        #determine the number needed of new particles
        num_of_rand_needed = int(max(min(len(particles)/10, avg_dist*4), 1))
        '''

        '''
        avg_w = 0

        for p in range(len(particles)):

            avg_w += particles[p].w

        avg_w /= len(particles)

        #num_of_rand_needed = int((1 - avg_w) *50)
        '''
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

#Update all the particles, done once per iteration
def update_particles(iteration):

    # 1. Advance physics
    advance_particles()

    # 2. Get weights from sensor model
    get_particle_weights()

    # 3. Resample according to weights
    resample_particles()

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

    #Process arguments and world file name
    args = rospy.myargv(argv=sys.argv)
    discrete_map = DiscreteMap(args[1], 5)
    distance_LUT = DistanceLUT(discrete_map)

    #Initialize timing sum
    delta_t_sum = 0.0

    #Initialize particles 
    #We will start with 500 particles, but you can experiment with different numbers of particles
    initialize_particles(7000)

    #Set iteration counter
    iteration = 0

    #Save an image of particles how often (in iterations)
    #Change this to influence how many images get saved out
    display_rate = 50

    #Main filtering loop
    while not rospy.is_shutdown():
        #Only proceed if we have received a laser scan
        if got_laser: 

            #Keep track of time this iteration takes
            before = rospy.get_rostime()
            
            #See if we should save out an image of the particles
            if (iteration % display_rate) == 0:
                sname = discrete_map.world_dir + '/' + 'pf_' + discrete_map.world_name + '_' + str(iteration).zfill(4) + '.png'
                discrete_map.display_particles(particles, robot, laser_data, sname)

            #Update the particles
            update_particles(iteration)

            #Increment our iteration counter
            iteration = iteration + 1
            
            #Figure our how long iteration took, keep track of stats
            #This gives us our delta_t for prediction step
            after = rospy.get_rostime()
            duration = after - before
            cur_delta_t = duration.to_sec()
            delta_t_sum = delta_t_sum + cur_delta_t
            delta_t = delta_t_sum / float(iteration)

