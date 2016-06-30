  #!/usr/bin/python
  
'''
Created on 30 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : Testing LCD Screen 16x2 Characters
'''

'''
Imports
'''
import pigpio
import os
import sys
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
from LCD_SCREEN_16x2.src.LCD_SCREEN_16x2 import LCD_16x2

if __name__ == "__main__":
  pi = pigpio.pi() # Connect to local Pi.
  pin_rs = 18
  pin_en = 23
  pin_d4 = 24
  pin_d5 = 25
  pin_d6 = 12
  pin_d7 = 16 
  screen = LCD_16x2(pi, pin_rs, pin_en, pin_d4, pin_d5, pin_d6, pin_d7)
  
  while 1:
    screen.clear()
    screen.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
    time.sleep(1)
