#!/usr/bin/env python

'''
Created on : 26 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : 
@note       : Test Temperature and Pressure sensor

'''

'''
Imports
'''
import pigpio
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
 
from BMP085.src.BMP085 import BMP085

if __name__ == "__main__":
 
   pi = pigpio.pi() # Connect to local Pi.

   sensor = BMP085(pi, 1) # Standard resolution
   print(sensor.read_temperature()) #Temperature in C
   print(sensor.read_pressure()) #Presure in Pa
   print(sensor.read_sealevel_pressure(80.0))
   sensor.close()