import math
import random   
   
class Pose():
    def __init__(self,x,y,theta):
        self.x = x
        self.y = y
        self.theta = theta
   
class Control():
    def __init__(self, v,w):
        self.v = v
        self.w = w
   
class VelocityParams():
    def __init__(self,a1,a2,a3,a4,a5,a6,delta_t):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5
        self.a6 = a6
        self.delta_t = delta_t
    
def sample_normal_distribution(b):
    r = 0
    for i in range(12):
        r += random.uniform(-b,b)
    return r/2.0
    
def sample_triangular_distribution(b):
    return (math.sqrt(6)/2)*(random.uniform(-b,b) + random.uniform(-b,b))
    
def sample_d(b):
    return sample_triangular_distribution(b)
    
def sample_motion_model_velocity(u,p,params):
   
    v = u.v + sample_d(params.a1*math.fabs(u.v) + params.a2*math.fabs(u.w))
    w = u.w + sample_d(params.a3*math.fabs(u.v) + params.a4*math.fabs(u.w))
    g = sample_d(params.a5*math.fabs(u.v) + params.a6*math.fabs(u.w))

    x = p.x + v*math.sin(p.theta)
    y = p.y + v*math.cos(p.theta)
    theta = p.theta

    if abs(w) > 0:        
        x = p.x - (v/w)*math.sin(p.theta) + (v/w)*math.sin(p.theta + w*params.delta_t)
        y = p.y + (v/w)*math.cos(p.theta) - (v/w)*math.cos(p.theta + w*params.delta_t)
        theta = p.theta + w*params.delta_t + g*params.delta_t
    
    #print 'New Pose: x=', x, ' y=', y, ' theta=', theta
    return Pose(x,y,theta)    
    
    
    
    
