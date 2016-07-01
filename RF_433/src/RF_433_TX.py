#!/usr/bin/env python

'''
Created on 1 juil. 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : RF 433 Mhz Transmission module 
'''

'''
Imports
'''
import time
import pigpio

class RF_433_TX:

   def __init__(self, pi, data_pin, repeats=6, bits=24, gap=9000, t0=300, t1=900):
      """
      The pre-/post-amble gap (default 9000 us), short pulse length
      (default 300 us), and long pulse length (default 900 us) may
      be set.
      """
      self.pi       = pi
      self.data_pin = data_pin
      self.repeats  = repeats
      self.bits     = bits
      self.gap      = gap
      self.t0       = t0
      self.t1       = t1

      self._make_waves()

      pi.set_mode(data_pin, pigpio.OUTPUT)

   def _make_waves(self):
      """
      Generates the basic waveforms needed to transmit codes.
      """
      wf = []
      wf.append(pigpio.pulse(1<<self.data_pin, 0, self.t0))
      wf.append(pigpio.pulse(0, 1<<self.data_pin, self.gap))
      self.pi.wave_add_generic(wf)
      self._amble = self.pi.wave_create()

      wf = []
      wf.append(pigpio.pulse(1<<self.data_pin, 0, self.t0))
      wf.append(pigpio.pulse(0, 1<<self.data_pin, self.t1))
      self.pi.wave_add_generic(wf)
      self._wid0 = self.pi.wave_create()

      wf = []
      wf.append(pigpio.pulse(1<<self.data_pin, 0, self.t1))
      wf.append(pigpio.pulse(0, 1<<self.data_pin, self.t0))
      self.pi.wave_add_generic(wf)
      self._wid1 = self.pi.wave_create()

   def set_repeats(self, repeats):
      if 1 < repeats < 100:
         self.repeats = repeats

   def set_bits(self, bits):
      if 5 < bits < 65:
         self.bits = bits

   def set_timings(self, gap, t0, t1):
      """
      Sets the code gap, short pulse, and long pulse length in us.
      """
      self.gap = gap
      self.t0 = t0
      self.t1 = t1

      self.pi.wave_delete(self._amble)
      self.pi.wave_delete(self._wid0)
      self.pi.wave_delete(self._wid1)

      self._make_waves()

   def send(self, code):
      """
      Transmits the code (using the current settings of repeats,
      bits, gap, short, and long pulse length).
      """
      chain = [self._amble, 255, 0]

      bit = (1<<(self.bits-1))
      for i in range(self.bits):
         if code & bit:
            chain += [self._wid1]
         else:
            chain += [self._wid0]
         bit = bit >> 1

      chain += [self._amble, 255, 1, self.repeats, 0]

      self.pi.wave_chain(chain)

      while self.pi.wave_tx_busy():
         time.sleep(0.1)

   def cancel(self):
      """
      Cancels the wireless code transmitter.
      """
      self.pi.wave_delete(self._amble)
      self.pi.wave_delete(self._wid0)
      self.pi.wave_delete(self._wid1)
