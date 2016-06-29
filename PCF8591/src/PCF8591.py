#!/usr/bin/env python

'''
Created on : 29 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : ADC module

'''

'''
Imports
'''
import pigpio

class PCF8591:
   ''' Constants '''
   I2C_ADDRESS   = 0x77
   I2C_BUS       = 0x01
   
   ADC_CH_0      = 0x00
   ADC_CH_1      = 0x01
   ADC_CH_2      = 0x02
   ADC_CH_3      = 0x03
   
   AUTO_INCR_FLAG = 0x01
   
   FOUR_SINGLE_ENDED_IN      = 0x00 
   THREE_DIFF_IN             = 0x01 # CH0 = AIN0 - AIN3 ; CH1 = AIN1 - AIN3 ; CH2 = AIN2 - AIN3
   SINGLE_ENDED_AND_DIFF_MIX = 0x02 # CH2 = AIN2 - AIN3
   TWO_DIFF_IN               = 0x03 # CH0 = AIN0 - AIN1 ; CH1 = AIN2 - AIN3
   
   ANALOG_OUTPUT_FLAG = 0x01
   
   QUANTUM = 3.3 / 256 # VREF = 3.3V - 8 bits converter
   
   def __init__(self, pi):
     ''' Open I2C '''
     self.pi = pi
     self.i2c_handler = pi.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)
     
   ''' Construct the control byte '''
   def _control_byte(self, channel, auto_increment, mode, analog_output):
     return ((analog_output << 7) + (mode << 5) + (auto_increment << 3) + channel)
    
   def read_ADC(self, read_all, mode, channel):
     if read_all :
       data = self.pi.i2c_read_byte_data(self.i2c_handler, self._control_byte(self.ADC_CH_0, self.AUTO_INCR_FLAG, mode, 0))
     else:
       data = self.pi.i2c_read_byte_data(self.i2c_handler, self._control_byte(channel, 0, mode, 0))
       
     voltage = []     
     for i in data:
       voltage[i] = data[i] * self.QUANTUM
       
     return voltage
    
   def i2c_close(self):
     self.pi.i2c_close(self.i2c_handler)
     
     
   
   
   