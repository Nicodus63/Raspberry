#!/usr/bin/env python
'''
Created on : 29 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio and lcdfonts
@note       : 128x128 LCD Screen 

'''

'''
Imports
'''
from time import sleep
import os
import pigpio
from lcdfonts import *

class TFT144:
   ''' SPI constants '''
   SPI_SPEED   = 16000000
   SPI_MODE    = 0
   
   ''' ORIENTATIONS '''
   ORIENTATION0   = 0
   ORIENTATION90  = 96
   ORIENTATION270 = 160
   ORIENTATION180 = 192
   
   ''' SCREEN DIMENSIONS '''
   TFTWIDTH    = 128
   TFTHEIGHT   = 128
   
   ''' COMMANDS '''
   NOP                    = 0x00
   SOFT_RESET             = 0x01
   ENTER_SLEEP_MODE       = 0x10
   EXIT_SLEEP_MODE        = 0x11
   ENTER_PARTIAL_MODE     = 0x12
   ENTER_NORMAL_MODE      = 0x13
   EXIT_INVERT_MODE       = 0x20
   ENTER_INVERT_MODE      = 0x21
   SET_GAMMA_CURVE        = 0x26
   SET_DISPLAY_OFF        = 0x28
   SET_DISPLAY_ON         = 0x29
   SET_COLUMN_ADDRESS     = 0x2A
   SET_PAGE_ADDRESS       = 0x2B
   WRITE_MEMORY_START     = 0x2C
   SET_PARTIAL_AREA       = 0x30
   SET_SCROLL_AREA        = 0x33
   SET_ADDRESS_MODE       = 0x36
   SET_SCROLL_START       = 0X37
   EXIT_IDLE_MODE         = 0x38
   ENTER_IDLE_MODE        = 0x39
   SET_PIXEL_FORMAT       = 0x3A
   WRITE_MEMORY_CONTINUE  = 0x3C
   READ_MEMORY_CONTINUE   = 0x3E
   FRAME_RATE_CONTROL1    = 0xB1
   FRAME_RATE_CONTROL2    = 0xB2
   FRAME_RATE_CONTROL3    = 0xB3
   DISPLAY_INVERSION      = 0xB4
   POWER_CONTROL1         = 0xC0 
   POWER_CONTROL2         = 0xC1
   POWER_CONTROL3         = 0xC2
   POWER_CONTROL4         = 0xC3
   POWER_CONTROL5         = 0xC4
   VCOM_CONTROL1          = 0xC5
   VCOM_CONTROL2          = 0xC6
   VCOM_OFFSET_CONTROL    = 0xC7
   POSITIVE_GAMMA_CORRECT = 0xE0
   NEGATIVE_GAMMA_CORRECT = 0xE1
   GAM_R_SEL              = 0xF2
   
   ''' Fonts '''
   fontDim = ([0], [4, 6, 1], [8, 12, 2], [6, 8, 1], [12, 16, 2], [8, 12, 1], [16, 24, 2], [8, 16, 1], [16, 32, 2])
   # Font dimensions for fonts 1-8.  [W, H, Scale]
   fontW = 0  # These are valid only AFTER a char was displayed
   fontH = 0
 
   def __init__(self, pi, pin_reset, pin_dc, pin_ce, is_redboard, orientation = ORIENTATION0):
     ''' Color defines '''
     self.BLUE       = self.colour565(0,0,255)
     self.GREEN      = self.colour565(0,255, 0)
     self.RED        = self.colour565(255,0,0)
     self.PINK       = self.colour565(255,120,120)
     self.LIGHTBLUE  = self.colour565(120,120,255)
     self.LIGHTGREEN = self.colour565(120,255,120)
     self.BLACK      = self.colour565(0,0,0)
     self.WHITE      = self.colour565(255,255,255)
     self.GREY       = self.colour565(120,120,120)
     self.YELLOW     = self.colour565(255,255,0)
     self.MAGENTA    = self.colour565(255,0,255)
     self.CYAN       = self.colour565(0,255,255)
     
     self.orientation = orientation
     self.is_redboard = is_redboard

     ''' Define pins and modes '''
     self.RST = pin_reset
     self.DC  = pin_dc # A0
     
     self.pi = pi
     
     pi.set_mode(self.DC, pigpio.OUTPUT)
     pi.write(self.DC, 1)
     
     pi.set_mode(self.RST, pigpio.OUTPUT)
     pi.write(self.RST, 1)
     
     ''' Open SPI bus '''
     self.spi_handler = pi.spi_open(pin_ce, self.SPI_SPEED, self.SPI_MODE)
    
     sleep(0.5)
     self.init_LCD(orientation)

   # function to pack 3 bytes of rgb value in 2 byte integer, R,G and B 0-255
   def colour565(self, r, g, b):
     return ((b & 0xF8) << 8) | ((g & 0xFC) << 3) | (r >> 3)

   # functions to translate x,y pixel coords. to text column,row
   def textX(self, x, font=3):
     return x * (self.fontDim[font][0])

   def textY(self, y, font=3):
     return y * (self.fontDim[font][1])

   # initial LCD reset
   def reset_LCD(self):
     if self.RST == 0:
         self.write_command(self.SOFT_RESET)
     else:
         self.pi.write(self.RST, 0)
         sleep (0.2)
         self.pi.write(self.RST, 1)
     sleep (0.2)
     return

    # write command to controller
   def write_command(self, address):
     self.pi.write(self.DC, 0)
     self.pi.spi_write(self.spi_handler, [address])

    # write data
   def write_data(self, data):
     self.pi.write(self.DC, 1)
     if not type(data) == type([]):  # is it already a list?
          data = [data]
     self.pi.spi_write(self.spi_handler, data)

   def init_LCD(self, orientation):
     self.reset_LCD()
     self.write_command(self.EXIT_SLEEP_MODE)
     sleep(0.05)
     self.write_command(self.SET_PIXEL_FORMAT)
     self.write_data(0x05)
     self.write_command(self.SET_GAMMA_CURVE)
     self.write_data(0x04)
     self.write_command(self.GAM_R_SEL)
     self.write_data(0x01)
     
     self.write_command(self.POSITIVE_GAMMA_CORRECT)
     self.write_data([0x3f, 0x25, 0x1c, 0x1e, 0x20, 0x12, 0x2a, 0x90, 0x24, 0x11, 0, 0, 0, 0, 0])
     
     self.write_command(self.NEGATIVE_GAMMA_CORRECT)
     self.write_data([0x20, 0x20, 0x20, 0x20, 0x05, 0, 0x15, 0xa7, 0x3d, 0x18, 0x25, 0x2a, 0x2b, 0x2b, 0x3a])
     self.write_command(self.FRAME_RATE_CONTROL1)
     self.write_data([0x08, 0x08])
     
     self.write_command(self.DISPLAY_INVERSION)
     self.write_data(0x01)
     
     self.write_command(self.POWER_CONTROL1)
     self.write_data([0x0a, 0x02])
     
     self.write_command(self.POWER_CONTROL2)
     self.write_data(0x02)
     
     self.write_command(self.VCOM_CONTROL1)
     self.write_data([0x50, 0x5b])
     
     self.write_command(self.VCOM_OFFSET_CONTROL)
     self.write_data(0x40)
     self.set_frame()
     
     self.write_command(self.SET_ADDRESS_MODE)
     self.write_data(orientation)
     
     self.clear_display(self.BLACK)
     self.write_command(self.SET_DISPLAY_ON)

   # clear display,writes same color pixel in all screen
   def clear_display(self, color):
     color_hi = color >> 8
     color_lo = color & (~(65280))
     self.set_frame()
     self.write_command(self.WRITE_MEMORY_START)

     # Repetitively push out all those identical pixels
     for row in range(self.TFTHEIGHT):
       self.write_data([color_hi, color_lo] * self.TFTWIDTH)

   def set_frame(self, x1=0, x2=TFTWIDTH - 1, y1=0, y2=TFTHEIGHT - 1):
     if self.is_redboard:
         if self.orientation == self.ORIENTATION0:
             y1 += 32
             y2 += 32
         if self.orientation == self.ORIENTATION90:
             x1 += 32
             x2 += 32
     self.write_command(self.SET_COLUMN_ADDRESS)
     self.write_data([0, x1, 0, x2])
     self.write_command(self.SET_PAGE_ADDRESS)
     self.write_data([0, y1, 0, y2])

   # draw a dot in x,y with 'color' colour
   def draw_dot(self, x, y, color):
     color_hi = color >> 8
     color_lo = color & (~(65280))
     self.set_frame(x, x + 1, y, y + 1)
     self.write_command(self.WRITE_MEMORY_START)
     self.write_data([color_hi, color_lo])

    # Bresenham's algorithm to draw a line with integers
    # x0<=x1, y0<=y1
   def draw_line(self, x0, y0, x1, y1, color):
     dy = y1 - y0
     dx = x1 - x0
     if (dy < 0):
        dy = -dy
        stepy = -1
     else:
        stepy = 1
     if (dx < 0):
        dx = -dx
        stepx = -1
     else:
        stepx = 1
     dx <<= 1
     dy <<= 1
     self.draw_dot(x0, y0, color)
     if (dx > dy):
        fraction = dy - (dx >> 1)
        while (x0 != x1):
           if (fraction >= 0):
              y0 += stepy
              fraction -= dx
           x0 += stepx
           fraction += dy
           self.draw_dot(x0, y0, color)
     else:
        fraction = dx - (dy >> 1)
        while (y0 != y1):
           if (fraction >= 0):
              x0 += stepx
              fraction -= dy
           y0 += stepy
           fraction += dx
           self.draw_dot(x0, y0, color)

    # draws hollow rectangle
    # x0<=x1, y0<= y1
   def draw_rectangle(self, x0, y0, x1, y1, color):
     self.draw_line(x0, y0, x0, y1, color)
     self.draw_line(x0, y1, x1, y1, color)
     self.draw_line(x1, y0, x1, y1, color)
     self.draw_line(x0, y0, x1, y0, color)

    # draws filled rectangle, fills frame memory section with same pixel
    # x0<=x1, y0<=y1
   def draw_filled_rectangle(self, x0, y0, x1, y1, color):
     color_hi = color >> 8
     color_lo = color & (~(65280))
     self.set_frame(x0, x1, y0, y1)

     self.write_command(self.WRITE_MEMORY_START)
     for pixels in range (0, (1 + x1 - x0)):
          dbuf = [color_hi, color_lo] * (y1 - y0)
          self.write_data(dbuf)

    # Bresenham's circle algorithm, circle can't pass screen boundaries
   def draw_circle(self, x0, y0, radio, color):
     error = 1 - radio
     errorx = 1
     errory = -2 * radio
     y = radio
     x = 0
     self.draw_dot(x0, y0 + radio, color)
     self.draw_dot(x0, y0 - radio, color)
     self.draw_dot(x0 + radio, y0, color)
     self.draw_dot(x0 - radio, y0, color)
     while (x < y):
        if (error >= 0):
           y -= 1
           errory += 2
           error += errory
        x += 1
        errorx += 2
        error += errorx
        self.draw_dot(x0 + x, y0 + y, color)
        self.draw_dot(x0 - x, y0 + y, color)
        self.draw_dot(x0 + x, y0 - y, color)
        self.draw_dot(x0 - x, y0 - y, color)
        self.draw_dot(x0 + y, y0 + x, color)
        self.draw_dot(x0 - y, y0 + x, color)
        self.draw_dot(x0 + y, y0 - x, color)
        self.draw_dot(x0 - y, y0 - x, color)

    # writes a character in graphic coordinates x,y, with
    # foreground and background colours
   def put_char(self, character, x, y, fgcolor, bgcolor, font=3):
     fgcolor_hi = fgcolor >> 8
     fgcolor_lo = fgcolor & (~(65280))
     bgcolor_hi = bgcolor >> 8
     bgcolor_lo = bgcolor & (~(65280))
     self.fontW = self.fontDim[font][0]
     self.fontH = self.fontDim[font][1]
     fontScale = self.fontDim[font][2]
     character = ord(character)
     if not (font == 3 or font == 4):  # restricted char set 32-126 for most
         if character < 32 or character > 126:  # only strictly ascii chars
           character = 0
         else:
           character -= 32
     self.set_frame(x, (x + self.fontW - 1), y, (y + self.fontH - 1))
     xx = [0]
     if fontScale == 2:
         xx = [0, 2, 2 * self.fontW, 2 + (2 * self.fontW) ]  # DOUBLE: every pixel becomes a 2x2 pixel

     self.write_command(self.WRITE_MEMORY_START)
     cbuf = [0] * (self.fontW * self.fontH * 2)
     for row in range (0, int(self.fontH // fontScale)):
        for column in range (0, int(self.fontW // fontScale)):
           topleft = ((column * 2 * fontScale) + (row * 2 * self.fontW * fontScale))
           if font <= 2:
              pixOn = (font4x6[character][row]) & (1 << column)
           elif font >= 7:
              pixOn = (font8x16[character][row]) & (1 << column)
           elif font >= 5:
              pixOn = (font8x12[character][row]) & (1 << column)
           else:
              pixOn = (font6x8[character][column]) & (1 << row)
           if pixOn:
               for rpt in xx:  # one pixel or a 2x2 "doubled" pixel
                  cbuf[rpt + topleft] = fgcolor_hi
                  cbuf[rpt + 1 + topleft] = fgcolor_lo
           else:
               for rpt in xx:
                  cbuf[rpt + topleft] = bgcolor_hi
                  cbuf[rpt + 1 + topleft] = bgcolor_lo
     self.write_data(cbuf)

    # writes a string in graphic x,y coordinates, with
    # foreground and background colours. If edge of screen is reached,
    # it wraps to next text line to same starting x coord.
   def put_string(self, str, originx, y, fgcolor, bgcolor, font=3):
     x = originx
     fontW = self.fontDim[font][0]
     fontH = self.fontDim[font][1]
     for char_number in range (0, len(str)):
        if ((x + fontW) > self.TFTWIDTH):
           x = originx
           y += (fontH)
        if ((y + fontH) > self.TFTHEIGHT):
           break
        self.put_char(str[char_number], x, y, fgcolor, bgcolor, font)
        x += (fontW)

   def draw_bmp(self, filename, x0=0, y0=0):
      if not os.path.exists(filename):
          return False
      with open(filename, 'rb') as bitmap_file:
          bitmap_file.seek(18)
          w = ord(bitmap_file.read(1))
          bitmap_file.seek(22)
          h = ord(bitmap_file.read(1))
          bitmap_file.seek(10)
          start = ord(bitmap_file.read(1))
          bitmap_file.seek(start)
          self.set_frame(x0, x0 + w - 1, y0, y0 + h - 1)
          self.write_command(self.WRITE_MEMORY_START)
          for y in range(h):  # 3 bytes of colour / pixel
                dbuf = [0] * (w * 2)
                for x in range(w):
                    b = ord(bitmap_file.read(1))
                    g = ord(bitmap_file.read(1))
                    r = ord(bitmap_file.read(1))
                    RGB = self.colour565(r, g, b)
                    # RGB = self.YELLOW
                    dbuf[2 * x] = RGB >> 8
                    dbuf[1 + (2 * x)] = RGB & (~65280)
                self.write_data(dbuf)
                # Now, BMP has a 4byte alignment issue at end of each line   V1.0.1
                x = 3 * w  # bytes in line @ 3bytes/pixel
                while (x % 4):
                    x += 1
                    bitmap_file.read(1)  # waste a byte until aligned
      return True

   def invert_screen(self):
     self.write_command(self.ENTER_INVERT_MODE)

   def normal_screen(self):
     self.write_command(self.EXIT_INVERT_MODE)
       
   def close_spi(self):
     self.pi.spi_close(self.spi_handler)