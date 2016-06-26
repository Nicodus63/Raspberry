#!/usr/bin/env python

'''
Created on : 23 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : Temperature and humidity sensor

'''

'''
Imports
'''
import pigpio
import time

class AM2320:
   ''' Constants '''
   I2C_BUS            = 0x01
   AM2320_ADDR        = 0x5C
   AM2320_RD_CMD      = 0x03
   AM2320_WR_CMD      = 0x10
   HUMIDITY_HI_REG    = 0x00
   HUMIDITY_LO_REG    = 0x01
   TEMPERATURE_HI_REG = 0x02
   TEMPERATURE_LO_REG = 0x03
   MODEL_HI_REG       = 0x08
   MODEL_LO_REG       = 0x09
   VERSION_NB_REG     = 0x0A
   DEVICE_ID_0_REG    = 0x0B
   DEVICE_ID_1_REG    = 0x0C
   DEVICE_ID_2_REG    = 0x0D
   DEVICE_ID_3_REG    = 0x0E
   STATUS_REG         = 0X0F
   
   ''' Constructor'''
   def __init__(self, pi):
     self.pi = pi
     self.bus_handler = pi.i2c_open(self.I2C_BUS, self.AM2320_ADDR)
    
   ''' Command to wake up the sensor ''' 
   def _wake_sensor(self):
     self.pi.i2c_write_quick(self.bus_handler, 1)
     time.sleep(.0008)
   
   ''' Send a read command to sensor need to indicate the first register
       and the number of registers we want to read '''  
   def _send_read_command(self, start_reg, length):
     self.pi.i2c_write_device(self.bus_handler, [self.AM2320_RD_CMD, start_reg, length])
     time.sleep(.0015)
   
   ''' Retrive data following the read_command '''  
   def _get_sensor_data(self, length):
     return self.pi.i2c_read_device(self.bus_handler, length)
   
   def read_temperature_and_humidity(self):
     self._wake_sensor()
     self._send_read_command(self.HUMIDITY_HI_REG, 4) # Length = 4 : Temperature (2 Bytes) + Humidity (2 Bytes)
     # Return function code + Data_Length + Humidity (2 Bytes) + Temperature (2 Bytes) + CRC
     length, data = self._get_sensor_data(8)
     #Parse data
     function_code = data[0]
     length        = data[1]
     humidity_hi   = data[2]
     humidity_lo   = data[3]
     temp_hi       = data[4]
     temp_lo       = data[5]
     crc_lo        = data[6] # CRC low first
     crc_hi        = data[7]
     #Check crc -- Remove crc from length (2 Bytes)
     crc = ((crc_hi << 8) + crc_lo)
     if (self._check_crc(data[:-2]) == crc):
       self._check_crc(data[:-2])
       temperature = ((temp_hi << 8) + temp_lo) / 10.0 # in C
       humidity    = ((humidity_hi << 8) + humidity_lo) / 10.0 # in %
     else:
       temperature = -1
       humidity    = -1

     return temperature, humidity
     
   def _check_crc(self, buf):
     crc = 0xFFFF
     for c in buf:
       crc ^= c
       for i in range(0,8):
         if crc & 0x01:
           crc >>= 1
           crc ^= 0xA001
         else:
           crc >>= 1
     return crc
     
   def close(self):
     self.pi.i2c_close(self.bus_handler)
                 