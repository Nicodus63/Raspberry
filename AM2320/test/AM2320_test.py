#!/usr/bin/env python

'''
Created on : 24 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio, AM2320
@note       : Testing AM2320 by printing temperature in humdity in a terminal

'''

'''
Imports
'''
import pigpio
import AM2320

if __name__ == "__main__":
 
   pi = pigpio.pi() # Connect to local Pi.

   sensor = AM2320(pi)
   print(sensor._read_temperature_and_humidity()) #Prints temperature in C and humidity in %
   sensor._close()