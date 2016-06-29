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
from PCF8591.src.PCF8591 import PCF8591

   pi = pigpio.pi() # Connect to local Pi. 
 
   sensor = PCF8591(pi)
   
   print (sensor.read_ADC(0, PCF8591.FOUR_SINGLE_ENDED_IN, PCF8591.ADC_CH_3))
   