"""
--------------------------------------------------------------------------
Potentiometer Driver
--------------------------------------------------------------------------
License:   
Copyright 2023 <NAME>

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------

Potentiometer Driver for PocketBeagle

Software API:

  Potentiometer(pin)
    - Provide PocketBeagle pin that the potentiometer is connected

  get_value()
    - Returns the raw ADC value.  Integer in [0, 4095] 

  get_voltage()
    - Returns the approximate voltage of the pin in volts

"""
import Adafruit_BBIO.ADC as ADC
import os
import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM


# ------------------------------------------------------------------------
# Functions / Classes
# ------------------------------------------------------------------------
from timer import HT16K33
from potentiometer import Potentiometer
from button import Button
from buzzer import Buzzer


# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

# See https://en.wikipedia.org/wiki/Seven-segment_display for reference 

HEX_DIGITS                  = [0x3f, 0x06, 0x5b, 0x4f,     # 0, 1, 2, 3
                              0x66, 0x6d, 0x7d, 0x07,     # 4, 5, 6, 7
                              0x7f, 0x6f, 0x77, 0x7c,     # 8, 9, A, b
                              0x39, 0x5e, 0x79, 0x71]     # C, d, E, F

LETTERS                     = { "a" : 0x77, "A" : 0x77,    # "A"
                                "b" : 0x7c, "B" : 0x7c,    # "b"
                                "c" : 0x58, "C" : 0x39,    # "c", "C"
                                "d" : 0x5e, "D" : 0x5e,    # "d"
                                "e" : 0x79, "E" : 0x79,    # "E"
                                "f" : 0x71, "F" : 0x71,    # "F"
                                "g" : 0x6F, "G" : 0x6F,    # "g"
                                "h" : 0x74, "H" : 0x76,    # "h", "H"
                                "i" : 0x04, "I" : 0x30,    # "i", "I"
                                "j" : 0x0e, "J" : 0x0e,    # "J"
# Cannot be implemented         "k" : None, "K" : None,    
                                "l" : 0x38, "L" : 0x38,    # "L"
# Cannot be implemented         "m" : None, "M" : None,    
                                "n" : 0x54, "N" : 0x54,    # "n"
                                "o" : 0x5c, "O" : 0x3f,    # "o", "O"
                                "p" : 0x73, "P" : 0x73,    # "P"
                                "q" : 0x67, "Q" : 0x67,    # "q"
                                "r" : 0x50, "R" : 0x50,    # "r"
                                "s" : 0x6D, "S" : 0x6D,    # "S"
                                "t" : 0x78, "T" : 0x78,    # "t"
                                "u" : 0x1c, "U" : 0x3e,    # "u", "U"
# Cannot be implemented         "v" : None, "V" : None,    
# Cannot be implemented         "w" : None, "W" : None,    
# Cannot be implemented         "x" : None, "X" : None,    
                                "y" : 0x6e, "Y" : 0x6e,    # "y"
# Cannot be implemented         "z" : None, "Z" : None,    
                                " " : 0x00,                # " "
                                "-" : 0x40,                # "-"
                                "0" : 0x3f,                # "0"
                                "1" : 0x06,                # "1"
                                "2" : 0x5b,                # "2"
                                "3" : 0x4f,                # "3"
                                "4" : 0x66,                # "4"
                                "5" : 0x6d,                # "5"
                                "6" : 0x7d,                # "6"
                                "7" : 0x07,                # "7"
                                "8" : 0x7f,                # "8"
                                "9" : 0x6f,                # "9"
                                "?" : 0x53                 # "?"
                              }                               

CLEAR_DIGIT                 = 0x7F
POINT_VALUE                 = 0x80

DIGIT_ADDR                  = [0x00, 0x02, 0x06, 0x08]
COLON_ADDR                  = 0x04

HT16K33_BLINK_CMD           = 0x80
HT16K33_BLINK_DISPLAYON     = 0x01
HT16K33_BLINK_OFF           = 0x00
HT16K33_BLINK_2HZ           = 0x02
HT16K33_BLINK_1HZ           = 0x04
HT16K33_BLINK_HALFHZ        = 0x06

HT16K33_SYSTEM_SETUP        = 0x20
HT16K33_OSCILLATOR          = 0x01

HT16K33_BRIGHTNESS_CMD      = 0xE0
HT16K33_BRIGHTNESS_HIGHEST  = 0x0F
HT16K33_BRIGHTNESS_DARKEST  = 0x00

# Maximum decimal value that can be displayed on 4 digit Hex Display
HT16K33_MAX_VALUE           = 9999


# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------
MIN_VALUE     = 0
MAX_VALUE     = 4095


# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

HIGH          = GPIO.HIGH
LOW           = GPIO.LOW


# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

PINS_3V6 = ["P1_2", "P2_35"]
PINS_1V8 = ["P1_19", "P1_21", "P1_23", "P1_25", "P1_27", "P2_36"]
LED = 'P2_3'
buzz_LED = 'P2_6'
step = 5       # Step size
min =  0        # dimmest value
max =  100      # brightest value
brightness = min # Current brightness;

 


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':

    display = HT16K33(1, 0x70)
    display.set_colon(True)
    PWM.start(LED, brightness)
    GPIO.setup(buzz_LED, GPIO.OUT)

    # Create instantiation of the potentiometer
    pot = Potentiometer("P1_19")

    # Use a Keyboard Interrupt (i.e. "Ctrl-C") to exit the test
    print("Use Ctrl-C to Exit")
    
    
    # Create instantiation of the button
    button1 = Button("P2_2")
    button2 = Button("P2_4")
    button3 = Button("P2_8")
    buzzer = Buzzer("P2_1")
    
    # set booleans
    start_timer = False
    stop_timer = False
    buzz_on = False
    
    def light():
        PWM.start(LED, brightness)
        if button1.is_pressed():
            PWM.set_duty_cycle(LED, 100)
            time.sleep(0.1)
                
        if not button1.is_pressed():
            PWM.set_duty_cycle(LED, 0)
            time.sleep(0.1)
            
    def buzz_light(buzz_on):
        if button3.is_pressed():
                buzz_on = not buzz_on
                time.sleep(0.2)
                print(buzz_on)
        if buzz_on:
            GPIO.output(buzz_LED, GPIO.HIGH)

        if not buzz_on:
            GPIO.output(buzz_LED, GPIO.LOW)
        
        return buzz_on
            
        
    # end def
    
    def buzz():
        buzzer.play(880, 1.0, True)       # Play 440Hz for 1 second
        time.sleep(1.0)   
        buzzer.cleanup()
        
        
    
    try:
        while(1):
            light()
            buzz_on = buzz_light(buzz_on)
            
            # Get potentiometer value
            value = pot.get_value()
            
            # before starting timer, get start time, push button2 to start it
            if not start_timer:
                display.set_colon(True)
                
                if value > 0:
                    set_timer = int(value / 45) # make value from 0 --> 91 min
                    display.update(set_timer*100) # show amount of time
                    time.sleep(0.1)
                if button2.is_pressed():
                    start_timer = not start_timer
                    print(start_timer)
                    time.sleep(0.1)
                    
            t = int(value/45)*60  # number of seconds
            
            while t and start_timer: 
                light()
                buzz_on = buzz_light(buzz_on)
                mins, secs = divmod(t, 60) # split into min and sec
                timer = (mins*100) + secs # show XX min: XX sec
                display.update(timer) # display time
                time.sleep(0.25) # make into 1 second at the end
                t -= 1 
                
                
            while t == 0 and start_timer: # once countdown goes to zero
                light()
                buzz_on = buzz_light(buzz_on)
                letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ?"
                display.text("done")
                if buzz_on:
                    buzz()
                time.sleep(0.1)
                if button2.is_pressed():
                    display.clear()
                    display.set_colon(True)
                    time.sleep(0.1)
                    start_timer = not start_timer
                    print(start_timer)
    
                
    except KeyboardInterrupt:
        pass
    GPIO.cleanup()

    print("Test Complete")


