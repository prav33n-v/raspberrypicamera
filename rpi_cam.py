#!/usr/bin/env python3

import os
import shutil

import signal
import touchphat
import RPi.GPIO as GPIO

#import lib.camera as camera
import lib.audioDAC_lcd as lcd
import lib.operations as operation

GPIO.setwarnings(False)
# Setup RPI.GPIO with "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)
# We must set the backlight pin up as an output first
GPIO.setup(13, GPIO.OUT)
# Set up our pin as a PWM output at 500Hz
backlight = GPIO.PWM(13, 500)

# Exposure time OR Shutter Speed in microseconds
exposure_time=[0,625,800,1000,1250,1562,2000,2500,3125,4000,5000,6250,8000,10000,12500,16667,20000,25000,33333,40000,50000,66667,76923,100000,125000,166667,200000,250000,333333,400000,500000,625000,769231,1000000,1300000,1600000,2000000,2500000,3000000,4000000,5000000,6000000,8000000,10000000,13000000,15000000,20000000,25000000,30000000,60000000]
image_height=[1600,2048,2464,3008,3264,3888,4000,4656]
image_width=[1200,1536,1632,2000,2448,2592,2800,3496]

def blink(count):
    for x in range (1,count+1,1):
        for y in range (1,7,1):
            touchphat.set_led(y, True)
            touchphat.set_led(y, False)

#def menu_key_input(display_config,shoot_config,camera_config):
#    global display_config,shoot_config,camera_config
#    print("Menu Key function to br developed")

def touch_input(input):
    global display_config,shoot_config,camera_config
    if(input == 1):                                                             # BACK key
        touchphat.set_led(input, False)
        display_config,shoot_config,camera_config = operation.back_button(display_config,shoot_config,camera_config)

    elif(input == 2):                                                           # Down key
        touchphat.set_led(input, False)
        display_config,shoot_config,camera_config = operation.down_button(display_config,shoot_config,camera_config)

    elif(input == 3):                                                           # Left key being used as DECREMENT ( - )
        touchphat.set_led(input, False)
        display_config,shoot_config,camera_config = operation.left_button(display_config,shoot_config,camera_config)
        if(display_config["menu"] == 41):
            backlight.ChangeDutyCycle(display_config["brightness"])

    elif(input == 4):                                                           # Right key being used as INCREMENT ( + )
        touchphat.set_led(input, False)
        display_config,shoot_config,camera_config = operation.right_button(display_config,shoot_config,camera_config)
        if(display_config["menu"] == 41):
            backlight.ChangeDutyCycle(display_config["brightness"])

    elif(input == 5):                                                           # UP key
        touchphat.set_led(input, False)
        display_config,shoot_config,camera_config = operation.up_button(display_config,shoot_config,camera_config)

    else:                                                                       # ENTER key
        touchphat.set_led(input, False)
        display_config,shoot_config,camera_config = operation.ok_shutter_button(display_config,shoot_config,camera_config)
        if(((display_config["menu"] > 40) and (display_config["menu"] < 50)) or ((display_config["menu"] > 4000) and (display_config["menu"] < 5000))):
            backlight.ChangeDutyCycle(display_config["brightness"])

# Code to get input from Pimoroni Touchphat 
# Based on the example code provided by pimoroni
# https://github.com/pimoroni/touch-phat/tree/master/examples
@touchphat.on_touch(['Back','A','B','C','D','Enter'])
def handle_touch(event):
    touch_input(event.pad)

def init():
    backlight.start(display_config["brightness"])
    lcd.boot_disp("camera_logo.jpeg")
    blink(10)

def end_program():
    lcd.boot_disp("camera_down_logo.jpeg")
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit
###############################################################################################################
# main()
###############################################################################################################

def main():
    global display_config,shoot_config,camera_config
    display_config,shoot_config,camera_config = operation.load_settings("auto_saved")
#    operation.save_settings(display_config,shoot_config,camera_config,"auto_saved")
    
    try:
        init()
        lcd.camera_home(display_config,shoot_config,camera_config)
        signal.pause()  
    except KeyboardInterrupt:
        print("Keyboard interrupt detected")
        end_program()

if __name__ == '__main__':
    main()
