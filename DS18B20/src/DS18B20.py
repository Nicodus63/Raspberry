#!/usr/bin/env python

'''
Created on : 26 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : 
@note       : Temperature sensor

'''

'''
Imports
'''
import os
import glob
import time

class DS18B20:
   ''' Constants '''
   BASE_DIR = '/sys/bus/w1/devices/'
   
   ''' Constructor'''
   def __init__(self):
     ''' Init 1 wire protocol'''
     os.system('modprobe w1-gpio')
     os.system('modprobe w1-therm')
     ''' Path of files where value is stored '''
     device_folder = glob.glob(self.BASE_DIR + '28*')[0]
     device_file = device_folder + '/w1_slave'

   ''' Read the file ina raw '''
   def _read_temp_raw(self):
     f = open(self.device_file, 'r')
     lines = f.readlines()
     f.close()
     return lines

   ''' Decode temperature '''
   def read_temp(self):
     lines = self._read_temp_raw()
     while lines[0].strip()[-3:] != 'YES':
       time.sleep(0.2)
       lines = self._read_temp_raw()
     equals_pos = lines[1].find('t=')
     if equals_pos != -1:
       temp_string = lines[1][equals_pos+2:]
       temp_c = float(temp_string) / 1000.0
       return temp_c
                 