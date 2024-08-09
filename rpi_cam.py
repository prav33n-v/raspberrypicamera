#!/usr/bin/env python3

import signal
import touchphat
import RPi.GPIO as GPIO

#import lib.camera as camera
import lib.audioDAC_lcd as lcd
import lib.operations as ops

# Setup  Rpi.GPIO with "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)
# We must set the backlight pin up as an output first
GPIO.setup(13, GPIO.OUT)
# Set up our pin as a PWM output at 500Hz
backlight = GPIO.PWM(13, 500)

camera_config = {
    "image_height": 1600,
    "image_width": 1200,
    "exposure": 0,
    "bnw": True,
    "raw": True
}

shoot_config = {
    "shoot_mode": 1,
    "interval": 1,
    "image_count": 10,
    "bracketing_count": 5,
    "image_quality": 3,
    "storage_path": "/home/pi/Pictures"
}

display_config = {
    "brightness": 5,
    "menu": 0
}

# Exposure time OR Shutter Speed in microseconds
exposure_time=[0,625,800,1000,1250,1562,2000,2500,3125,4000,5000,6250,8000,10000,12500,16667,20000,25000,33333,40000,50000,66667,76923,100000,125000,166667,200000,250000,333333,400000,500000,625000,769231,1000000,1300000,1600000,2000000,2500000,3000000,4000000,5000000,6000000,8000000,10000000,13000000,15000000,20000000,25000000,30000000,60000000,90000000,120000000,150000000,180000000]
image_height=[1600,2048,2464,3008,3264,3888,4000,4656]
image_width=[1200,1536,1632,2000,2448,2592,2800,3496]

def blink(count):
    for x in range (1,count+1,1):
        for y in range (1,7,1):
            touchphat.set_led(y, True)
            touchphat.set_led(y, False)

def touch_input(input):
    if(input == 1):                 # BACK key on TouchPHAT
        touchphat.set_led(input, False)
        if(display_config["menu"] > 0 and display_config["menu"] < 9):
            display_config["menu"] = 0
            lcd.camera_home()
    elif(input == 2):               # 'A' Key on TouchPHAT being used as DOWN
        touchphat.set_led(input, False)
        if(display_config["menu"] >= 1 and display_config["menu"] <=9):
            display_config["menu"] = ops.down(display_config["menu"],1,4) 
            lcd.menu_control(display_config,shoot_config,camera_config)
    elif(input == 3):               # 'B' key on TouchPHAT being used as DECREMENT ( - )
        touchphat.set_led(input, False)
    elif(input == 4):               # 'C' key on TouchPHAT being used as INCREMENT ( + )
        touchphat.set_led(input, False)
    elif(input == 5):               # 'D' key on TouchPHAT being used as UP
        touchphat.set_led(input, False)
        if(display_config["menu"] == 0):
            display_config["menu"] = 1
        elif(display_config["menu"] >= 1 and display_config["menu"] <=9):
            display_config["menu"] = ops.up(display_config["menu"],1,4) 
        else:
            blink(10)
        lcd.menu_control(display_config,shoot_config,camera_config)
    else:                           # ENTER key on TouchPHAT used as ENTER
        touchphat.set_led(input, False)

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
    lcd.init_disp()
    blink(10)
    lcd.camera_home()
    signal.pause()

if __name__ == '__main__':
    main()
