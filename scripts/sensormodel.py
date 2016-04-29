#!/usr/bin/env python
import math

#Return the value of the normal pdf with mean and sd at value x
def normpdf(x,mean,sd):
    var = float(sd)**2
    denom = (2*math.pi*var)**0.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom

#Return the value of the normal cdf with mean and sd at value x
def normcdf(x,mean,sd):
    z = (float(x)-float(mean))/float(sd)
    if z >= 0.0:
        return 0.5 + 0.5 * math.erf(z / math.sqrt(2.0))
    else:
        return 0.5 * math.erfc(-z / math.sqrt(2.0))

#Return the probability of sensor_reading, given true_distance to obstacle
def sensor_model(true_distance, sensor_reading, range_max):
    std = 2.5
    alpha = 1.0 / (1.0 - normcdf(0.0, true_distance, std))
    beta = 1.0 - normcdf(range_max, true_distance, std)
    if sensor_reading >= range_max:
        return beta
    return alpha * normpdf(sensor_reading,true_distance,std)


