#!/usr/bin/env python
import math

def wrap_angle(angle):
    r_angle = angle
    while r_angle <= -math.pi:
        r_angle += 2*math.pi
    while r_angle >= math.pi:
        r_angle -= 2*math.pi
    return r_angle

