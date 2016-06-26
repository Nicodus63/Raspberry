#!/usr/bin/env python

'''
Created on : 26 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : Temperature and pressure sensor

'''

'''
Imports
'''
import pigpio
import time

class BMP085():
   ''' Constants '''
   # BMP085 default address.
   BMP085_I2CADDR           = 0x77
   I2C_BUS                  = 0x01

   # Operating Modes
   BMP085_ULTRALOWPOWER     = 0
   BMP085_STANDARD          = 1
   BMP085_HIGHRES           = 2
   BMP085_ULTRAHIGHRES      = 3

   # BMP085 Registers
   BMP085_CAL_AC1           = 0xAA  # R   Calibration data (16 bits)
   BMP085_CAL_AC2           = 0xAC  # R   Calibration data (16 bits)
   BMP085_CAL_AC3           = 0xAE  # R   Calibration data (16 bits)
   BMP085_CAL_AC4           = 0xB0  # R   Calibration data (16 bits)
   BMP085_CAL_AC5           = 0xB2  # R   Calibration data (16 bits)
   BMP085_CAL_AC6           = 0xB4  # R   Calibration data (16 bits)
   BMP085_CAL_B1            = 0xB6  # R   Calibration data (16 bits)
   BMP085_CAL_B2            = 0xB8  # R   Calibration data (16 bits)
   BMP085_CAL_MB            = 0xBA  # R   Calibration data (16 bits)
   BMP085_CAL_MC            = 0xBC  # R   Calibration data (16 bits)
   BMP085_CAL_MD            = 0xBE  # R   Calibration data (16 bits)
   BMP085_CONTROL           = 0xF4
   BMP085_TEMPDATA          = 0xF6
   BMP085_PRESSUREDATA      = 0xF6

   # Commands
   BMP085_READTEMPCMD       = 0x2E
   BMP085_READPRESSURECMD   = 0x34
   
   def __init__(self, pi, mode):
     self.pi = pi
     self.bus_handler = pi.i2c_open(self.I2C_BUS, self.BMP085_I2CADDR)
     self.mode = mode # Low power, standard, high resolution, ultra high resolution

   def _load_calibration(self):
     self.cal_AC1 = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_AC1, 2)
     self.cal_AC2 = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_AC2, 2)
     self.cal_AC3 = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_AC3, 2)   
     self.cal_AC4 = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_AC4, 2)   
     self.cal_AC5 = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_AC5, 2)   
     self.cal_AC6 = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_AC6, 2)   
     self.cal_B1  = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_B1, 2)   
     self.cal_B2  = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_B2, 2)   
     self.cal_MB  = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_MB, 2)   
     self.cal_MC  = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_MC, 2)    
     self.cal_MD  = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_CAL_MD, 2)     

   def _read_raw_temp(self):
     """Reads the raw (uncompensated) temperature from the sensor."""
     self.pi.i2c_write_byte_data(self.bus_handler, self.BMP085_CONTROL, self.BMP085_READTEMPCMD)
     time.sleep(0.005)  # Wait 5ms
     raw = self.pi.i2c_read_i2c_block_data(self.bus_handler, self.BMP085_TEMPDATA, 2)
     return raw

   def _read_raw_pressure(self):
     """Reads the raw (uncompensated) pressure level from the sensor."""
     self.pi.i2c_write_byte_data(self.bus_handler, self.BMP085_CONTROL, self.BMP085_READPRESSURECMD + (self.mode << 6))
     if self.mode == self.BMP085_ULTRALOWPOWER:
         time.sleep(0.005)
     elif self.mode == self.BMP085_HIGHRES:
         time.sleep(0.014)
     elif self.mode == self.BMP085_ULTRAHIGHRES:
         time.sleep(0.026)
     else:
         time.sleep(0.008)
     msb  = self.pi.i2c_read_byte_data(self.bus_handler, self.BMP085_PRESSUREDATA)
     lsb  = self.pi.i2c_read_byte_data(self.bus_handler, self.BMP085_PRESSUREDATA + 1)
     xlsb = self.pi.i2c_read_byte_data(self.bus_handler, self.BMP085_PRESSUREDATA + 2)
     raw = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - self.mode)
     return raw

   def read_temperature(self):
     """Gets the compensated temperature in degrees celsius."""
     UT = self._read_raw_temp()
     X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
     X2 = (self.cal_MC << 11) // (X1 + self.cal_MD)
     B5 = X1 + X2
     temp = ((B5 + 8) >> 4) / 10.0
     return temp

   def read_pressure(self):
      """Gets the compensated pressure in Pascals."""
      UT = self._read_raw_temp()
      UP = self._read_raw_pressure()
      X1 = ((UT - self.cal_AC6) * self.cal_AC5) >> 15
      X2 = (self.cal_MC << 11) // (X1 + self.cal_MD)
      B5 = X1 + X2

      # Pressure Calculations
      B6 = B5 - 4000
      X1 = (self.cal_B2 * (B6 * B6) >> 12) >> 11
      X2 = (self.cal_AC2 * B6) >> 11
      X3 = X1 + X2
      B3 = (((self.cal_AC1 * 4 + X3) << self._mode) + 2) // 4
      X1 = (self.cal_AC3 * B6) >> 13
      X2 = (self.cal_B1 * ((B6 * B6) >> 12)) >> 16
      X3 = ((X1 + X2) + 2) >> 2
      B4 = (self.cal_AC4 * (X3 + 32768)) >> 15
      B7 = (UP - B3) * (50000 >> self._mode)
      if B7 < 0x80000000:
          p = (B7 * 2) // B4
      else:
          p = (B7 // B4) * 2
      X1 = (p >> 8) * (p >> 8)
      X1 = (X1 * 3038) >> 16
      X2 = (-7357 * p) >> 16
      p = p + ((X1 + X2 + 3791) >> 4)

      return p

   def read_altitude(self, sealevel_pa=101325.0):
     """Calculates the altitude in meters."""
     pressure = float(self.read_pressure())
     altitude = 44330.0 * (1.0 - pow(pressure / sealevel_pa, (1.0/5.255)))
     return altitude

   def read_sealevel_pressure(self, altitude_m=0.0):
     """Calculates the pressure at sealevel when given a known altitude in
     meters. Returns a value in Pascals."""
     pressure = float(self.read_pressure())
     p0 = pressure / pow(1.0 - altitude_m/44330.0, 5.255)
     return p0
    
   def close(self):
     self.pi.i2c_close(self.bus_handler)
