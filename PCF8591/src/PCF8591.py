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
   I2C_ADDRESS   = 0x48
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
   
   VREF    = 3.3
   QUANTUM = VREF / 256 # VREF = 3.3V - 8 bits converter
   
   def __init__(self, pi):
     ''' Open I2C '''
     self.pi = pi
     self.i2c_handler = pi.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)
     
   ''' Construct the control byte '''
   def _control_byte(self, channel, auto_increment, mode, analog_output):
     return ((analog_output << 6) + (mode << 4) + (auto_increment << 2) + channel)
    
   def read_ADC(self, read_all, mode, channel, output_en):
     if read_all :
       read_number = 5
       count, data = self.pi.i2c_read_i2c_block_data(self.i2c_handler, self._control_byte(self.ADC_CH_0, self.AUTO_INCR_FLAG, mode, output_en), read_number)
     else:
       read_number = 2
       count, data = self.pi.i2c_read_i2c_block_data(self.i2c_handler, self._control_byte(channel, 0, mode, output_en), read_number)
       
     voltage = []
     for i in range(0, read_number):
       voltage.append(data[i] * self.QUANTUM)
       
     ''' Remove first value according to specifications '''
     return voltage[1:]
     
   def write_ADC(self, tension):
     dac_number = tension // self.QUANTUM
     if dac_number > 255:
       dac_number = 255

     command = self._control_byte(0, 0, 0, self.ANALOG_OUTPUT_FLAG)
     self.pi.i2c_write_device(self.i2c_handler, [command, int(dac_number)])
    
   def i2c_close(self):
     self.pi.i2c_close(self.i2c_handler)
     
     
   
   
   