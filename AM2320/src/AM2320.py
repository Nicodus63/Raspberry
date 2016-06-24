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
   AM2320_ADDR        = 0xB8
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
     pi.i2c_open(self.I2C_BUS, self.AM2320_ADDR)
    
   ''' Command to wake up the sensor ''' 
   def _wake_sensor(self):
     self.pi.i2c_write_quick(self.I2C_BUS, self.AM2320_ADDR)
     time.sleep(.0008)
   
   ''' Send a read command to sensor need to indicate the first register
       and the number of registers we want to read '''  
   def _send_read_command(self, start_reg, length):
     self.pi.i2c_write_device(self.I2C_BUS, [self.AM2320_RD_CMD, start_reg, length])
     time.sleep(.0015)
   
   ''' Retrive data following the read_command '''  
   def _get_sensor_data(self, length):
     return self.pi.i2c_read_device(self.I2C_BUS, length)
   
   def _read_temperature_and_humidity(self):
     self._wake_sensor(self)
     self._send_read_command(self, self.HUMIDITY_HI_REG, 4) # Length = 4 : Temperature (2 Bytes) + Humidity (2 Bytes)
     # Return function code + Data_Length + Humidity (2 Bytes) + Temperature (2 Bytes) + CRC
     function_code, length, humidity_hi, humidity_lo, temp_hi, temp_lo, crc_hi, crc_lo = self._get_sensor_data(self, 8)
     temperature = (temp_hi<<8 + temp_lo) / 10
     humidity = (humidity_hi<<8 + humidity_lo) / 10
     print(function_code, length, humidity_hi, humidity_lo, temp_hi, temp_lo, crc_hi, crc_lo)
     print(temperature)
     print(humidity)
     
if __name__ == "__main__":
 
   pi = pigpio.pi() # Connect to local Pi.

   sensor = AM2320(pi)
   sensor._read_temperature_and_humidity()
        