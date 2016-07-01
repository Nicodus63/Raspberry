#!/usr/bin/env python

'''
Created on 1 juil. 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : Test RF 433 Mhz Reception module 
'''

'''
Imports
'''
import pigpio
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '../..'))
 
from RF_433.src.RF_433_RX import RF_433_RX
from RF_433.src.RF_433_TX import RF_433_TX

if __name__ == "__main__":

   PIN_RX=22
   PIN_TX=17

   # define optional callback for received codes.

   def rx_callback(code, bits, gap, t0, t1):
      print("code={} bits={} (gap={} t0={} t1={})".
         format(code, bits, gap, t0, t1))

   pi = pigpio.pi() # Connect to local Pi.

   rx = RF_433_RX(pi, PIN_RX, callback=rx_callback)

   args = len(sys.argv)

   time.sleep(60)

   rx.cancel() # Cancel the receiver.

   pi.stop() # Disconnect from local Pi.
