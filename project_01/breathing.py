import time
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
from button import Button

# Pin configuration
BUTTON_PIN = "P2_2"
LED = "P2_3"

# Setup GPIO and PWM
GPIO.setup(BUTTON_PIN, GPIO.IN)
PWM.start(LED, 0)  # Start with 0% duty cycle

# Variables
brightness = 0          # Current brightness (0-100%)
state = "fade_up"       # Initial state: "fade_up", "hold", or "fade_down"
state_start_time = time.time()  # Record when the state started

# Time durations for each state
fade_up_duration = 4  # seconds
hold_duration = 7     # seconds
fade_down_duration = 8  # seconds


def Breathing(state_start_time, state, fade_up_duration, hold_duration, fade_down_duration):
    button = Button("P2_2")
    PWM.set_duty_cycle(LED, 100)
    time.sleep(0.1)
    PWM.set_duty_cycle(LED, 0)
    time.sleep(0.1)
    start_breathe = True
    print("starting")
    print(start_breathe)
    while start_breathe:
        current_time = time.time()
        elapsed_time = current_time - state_start_time
        if button.is_pressed():
            start_breathe = False
            print(start_breathe)
            time.sleep(0.1)
        if state == "fade_up":
            # print("fade up")
            # Calculate brightness based on elapsed time
            brightness = min(100, (elapsed_time / fade_up_duration) * 100)
            print(brightness)
            PWM.set_duty_cycle(LED, brightness)
            if elapsed_time >= fade_up_duration:
                state = "hold"
                PWM.set_duty_cycle(LED, 0)
                time.sleep(0.1)
                state_start_time = current_time  # Reset state start time
    
        elif state == "hold":
            # print("hold")
            # Keep brightness at max
            PWM.set_duty_cycle(LED, 100)
            if elapsed_time >= hold_duration:
                state = "fade_down"
                PWM.set_duty_cycle(LED, 0)
                time.sleep(0.1)
                state_start_time = current_time  # Reset state start time
    
        elif state == "fade_down":
            # print("fade down")
            # Calculate brightness based on elapsed time
            brightness = max(0, 100 - (elapsed_time / fade_down_duration) * 100)
            print(brightness)
            PWM.set_duty_cycle(LED, brightness)
            if elapsed_time >= fade_down_duration:
                state = "fade_up"  # Optional: You can stop or loop the behavior
                PWM.set_duty_cycle(LED, 0)
                time.sleep(0.1)
                state_start_time = current_time  # Reset state start time
        if button.is_pressed():
            start_breathe = False
            print("stop!!!")
            PWM.set_duty_cycle(LED, 0)
            time.sleep(0.1)
            return
        
    else:
        PWM.set_duty_cycle(LED, 0)
        return
    # Small delay to reduce CPU usage
    time.sleep(0.1)
    

try:
    print("starting ...")
    # while True:
    Breathing(state_start_time, state, 4, 7, 8)
    time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    PWM.stop(LED)
    PWM.cleanup()
    GPIO.cleanup()
