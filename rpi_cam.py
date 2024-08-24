#!/usr/bin/env python3

import os
import shutil
import time
import signal
import touchphat
import RPi.GPIO as GPIO

import lib.camera as camera
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

def display_sleep(brightness,sleep):
    global backlight
    if(sleep):
        for x in range (brightness,-1,-1):
            backlight.ChangeDutyCycle(x)
            time.sleep(0.01)
    else:
        for x in range (0,brightness+1,1):
            backlight.ChangeDutyCycle(x)
            time.sleep(0.01)

def init(display_config,shoot_config,camera_config):
    backlight.start(1)
    lcd.boot_disp("camera_logo.jpeg")
    camera.initialize_camera(camera_config)
    display_sleep(display_config["brightness"],False)

def end_program():
    lcd.boot_disp("camera_down_logo.jpeg")
    camera.stop_camera()
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit

def touch_input(input_value):
    global display_config,shoot_config,camera_config
    if(input_value == 1):                                                             # BACK key
        touchphat.set_led(input_value, display_config["status_led"])
        if(display_config["menu"] == -1):
            display_sleep(display_config["brightness"],False)
        display_config,shoot_config,camera_config = operation.back_button(display_config,shoot_config,camera_config)

    elif(input_value == 2):                                                           # Down key
        touchphat.set_led(input_value, display_config["status_led"])
        display_config,shoot_config,camera_config = operation.down_button(display_config,shoot_config,camera_config)

    elif(input_value == 3):                                                           # Left key being used as DECREMENT ( - )
        touchphat.set_led(input_value, display_config["status_led"])
        display_config,shoot_config,camera_config = operation.left_button(display_config,shoot_config,camera_config)
        if(display_config["menu"] == 41):
            backlight.ChangeDutyCycle(display_config["brightness"])

    elif(input_value == 4):                                                           # Right key being used as INCREMENT ( + )
        touchphat.set_led(input_value, display_config["status_led"])
        display_config,shoot_config,camera_config = operation.right_button(display_config,shoot_config,camera_config)
        if(display_config["menu"] == 41):
            backlight.ChangeDutyCycle(display_config["brightness"])

    elif(input_value == 5):                                                           # UP key
        touchphat.set_led(input_value, display_config["status_led"])
        display_config,shoot_config,camera_config = operation.up_button(display_config,shoot_config,camera_config)

    else:                                                                       # ENTER key
        touchphat.set_led(input_value, display_config["status_led"])
        if(display_config["menu"] == -1):
            display_sleep(display_config["brightness"],False)
        display_config,shoot_config,camera_config = operation.ok_shutter_button(display_config,shoot_config,camera_config)
        if(((display_config["menu"] > 40) and (display_config["menu"] < 50)) or ((display_config["menu"] > 4000) and (display_config["menu"] < 5000))):
            backlight.ChangeDutyCycle(display_config["brightness"])
        if(display_config["menu"] == -2):
            display_config["menu"] = -1
            display_sleep(display_config["brightness"],True)

# Code to get input from Pimoroni Touchphat 
# Based on the example code provided by pimoroni
# https://github.com/pimoroni/touch-phat/tree/master/examples
@touchphat.on_touch(['Back','A','B','C','D','Enter'])
def handle_touch(event):
    touch_input(event.pad)

###############################################################################################################
# main()
###############################################################################################################

def main():
    global display_config,shoot_config,camera_config
    display_config,shoot_config,camera_config = operation.load_settings("auto_saved")
    init(display_config,shoot_config,camera_config)
    
    while(True):
        try:
            lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))
            signal.pause()  
        except KeyboardInterrupt:
            print("Keyboard interrupt detected")
            display_config["menu"] == 0
            operation.save_settings(display_config,shoot_config,camera_config,"auto_saved")
            print("Current settings saved")
            end_program()

if __name__ == '__main__':
    main()
