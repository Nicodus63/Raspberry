#!/usr/bin/env python

'''
Created on : 29 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : Testing ADC module

'''

'''
Imports
'''
import pigpio
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from PCF8591.src.PCF8591 import PCF8591

if __name__ == "__main__":
  pi = pigpio.pi() # Connect to local Pi.  
  sensor = PCF8591(pi)
  sensor.write_ADC(1.5)
  print (sensor.read_ADC(0, PCF8591.FOUR_SINGLE_ENDED_IN, PCF8591.ADC_CH_2, PCF8591.ANALOG_OUTPUT_FLAG)) 
  sensor.i2c_close()
   