#!/usr/bin/env python

'''
Created on : 26 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio - A bmp Image 128*128
@note       : Testing screen 128x128 

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
   pin_ce = 0
   orientation = TFT144.ORIENTATION180
 
   screen = TFT144(pi, pin_reset, pin_dc, pin_ce, 1, orientation)
   screen.clear_display(screen.BLACK)
   screen.normal_screen()

   ''' Print an image - Relative path from Raspberry repo '''
   if os.path.exists("./LCD_128x128/test/lena.bmp"):
     print "Image test"
     screen.draw_bmp("./LCD_128x128/test/lena.bmp", 0, 0)
   else:
     print "Blue rectangle"
     screen.draw_filled_rectangle(10, 10, 60, 60, screen.BLUE)
     
   screen.close_spi()
   