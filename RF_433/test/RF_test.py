#!/usr/bin/env python

'''
Created on 1 juil. 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : Test RF 433 Mhz Reception and Transmission module 
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

   PIN_RX = 22
   PIN_TX = 17

   # define optional callback for received codes.

   def rx_callback(code, bits, gap, t0, t1):
      print("code={} bits={} (gap={} t0={} t1={})".
         format(code, bits, gap, t0, t1))

   pi = pigpio.pi() # Connect to local Pi.

   rx = RF_433_RX(pi, PIN_RX, callback=rx_callback, min_bits=8, max_bits=32, glitch=100)
   args = len(sys.argv)

   if args > 1:

      # If the script has arguments they are assumed to codes
      # to be transmitted.

      tx = RF_433_TX(pi, PIN_TX, repeats=6, bits=24, gap=5000, t0=150, t1=500)

      for i in range(args-1):
         print("sending {}".format(sys.argv[i+1]))
         tx.send(int(sys.argv[i+1]))
         time.sleep(1)

      tx.cancel() # Cancel the transmitter.

   time.sleep(60)

   rx.cancel() # Cancel the receiver.

   pi.stop() # Disconnect from local Pi.
