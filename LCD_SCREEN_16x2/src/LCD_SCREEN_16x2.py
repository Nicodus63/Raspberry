  #!/usr/bin/python
  
'''
Created on 30 juin 2016

@author     : ARVEUF Nicolas
@Version    : 1.0
@requires   : Pigpio
@note       : LCD Screen 16x2 Characters
'''

''' 
Imports
'''
import time
import pigpio


class LCD_16x2:
   # Commands
   LCD_CLEARDISPLAY        = 0x01
   LCD_RETURNHOME          = 0x02
   LCD_ENTRYMODESET        = 0x04
   LCD_DISPLAYCONTROL      = 0x08
   LCD_CURSORSHIFT         = 0x10
   LCD_FUNCTIONSET         = 0x20
   LCD_SETCGRAMADDR        = 0x40
   LCD_SETDDRAMADDR        = 0x80
  
   # Entry flags
   LCD_ENTRYRIGHT          = 0x00
   LCD_ENTRYLEFT           = 0x02
   LCD_ENTRYSHIFTINCREMENT = 0x01
   LCD_ENTRYSHIFTDECREMENT = 0x00
   
   # Control flags
   LCD_DISPLAYON           = 0x04
   LCD_DISPLAYOFF          = 0x00
   LCD_CURSORON            = 0x02
   LCD_CURSOROFF           = 0x00
   LCD_BLINKON             = 0x01
   LCD_BLINKOFF            = 0x00
  
   # Move flags
   LCD_DISPLAYMOVE         = 0x08
   LCD_CURSORMOVE          = 0x00
   LCD_MOVERIGHT           = 0x04
   LCD_MOVELEFT            = 0x00
   
   # Function set flags
   LCD_4BITMODE            = 0x00
   LCD_2LINE               = 0x08
   LCD_1LINE               = 0x00
   LCD_5x10DOTS            = 0x04
   LCD_5x8DOTS             = 0x00
  
   # Offset for up to 4 rows.
   LCD_ROW_OFFSETS         = (0x00, 0x40, 0x14, 0x54)
  
   # Char LCD plate GPIO numbers.
   LCD_PLATE_RS            = 15
   LCD_PLATE_RW            = 14
   LCD_PLATE_EN            = 13
   LCD_PLATE_D4            = 12
   LCD_PLATE_D5            = 11
   LCD_PLATE_D6            = 10
   LCD_PLATE_D7            = 9
   
   LCD_COLS                = 16
   LCD_LINES               = 2

   def __init__(self, pi, rs, en, d4, d5, d6, d7):
        ''' Command LCD in 4 bits mode - Read LCD status is not available '''
        self.pi = pi

        # Save column and line state.
        self._cols = self.LCD_COLS
        self._lines = self.LCD_LINES
        # Save pin numbers.
        self._rs = rs
        self._en = en
        self._d4 = d4
        self._d5 = d5
        self._d6 = d6
        self._d7 = d7

        # Setup all pins as outputs.
        for pin in (rs, en, d4, d5, d6, d7):
            self.pi.set_mode(pin, pigpio.OUTPUT)

        # Initialize the display.
        self.write8(0x33)
        self.write8(0x32)
        # Initialize display control, function, and mode registers.
        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_2LINE | self.LCD_5x8DOTS
        self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        # Write registers.
        self.write8(self.LCD_DISPLAYCONTROL | self.displaycontrol)
        self.write8(self.LCD_FUNCTIONSET | self.displayfunction)
        self.write8(self.LCD_ENTRYMODESET | self.displaymode)  # set the entry mode
        self.clear()

   def home(self):
        """Move the cursor back to its home (first line and first column)."""
        self.write8(self.LCD_RETURNHOME)  # set cursor position to zero
        self._delay_microseconds(3000)  # this command takes a long time!

   def clear(self):
        """Clear the LCD."""
        self.write8(self.LCD_CLEARDISPLAY)  # command to clear display
        self._delay_microseconds(3000)  # 3000 microsecond sleep, clearing the display takes a long time

   def set_cursor(self, col, row):
        """Move the cursor to an explicit column and row position."""
        # Clamp row to the last row of the display.
        if row > self._lines:
            row = self._lines - 1
        # Set location.
        self.write8(self.LCD_SETDDRAMADDR | (col + self.LCD_ROW_OFFSETS[row]))

   def enable_display(self, enable):
        """Enable or disable the display.  Set enable to True to enable."""
        if enable:
            self.displaycontrol |= self.LCD_DISPLAYON
        else:
            self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write8(self.LCD_DISPLAYCONTROL | self.displaycontrol)

   def show_cursor(self, show):
        """Show or hide the cursor.  Cursor is shown if show is True."""
        if show:
            self.displaycontrol |= self.LCD_CURSORON
        else:
            self.displaycontrol &= ~self.LCD_CURSORON
        self.write8(self.LCD_DISPLAYCONTROL | self.displaycontrol)

   def blink(self, blink):
        """Turn on or off cursor blinking.  Set blink to True to enable blinking."""
        if blink:
            self.displaycontrol |= self.LCD_BLINKON
        else:
            self.displaycontrol &= ~self.LCD_BLINKON
        self.write8(self.LCD_DISPLAYCONTROL | self.displaycontrol)

   def move_left(self):
        """Move display left one position."""
        self.write8(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

   def move_right(self):
        """Move display right one position."""
        self.write8(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT)

   def set_left_to_right(self):
        """Set text direction left to right."""
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write8(self.LCD_ENTRYMODESET | self.displaymode)

   def set_right_to_left(self):
        """Set text direction right to left."""
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write8(self.LCD_ENTRYMODESET | self.displaymode)

   def autoscroll(self, autoscroll):
        """Autoscroll will 'right justify' text from the cursor if set True,
        otherwise it will 'left justify' the text.
        """
        if autoscroll:
            self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        else:
            self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write8(self.LCD_ENTRYMODESET | self.displaymode)

   def message(self, text):
        """Write text to display.  Note that text can include newlines."""
        line = 0
        # Iterate through each character.
        for char in text:
            # Advance to next line if character is a new line.
            if char == '\n':
                line += 1
                # Move to left or right side depending on text direction.
                col = 0 if self.displaymode & self.LCD_ENTRYLEFT > 0 else self._cols-1
                self.set_cursor(col, line)
            # Write the character to the display.
            else:
                self.write8(ord(char), True)

   def write8(self, value, char_mode=False):
        """Write 8-bit value in character or data mode.  Value should be an int
        value from 0-255, and char_mode is True if character data or False if
        non-character data (default).
        """
        # One millisecond delay to prevent writing too quickly.
        self._delay_microseconds(1000)
        # Set character / data bit.
        self.pi.write(self._rs, char_mode)
        # Write upper 4 bits.
        self.pi.write(self._d4, (value >> 4) & 1)
        self.pi.write(self._d5, (value >> 5) & 1)
        self.pi.write(self._d6, (value >> 6) & 1)
        self.pi.write(self._d7, (value >> 7) & 1)

        self._pulse_enable()
        
        # Write lower 4 bits.
        self.pi.write(self._d4, value & 1)
        self.pi.write(self._d5, (value >> 1) & 1)
        self.pi.write(self._d6, (value >> 2) & 1)
        self.pi.write(self._d7, (value >> 3) & 1)

        self._pulse_enable()

   def create_char(self, location, pattern):
        """Fill one of the first 8 CGRAM locations with custom characters.
        The location parameter should be between 0 and 7 and pattern should
        provide an array of 8 bytes containing the pattern. E.g. you can easyly
        design your custom character at http://www.quinapalus.com/hd44780udg.html
        To show your custom character use eg. lcd.message('\x01')
        """
        # only position 0..7 are allowed
        location &= 0x7
        self.write8(self.LCD_SETCGRAMADDR | (location << 3))
        for i in range(8):
            self.write8(pattern[i], char_mode=True)

   def _delay_microseconds(self, microseconds):
        # Busy wait in loop because delays are generally very short (few microseconds).
        end = time.time() + (microseconds/1000000.0)
        while time.time() < end:
            pass

   def _pulse_enable(self):
        # Pulse the clock enable line off, on, off to send command.
        self.pi.write(self._en, False)
        self._delay_microseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns
        self.pi.write(self._en, True)
        self._delay_microseconds(1)       # 1 microsecond pause - enable pulse must be > 450ns
        self.pi.write(self._en, False)
        self._delay_microseconds(1)       # commands need > 37us to settle
