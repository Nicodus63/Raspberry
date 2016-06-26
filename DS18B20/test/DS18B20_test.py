#!/usr/bin/env python

'''
Created on : 26 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : 
@note       : Test Temperature sensor

'''

'''
Imports
'''
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
 
from DS18B20.src.DS18B20 import DS18B20

if __name__ == "__main__":
 
   sensor = DS18B20()
   print(sensor.read_temp()) #Prints temperature in C