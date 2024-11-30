#!/usr/bin/python3
#//////////////////////////////////////
# 	fadeLED.py
#   Fades the LED wired to P2_3 using the PWM.
# 	Wiring:	P2_3 connects to the plus lead of an LED.  The negative lead of the
# 			LED goes to a 220 Ohm resistor.  The other lead of the resistor goes
# 			to 3.3V (P9_3).
#//////////////////////////////////////
import Adafruit_BBIO.PWM as PWM
import time
LED = 'P2_3'
step = 5       # Step size
min =  0        # dimmest value
max =  100      # brightest value
brightness = min # Current brightness;
 
PWM.start(LED, brightness)

while True:
    PWM.set_duty_cycle(LED, brightness)
    brightness += step
    if(brightness >= max or brightness <= min):
        step = -1 * step
    time.sleep(0.05)
