'''
Created on 26 juin 2016

@author: ARVEUF N
'''
import pigpio
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
 
from LCD_128x128.src.TFT144 import TFT144

if __name__ == "__main__":
 
   pi = pigpio.pi() # Connect to local Pi. 
   pin_reset = 6
   pin_dc = 5
 
   screen = TFT144(pi, pin_reset, pin_dc)
   screen.init_LCD(0)
   '''screen.reset_LCD()'''
   screen.draw_filled_rectangle(10, 10, 60, 60, screen.BLUE)
   screen.draw_circle(75, 75, 30, screen.RED)