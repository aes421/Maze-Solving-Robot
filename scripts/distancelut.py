#!/usr/bin/env python
import discretemap
import os.path

class DistanceLUT():
    def __init__(self, discrete_map):
        self.discrete_map = discrete_map
        self.LUT = None
        self.lutfile = self.discrete_map.image_file[0:-4] + '_' + str(self.discrete_map.d_step) + '.dlut'
        self.load_LUT()

    #Determine the distance to an obstacle from map coordinates x,y in direction theta
    #Done from Look-up table (fast)
    def distance(self,x,y,angle):
        (gx,gy) = self.discrete_map.map_to_grid((x,y))
        ai = self.discrete_map.map_angle_to_discrete_angle(angle)
        #print 'In checking', gx,gy,ai
        return self.LUT[gx][gy][ai]

    #Load the look-up table, if there is one, if not, create it (takes a while (around 45 minutes on my machine)
    def load_LUT(self):
        if os.path.isfile(self.lutfile):
            #Load it
            print 'Loading Distance Look-Up Table . . .',
            dlut = open(self.lutfile,'r')
            self.LUT = eval(dlut.read())
            dlut.close()
            print 'Done'
        else:
            print 'Creating Distance Look-Up Table . . .'
            #Create it
            self.LUT = [[[0.0 for a in range(self.discrete_map.num_angles)] for y in range(self.discrete_map.grid_height+1)] for x in range(self.discrete_map.grid_width+1)]

            for gx in range(self.discrete_map.grid_width+1):
                print 'X = ', gx, ' of ', self.discrete_map.grid_width+1
                for gy in range(self.discrete_map.grid_height+1):
                    for ga in range(self.discrete_map.num_angles):
                        d = self.discrete_map.distance_to_obstacle((gx,gy),self.discrete_map.discrete_angle_to_map_angle(ga))
                        self.LUT[gx][gy][ga] = d
                        
            print 'Done creating distance LUT'
            print 'Saving to file'
            dlut = open(self.lutfile,'w')
            dlut.write(str(self.LUT))
            dlut.close()
            print 'Done.'

    
