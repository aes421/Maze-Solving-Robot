#!/usr/bin/env python
import rospy
from geometry_msgs.msg import *
from sensor_msgs.msg import *
from nav_msgs.msg import *
import math
import random

##########################
# BEGIN Global Variable Definitions
front_distance = -1.0
wall_distance = -1.0
# END Global Variable Definitions
##########################

##########################
# BEGIN ROS Topic Callback Function [DON'T MESS WITH THIS STUFF]
##########################
def laserCallback(laser_data):
#This function will set front_distance and wall_distance.  Both of these work in the same way.  If something is closer than the detection_distance for that sensor, the value will tell how close something is.  If nothing is closer than the detection distance, the value of -1 will be used.

    global front_distance
    global wall_distance

    front_detection_distance = 0.9
    wall_detection_distance = 0.9

    wf_min_right = 10.0
    wf_min_front = 10.0
    
    cur_angle = laser_data.angle_min 

    for i in range(len(laser_data.ranges)):
        if abs(cur_angle + math.pi/2) < (math.pi / 8):
            #Wall sensor ((-5/8)*math.pi <= cur_angle <= (-3/8)*math.pi)
            if laser_data.ranges[i] < wf_min_right:
                wf_min_right = laser_data.ranges[i]

        if abs(cur_angle) < (math.pi / 8):
            #Wall sensor ((-1/8)*math.pi <= cur_angle <= (1/8)*math.pi)
            if laser_data.ranges[i] < wf_min_front:
                wf_min_front = laser_data.ranges[i]

        cur_angle = cur_angle + laser_data.angle_increment

    #Set the sensor variables
    front_distance = -1
    wall_distance = -1
    if wf_min_front < front_detection_distance:
        front_distance = wf_min_front
    if wf_min_right < wall_detection_distance:
        wall_distance = wf_min_right

############################
##### END CALLBACK FUNCTION   
############################
        
if __name__ == '__main__':
    rospy.init_node('lab3', anonymous=True) #Initialize the ros node
    pub = rospy.Publisher('cmd_vel', Twist) #Create our publisher to send drive commands to the robot
    rospy.Subscriber("base_scan", LaserScan, laserCallback) #Subscribe to the laser scan topic

    rate = rospy.Rate(10) #10 Hz  
    
    #SENSOR VARIABLES
    global front_distance #How close is something in front of the robot (-1 = nothing is close)
    global wall_distance  #How close is something on the right side of the robot (-1 = nothing is close)
        
    #########################################
    # LAB 3 VARIABLE DECLARATION CODE : BEGIN
    #########################################

    # PART C CODE HERE:
    #  Define and initialize variables that  
    #  you need inside the main loop

    last_wall_distance_reading = -1
    state = 0

    #######################################
    # LAB 3 VARIABLE DECLARATION CODE : END
    #######################################
    
    while not rospy.is_shutdown():
        
        #Declare the twist command that we will publish this time step
        twist = Twist()
              
        ###############################
        # LAB 3 INNER LOOP CODE : BEGIN
        ###############################

        # PART C CODE HERE:
        # Make sure that twist gets set with your drive command

        # Initial state, lets look for a wall
        if state is 0:

            twist.linear.x = 1

            if front_distance != -1 and front_distance < .7:
                state = 1

            if wall_distance != -1 and wall_distance < .7:
                state = 2

        # Wall Avoid, front sensor has gone off to put us in this state
        elif state is 1:
            
            twist.angular.z = 1

            if front_distance == -1 or wall_distance > .7:
                state = 2

        # Wall Follow, wall sensor is returning true to put us in this state
        elif state is 2:

            twist.linear.x = .5

            # Used to make sure the robot doesn't stray from the wall
            twist.angular.z = (wall_distance - last_wall_distance_reading)*-35

            if front_distance != -1 and front_distance<.5:
                state = 1

            if wall_distance == -1 or wall_distance >= .8:
                state = 3
                #twist.linear.x = -1

        # We lost the wall we're following, try finding it brah
        elif state is 3:

            
            twist.angular.z = -1

            if wall_distance != -1:
                state = 2
            

        last_wall_distance_reading = wall_distance
        last_wall_distance_reading += (.3-last_wall_distance_reading)/10
        #print 'state: ',state

        #############################
        # LAB 3 INNER LOOP CODE : END
        #############################
    
        #Publish drive command
        pub.publish(twist)
        rate.sleep() #Sleep until the next time to publish

    twist = Twist()
    pub.publish(twist)

