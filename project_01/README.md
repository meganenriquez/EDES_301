<h1>Touching Grass Timer</h1>
I created this project as a way for me to manage my stress while being productive

<p1>
Here are sub files I uese to combine in the my_project script -->

breathing.py: a test and create a way to control the LED
                into a pulse that inhales, holds, and exhales
          
button.py: test button functionality and initiate buttons

buzzer.py:  activates buzzer and is used as a reference to alert end of timer. 
            Plays different frequencies of noise
            
potentiometer.py: read values from interactive potentiometer (knob)

timer.py: convert given value into min + sec, then displays countdown 
            using Ht16K33 (hex display)

<h1> my_project.py: (main one) </h1>

  Beginning: (t = 0, start = 0)
  
    - get potentiometer1 value --> = t for set time
    
    - get potentiometer2 value for display brightness
    
  Middle: (t > 0, start = 1)
  
    - activated timer with button2
    
    - toggle yes/no to buzzer with button3

    - [SOON] hold button1 for breathing exercise
    
  End: (t = 0, start = 1)
  
    - display done
    
    - if buzz_on --> buzz
    
    - reset with button2
    
<p1> 
