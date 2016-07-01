#!/usr/bin/env python

'''
Created on 1 juil. 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : RF 433 Mhz Reception module 
'''

'''
Imports
'''
import pigpio

class RF_433_RX:

   def __init__(self, pi, data_pin, callback=None,
                      min_bits=8, max_bits=32, glitch=150):
      """
      Codes with bit lengths outside the range min_bits to max_bits
      will be ignored.

      A glitch filter will be used to remove edges shorter than
      glitch us long from the wireless stream.  This is intended
      to remove the bulk of radio noise.
      """
      self.pi         = pi
      self.data_pin   = data_pin
      self.cb         = callback
      self.min_bits   = min_bits
      self.max_bits   = max_bits
      self.glitch     = glitch

      self._in_code   = False
      self._edge      = 0
      self._code      = 0
      self._gap       = 0

      self._ready = False

      pi.set_mode(data_pin, pigpio.INPUT)
      pi.set_glitch_filter(data_pin, glitch)

      self._last_edge_tick = pi.get_current_tick()
      self._cb = pi.callback(data_pin, pigpio.EITHER_EDGE, self._cbf)

   def _timings(self, e0, e1):
      """
      Accumulates the short and long pulse length so that an
      average short/long pulse length can be calculated. The
      figures may be used to tune the transimission settings.
      """
      if e0 < e1:
         shorter = e0
         longer = e1
      else:
         shorter = e1
         longer = e0

      if self._bits:
         self._t0 += shorter
         self._t1 += longer
      else:
         self._t0 = shorter
         self._t1 = longer

      self._bits += 1

   def _calibrate(self, e0, e1):
      """
      The first pair of pulses is used as the template for
      subsequent pulses.  They should be one short, one long, not
      necessarily in that order.  The ratio between long and short
      should really be 2 or more.  If less than 1.5 the pulses are
      assumed to be noise.
      """
      self._bits = 0
      self._timings(e0, e1)
      self._bits = 0

      ratio = float(self._t1)/float(self._t0)

      if ratio < 1.5:
         self._in_code = False

      slack0 = int(0.3 * self._t0)
      slack1 = int(0.2 * self._t1)

      self._min_0 = self._t0 - slack0
      self._max_0 = self._t0 + slack0
      self._min_1 = self._t1 - slack1
      self._max_1 = self._t1 + slack1

   def _test_bit(self, e0, e1):
      """
      Returns the bit value represented by the sequence of pulses.

      0: short long
      1: long short
      2: illegal sequence
      """
      self._timings(e0, e1)

      if   ( (self._min_0 < e0 < self._max_0) and
             (self._min_1 < e1 < self._max_1) ):
         return 0
      elif ( (self._min_0 < e1 < self._max_0) and
             (self._min_1 < e0 < self._max_1) ):
         return 1
      else:
         return 2

   def _cbf(self, g, l, t):
      """
      Accumulates the code from pairs of short/long pulses.
      The code end is assumed when an edge greater than 5 ms
      is detected.
      """
      edge_len = pigpio.tickDiff(self._last_edge_tick, t)
      self._last_edge_tick = t

      if edge_len > 5000: # 5000 us, 5 ms.

         if self._in_code:
            if self.min_bits <= self._bits <= self.max_bits:
               self._lbits = self._bits
               self._lcode = self._code
               self._lgap = self._gap
               self._lt0 = int(self._t0/self._bits)
               self._lt1 = int(self._t1/self._bits)
               self._ready = True
               if self.cb is not None:
                  self.cb(self._lcode, self._lbits,
                          self._lgap, self._lt0, self._lt1)

         self._in_code = True
         self._gap = edge_len
         self._edge = 0
         self._bits = 0
         self._code = 0

      elif self._in_code:

         if self._edge == 0:
            self._e0 = edge_len
         elif self._edge == 1:
            self._calibrate(self._e0, edge_len)

         if self._edge % 2: # Odd edge.

            bit = self._test_bit(self._even_edge_len, edge_len)
            self._code = self._code << 1
            if bit == 1:
               self._code += 1
            elif bit != 0:
               self._in_code = False

         else: # Even edge.

            self._even_edge_len = edge_len

         self._edge += 1

   def ready(self):
      return self._ready

   def code(self):
      self._ready = False
      return self._lcode

   def details(self):
      """
      Returns details of the last receieved code.  The details
      consist of the code, the number of bits, the length (in us)
      of the gap, short pulse, and long pulse.
      """
      self._ready = False
      return self._lcode, self._lbits, self._lgap, self._lt0, self._lt1

   def cancel(self):
      """
      Cancels the wireless code receiver.
      """
      if self._cb is not None:
         self.pi.set_glitch_filter(self.data_pin, 0) # Remove glitch filter.
         self._cb.cancel()
         self._cb = None