#!/usr/bin/env python

import Image, ImageDraw, ImageColor
import math
import Queue
from motionmodel import *
import random
from distancelut import *
from labutils import *
import os.path
from distancelut import *

class DiscreteMap():
    def __init__(self,world_file,d_step):
        self.d_step = d_step
        self.map_width = 1.0
        self.map_height = 1.0
        self.image_width = 1.0
        self.image_height = 1.0
        self.grid_width = 1
        self.grid_height = 1
        self.world_file = world_file
        
        self.occupied = []
        self.num_angles = 72

        self.world_dir, self.world_name = os.path.split(self.world_file)
        print 'Created discrete map: '
        print 'World Dir: ', self.world_dir
        print 'World name: ', self.world_name[0:-6]
        self.parse_worldfile()
        self.load_image()
        self.discretize()

        print 'Discretized Map with d_step ', self.d_step, 'x y product', self.grid_width, self.grid_height, self.grid_width*self.grid_height

    def map_angle_to_grid_angle(self,angle):
        return -angle

    def map_angle_to_discrete_angle(self, angle):
        w_angle = wrap_angle(angle)
        if w_angle < 0:
            w_angle += 2*math.pi
        a_step = 2*math.pi / self.num_angles
        d_angle = int(math.floor(w_angle / a_step))
        return d_angle

    def discrete_angle_to_map_angle(self, d_angle):
        a_step = 2*math.pi / self.num_angles
        return wrap_angle(d_angle * a_step)

    def distance_to_obstacle(self,(gx,gy),mangle):
        angle = self.map_angle_to_grid_angle(mangle)
        X = gx
        Y = gy
        ca = math.cos(angle)
        sa = math.sin(angle)
        stepX = int(math.copysign(1,ca))
        stepY = int(math.copysign(1,sa))
        
        tDeltaX = 100.0
        tMaxX = 100.0
        if abs(ca) > 0:
            tDeltaX = 1.0 / abs(ca)
            tMaxX = 1.0 / (2*abs(ca))

        tDeltaY = 100.0
        tMaxY = 100.0
        if abs(sa) > 0:
            tDeltaY = 1.0 / abs(sa)
            tMaxY = 1.0 / (2*abs(sa))

        endX = -1
        endY = -1

        on_grid = True

        while on_grid:
            if (X,Y) in self.occupied:
                endX = X
                endY = Y
                on_grid = False

            if X < 0 or X > self.grid_width or Y < 0 or Y > self.grid_height:
                on_grid = False

            if tMaxX < tMaxY:
                tMaxX += tDeltaX
                X = X + stepX
            else:
                tMaxY += tDeltaY
                Y = Y + stepY
   
        if endX >= 0:
            s = self.grid_to_map((gx,gy))
            e = self.grid_to_map((endX,endY))
            return math.hypot(e[0]-s[0],e[1]-s[1])
        
        return 100.0

    def draw_discrete_map(self,sname):
        draw = ImageDraw.Draw(self.im)
        self.discretize(draw)
        self.im.save(sname)
        del draw

    def load_image(self):
        self.im = Image.open(self.image_file)
        self.im2 = self.im.convert("L")
        self.image_width = self.im.size[0]
        self.image_height = self.im.size[1]

    def discretize(self, draw=None):
        pix = self.im2.load()
        
        x = 0
        gx = 0

        while x < self.image_width:
            if draw is not None:
                draw.line([x,0,x,self.image_height],fill='Orange')
            y = 0
            gy = 0
            while y < self.image_height:
                if draw is not None: 
                    draw.line([0,y,self.image_width,y],fill='Orange')

                obstacle = False
                for px in range(x,x+self.d_step):
                    for py in range(y,y+self.d_step):
                        if px < self.image_width and py < self.image_height:
                            if pix[px,py] == 0:
                                obstacle = True
                                break
                    
                    if obstacle:
                        break

                if obstacle:
                    self.occupied.append((gx,gy))
                    if draw is not None:
                        self.draw_grid_rectangle(gx,gy,draw,"Green")

                if gy > self.grid_height:
                    self.grid_height = gy
                y = y + self.d_step
                gy = gy + 1

            if gx > self.grid_width:
                self.grid_width = gx
            x = x + self.d_step
            gx = gx + 1    

    def draw_grid_rectangle(self,gx,gy,draw,color):
        (x,y) = self.grid_to_image((gx,gy))
        draw.rectangle([x+1,y+1,x+self.d_step-1,y+self.d_step-1],fill=color)

    def image_to_grid(self,(ix,iy)):
        gx = int(math.floor( (float(ix) / float(self.d_step))))
        gy = int(math.floor( (float(iy) / float(self.d_step))))
        return (gx,gy)

    #The pixel corresponding to each grid cell is the pixel in the upper left-hand
    #corner of the grid cell
    def grid_to_image(self,(gx,gy)):
        ix = int(math.floor((float(gx) * float(self.d_step))))
        iy = int(math.floor((float(gy) * float(self.d_step))))
        return (ix,iy)

    def image_to_map(self,(ix,iy)):
        mx = float(ix)*float(self.map_width)/float(self.image_width) - float(self.map_width)/2
        my = (1.0 - (float(iy)/float(self.image_height)))*float(self.map_height) - float(self.map_height)/2
        return (mx,my)

    def map_to_image(self,(mx,my)):
        ix = int(math.floor(float(self.image_width) * (float(mx) + (float(self.map_width) / 2.0)) / float(self.map_width)))
        iy = int(math.floor(float(self.image_height) * (1.0 - (float(my) + (float(self.map_height) / 2.0)) / float(self.map_height))))
        return (ix,iy)

    def map_to_grid(self,(mx,my)):
        i = self.map_to_image((mx,my))
        return self.image_to_grid(i)

    def grid_to_map(self, g):
        i = self.grid_to_image(g)
        return self.image_to_map(i)

    def parse_worldfile(self):
        inmap = False

        f = open(self.world_file)

        for line in f:
            if line.find('map') == 0:
                inmap = True
            if inmap and line.find('bitmap') != -1:
                ls = line.split('"')
                self.image_file = os.path.dirname(self.world_file) + '/' + ls[1]
            if inmap and line.find('size') != -1:
                ls = line.split('[')
                ms = ls[1].split()
                self.map_width = float(ms[0])
                self.map_height = float(ms[1])
            if line.find('define') != -1:
                inmap = False

    def euclidean_distance_grid(self, a,b):
        d = math.hypot(b[0]-a[0],b[1]-a[1])
        return d

    def display_distance_LUT(self, dlut, sname):
        display_im = self.im.copy()
        draw = ImageDraw.Draw(display_im)

        print 'Grid w x h =', self.grid_width, self.grid_height
        max_d = 0

        for gx in range(self.grid_width-1):
            for gy in range(self.grid_height-1):
                (x,y) = self.grid_to_map((gx,gy))
                if (gx,gy) in self.occupied:
                    continue
                min_d = 40.0
                for ga in range(self.num_angles-1):
                    #print 
                    d = dlut.distance(x,y,self.discrete_angle_to_map_angle(ga))
                    #d2 = self.distance_to_obstacle((gx,gy),self.discrete_angle_to_map_angle(ga))
                    #print 'Checking <', gx, gy, ga, '> d = ', d, 'd2=',d2
                    if d < min_d:
                        min_d = d
                #print (x,y), '->', min_d
                if min_d > max_d:
                    max_d = min_d
                rvalue = int(255 - (min_d*255/5.0))
                if rvalue < 0:
                    rvalue = 0
                self.draw_grid_rectangle(gx,gy,draw,ImageColor.getrgb('rgb(' + str(rvalue) + ',0,0)'))
        print 'MAX D= ', max_d
                   
        #Save the image
        display_im.save(sname)
        del draw
        del display_im                   
                    

    def display_particles(self, particles, robot, laser_data, sname):
        #Create the draw object to draw with
        display_im = self.im.copy()
        draw = ImageDraw.Draw(display_im)
    
        #Plot out the particle locations on the image (in red)
        for i in range(len(particles)):
            d = 8
            p = self.map_to_image((particles[i].x,particles[i].y))
            draw.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2),fill='Red')
            draw.line([p,(p[0] + math.cos(particles[i].theta) * d,p[1] - math.sin(particles[i].theta)*d)],fill='Red',width =1)
            
        #Plot out the robot's actual location on the image (in blue)
        d = 10
        r = self.map_to_image((robot[0],robot[1]))
        draw.ellipse((r[0]-5,r[1]-5,r[0]+5,r[1]+5),fill='Blue')
        cur_angle = laser_data.angle_min
        
        #Plot out the current laser scan on the image (in blue)
        for j in range(len(laser_data.ranges)):
            d2 = int(laser_data.ranges[j] * self.image_height / self.map_height)
            draw.line([(r[0],r[1]),(r[0]+math.cos(robot[2] + cur_angle)*d2, r[1]-math.sin(robot[2]+cur_angle)*d2)],fill='Blue',width=1)
            cur_angle = cur_angle + laser_data.angle_increment
        
        d = 10
        draw.line([(r[0],r[1]),(r[0]+math.cos(robot[2])*d, r[1]-math.sin(robot[2])*d)],fill='Black',width=3)

        #Save the image
        display_im.save(sname)
        del draw
        del display_im

#This is space that allows us to test various aspects of the code.  Run if we run this 
#File as a standalone python script
if __name__ == '__main__':

    dmap = DiscreteMap("world/house1.world",5) 
    lut = DistanceLUT(dmap)
    dmap.display_distance_LUT(lut, 'world/dlutVIZ1.png')

    dmap.draw_discrete_map("world/discretemap20.png")
