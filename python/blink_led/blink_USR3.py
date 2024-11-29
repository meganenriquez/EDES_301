#!/usr/bin/python3
#//////////////////////////////////////
#	blink_USR3.py
#	Blinks USR3 LED at 5 Hz
#	Wiring:	just connected to beaglebone
#	Setup:	
#	See:	https://github.com/adafruit/adafruit-beaglebone-io-python/tree/master
#//////////////////////////////////////
import Adafruit_BBIO.GPIO as GPIO
import time

out = "USR3" # blink USR3 LED
 
GPIO.setup(out, GPIO.OUT)
 
while True:
    GPIO.output(out, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(out, GPIO.LOW)
    time.sleep(0.5)
