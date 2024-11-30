"""
--------------------------------------------------------------------------
Button Driver
--------------------------------------------------------------------------
License:   
Copyright 2021-2024 - Megan Enriquez

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

Button Driver

  This driver can support buttons that have either a pull up resistor between the
button and the processor pin (i.e. the input is "High" / "1" when the button is
not pressed) and will be connected to ground when the button is pressed (i.e. 
the input is "Low" / "0" when the button is pressed), or a pull down resistor 
between the button and the processor pin (i.e. the input is "Low" / "0" when the 
button is not pressed) and will be connected to power when the button is pressed
(i.e. the input is "High" / "1" when the button is pressed).

  To select the pull up configuration, active_low=True.  To select the pull down
configuration, active_low=False.


Software API:

  Button(pin, sleep_time=0.1, active_low=True)
    - Provide pin that the button monitors
    - The sleep_time is the time between calls to the callback functions
      while the button is waiting in either the pressed or unpressed state
    - By default, the button is "active_low" (i.e. the button has a 
      pull up resistor between the button and the processor pin and 
      will be connected to ground when the button is pressed.  The 
      input is "High"/"1" when the button is not pressed, and the 
      input is "Low" / "0" when the button is pressed).  If false, 
      the button has the opposite polarity.
    
    wait_for_press()
      - Wait for the button to be pressed 
      - Function consumes time
        
    is_pressed()
      - Return a boolean value (i.e. True/False) on if button is pressed
      - Function consumes no time
    
    get_last_press_duration()
      - Return the duration the button was last pressed

    cleanup()
      - Clean up HW
      
    Callback Functions:
      These functions will be called at the various times during a button 
      press cycle.  There is also a corresponding function to get the value
      from each of these callback functions in case they return something.
    
      - set_pressed_callback(function)
        - Excuted every "sleep_time" while the button is pressed
      - set_unpressed_callback(function)
        - Excuted every "sleep_time" while the button is unpressed
      - set_on_press_callback(function)
        - Executed once when the button is pressed
      - set_on_release_callback(function)
        - Executed once when the button is released
      
      - get_pressed_callback_value()
      - get_unpressed_callback_value()
      - get_on_press_callback_value()
      - get_on_release_callback_value()      

"""
import time

import Adafruit_BBIO.GPIO as GPIO

# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

HIGH          = GPIO.HIGH
LOW           = GPIO.LOW

# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------

# None

# ------------------------------------------------------------------------
# Functions / Classes
# ------------------------------------------------------------------------
import Adafruit_BBIO.PWM as PWM
import time
LED = 'P2_3'
step = 10       # Step size
min =  0        # dimmest value
max =  100      # brightest value
brightness = min # Current brightness;
 
PWM.start(LED, brightness)

class Button():
    """ Button Class """
    pin                           = None
    
    unpressed_value               = None
    pressed_value                 = None
    
    sleep_time                    = None
    press_duration                = None

    pressed_callback              = None
    pressed_callback_value        = None
    unpressed_callback            = None
    unpressed_callback_value      = None
    on_press_callback             = None
    on_press_callback_value       = None
    on_release_callback           = None
    on_release_callback_value     = None
    
    
    def __init__(self, pin=None, sleep_time=0.1, active_low=True):
        """ Initialize variables and set up the button """
        if (pin == None):
            raise ValueError("Pin not provided for Button()")
        else:
            self.pin = pin
        
        # For pull up resistor configuration:    active_low = True
        # For pull down resistor configuration:  active_low = False
        if active_low:
            self.unpressed_value = HIGH
            self.pressed_value   = LOW
        else:
            self.unpressed_value = LOW
            self.pressed_value   = HIGH
        
        # Initialize Class Variables      
        self.sleep_time      = sleep_time
        self.press_duration  = 0.0        

        # All callback functions and values set to None if not used        
        
        # Initialize the hardware components        
        self._setup()
    
    # End def
    
    
    def _setup(self):
        """ Setup the hardware components. """
        # Initialize Button
        GPIO.setup(self.pin, GPIO.IN)

    # End def


    def is_pressed(self):
        """ Is the Button pressed?
        
           Returns:  True  - Button is pressed
                     False - Button is not pressed
        """
        return GPIO.input(self.pin) == self.pressed_value

    # End def


    def wait_for_press(self):
        """ Wait for the button to be pressed.  This function will 
           wait for the button to be pressed and released so there
           are no race conditions.
           
           Use the callback functions to peform actions while waiting
           for the button to be pressed or get values after the button
           is pressed.
        
           Arguments:  None
           Returns:    None
        """
        button_press_time = None
        
        # Wait for button press
        #   Execute the unpressed callback function based on the sleep time
        #
        while(GPIO.input(self.pin) == self.unpressed_value):
        
            if self.unpressed_callback is not None:
                self.unpressed_callback_value = self.unpressed_callback()
            
            time.sleep(self.sleep_time)
            
        # Record time
        button_press_time = time.time()
        
        # Executed the on press callback function
        if self.on_press_callback is not None:
            self.on_press_callback_value = self.on_press_callback()
        
        # Wait for button release
        #   Execute the pressed callback function based on the sleep time
        #
        while(GPIO.input(self.pin) == self.pressed_value):
        
            if self.pressed_callback is not None:
                self.pressed_callback_value = self.pressed_callback()
                
            time.sleep(self.sleep_time)
        
        # Record the press duration
        self.press_duration = time.time() - button_press_time

        # Executed the on release callback function
        if self.on_release_callback is not None:
            self.on_release_callback_value = self.on_release_callback()        
        
    # End def

    
    def get_last_press_duration(self):
        """ Return the last press duration """
        return self.press_duration
    
    # End def
    
    
    def cleanup(self):
        """ Clean up the button hardware. """
        # Nothing to do for GPIO
        pass
    
    # End def
    
    
    # -----------------------------------------------------
    # Callback Functions
    # -----------------------------------------------------

    def set_pressed_callback(self, function):
        """ Function excuted every "sleep_time" while the button is pressed """
        self.pressed_callback = function
    
    # End def

    def get_pressed_callback_value(self):
        """ Return value from pressed_callback function """
        return self.pressed_callback_value
    
    # End def
    
    def set_unpressed_callback(self, function):
        """ Function excuted every "sleep_time" while the button is unpressed """
        self.unpressed_callback = function
    
    # End def

    def get_unpressed_callback_value(self):
        """ Return value from unpressed_callback function """
        return self.unpressed_callback_value
    
    # End def

    def set_on_press_callback(self, function):
        """ Function excuted once when the button is pressed """
        self.on_press_callback = function
    
    # End def

    def get_on_press_callback_value(self):
        """ Return value from on_press_callback function """
        return self.on_press_callback_value
    
    # End def

    def set_on_release_callback(self, function):
        """ Function excuted once when the button is released """
        self.on_release_callback = function
    
    # End def

    def get_on_release_callback_value(self):
        """ Return value from on_release_callback function """
        return self.on_release_callback_value
    
    # End def    
    
# End class



# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':
    print("Button Test")
    
    # Create instantiation of the button
    button1 = Button("P2_2")
    button2 = Button("P2_4")
    
    # Create functions to test the callback functions
    
    starting_timer = 0
    start_LED = 0

    while(1):
        if button2.is_pressed():
            starting_timer = not starting_timer
            print(starting_timer)
            time.sleep(0.25)
            
        if button1.is_pressed():
            print("button1 pressed")
            start_LED = 1;
            PWM.set_duty_cycle(LED, 100)
            time.sleep(0.25)
            PWM.set_duty_cycle(LED, brightness)
            brightness += step
            if(brightness >= max or brightness <= min):
                step = -1 * step
                time.sleep(0.1)
            button1.wait_for_press()
            print("    Button pressed for {0} seconds. ".format(button1.get_last_press_duration()))
            time.sleep(0.25)
            
        if not button1.is_pressed():
            print("button1 not pressed")
            start_LED = 0;
            PWM.set_duty_cycle(LED, 0)
            time.sleep(0.1)
        
 
    
    
    # def pressed():
    #     print("  Button pressed")
    # # End def
    
    # def unpressed():
    #     print("  Button not pressed")
    # # End def

    # def on_press():
    #     print("  On Button press")
    #     return 3
    # # End def

    # def on_release():
    #     print("  On Button release")
    #     return 4
    # # End def    

    # Use a Keyboard Interrupt (i.e. "Ctrl-C") to exit the test
    # try:
    #     # Check if the button is pressed
    #     print("Is the button pressed?")
    #     print("    {0}".format(button1.is_pressed()))

    #     print("Press and hold the button.")
    #     time.sleep(4)
        
    #     # Check if the button is pressed
    #     print("Is the button pressed?")
    #     print("    {0}".format(button1.is_pressed()))
        
    #     print("Release the button.")
    #     time.sleep(4)
        
    #     print("Waiting for button press ...")
    #     button1.wait_for_press()
    #     print("    Button pressed for {0} seconds. ".format(button1.get_last_press_duration()))
        
    #     print("Setting callback functions ... ")
    #     button1.set_pressed_callback(pressed)
    #     button1.set_unpressed_callback(unpressed)
    #     button1.set_on_press_callback(on_press)
    #     button1.set_on_release_callback(on_release)
        
    #     print("Waiting for button press with callback functions ...")
    #     value = button1.wait_for_press()
    #     print("    Button pressed for {0} seconds. ".format(button1.get_last_press_duration()))
    #     print("    Button pressed callback return value    = {0} ".format(button1.get_pressed_callback_value()))
    #     print("    Button unpressed callback return value  = {0} ".format(button1.get_unpressed_callback_value()))
    #     print("    Button on press callback return value   = {0} ".format(button1.get_on_press_callback_value()))
    #     print("    Button on release callback return value = {0} ".format(button1.get_on_release_callback_value()))        
        
    # except KeyboardInterrupt:
    #     pass

    print("Test Complete")
