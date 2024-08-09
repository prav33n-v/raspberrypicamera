#!/usr/bin/env python3

import os
import shutil

import signal
import touchphat
import RPi.GPIO as GPIO

#import lib.camera as camera
import lib.audioDAC_lcd as lcd
import lib.operations as ops

# Setup RPI.GPIO with "BCM" numbering scheme
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
    "brightness": 40,
    "menu": 0,
    "left_right": False
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

def load_settings():
    print("Load settings logic yet to implemented !!")
def save_settings():
    print("Save settings logic yet to implemented !!")
def reset_settings():
    print("Reset settings logic yet to implemented !!")

def touch_input(input):
    if(input == 1):                 # BACK key on TouchPHAT
        touchphat.set_led(input, False)
        if(display_config["menu"] > 0 and display_config["menu"] < 9):          # Back from main menu page to home screen
            display_config["menu"] = 0
        elif(display_config["menu"] > 10 and display_config["menu"] < 19):      # Back from image settings page to main menu page
            display_config["menu"] = 1
            display_config["left_right"] = False
        elif(display_config["menu"] > 20 and display_config["menu"] < 29):      # Back from shooting mode page to main menu page
            display_config["menu"] = 2
        elif(display_config["menu"] >= 221 and display_config["menu"] <=229):   # Back from bracketing mode submenu to shooting mode page
            display_config["menu"] = 22 
            display_config["left_right"] = False
        elif(display_config["menu"] >= 231 and display_config["menu"] <=239):   # Back from timelapse photo mode submenu to shooting mode page
            display_config["menu"] = 23
            display_config["left_right"] = False
        elif(display_config["menu"] >= 241 and display_config["menu"] <=249):   # Back from timelapse photo mode submenu to shooting mode page
            display_config["menu"] = 24
            display_config["left_right"] = False
        elif(display_config["menu"] > 30 and display_config["menu"] < 39):      # Back from system menu page to main menu page
            display_config["menu"] = 3
            display_config["left_right"] = False
        elif(display_config["menu"] == 3333 or display_config["menu"] == 333):  # Back from wiping data of system menu page
            display_config["menu"] = 3
        elif(display_config["menu"] == 3444 or display_config["menu"] == 344):  # Back from save setting of system menu page
            display_config["menu"] = 3
        elif(display_config["menu"] == 3555 or display_config["menu"] == 355):  # Back from reset setting of system menu page
            display_config["menu"] = 3
        elif(display_config["menu"] > 40 and display_config["menu"] < 49):      # Back from power options page to main menu page
            display_config["menu"] = 4
        else:
            blink(10)
        if(display_config["menu"] == 0):
            lcd.camera_home(display_config,shoot_config,camera_config)
        else:
            lcd.menu_control(display_config,shoot_config,camera_config)

    elif(input == 2):               # 'A' Key on TouchPHAT being used as DOWN
        touchphat.set_led(input, False)
        if(display_config["menu"] >= 1 and display_config["menu"] <=9):         # Main menu page
            display_config["menu"] = ops.down(display_config["menu"],1,4) 
        elif(display_config["menu"] >= 11 and display_config["menu"] <=19):     # Image settings page
            display_config["menu"] = ops.down(display_config["menu"],11,16) 
        elif(display_config["menu"] >= 21 and display_config["menu"] <=29):     # Shooting mode page
            display_config["menu"] = ops.down(display_config["menu"],21,24) 
            shoot_config["shoot_mode"] = display_config["menu"] % 10
        elif(display_config["menu"] >= 221 and display_config["menu"] <=229):   # Bracketing submenu
            display_config["menu"] = ops.down(display_config["menu"],223,224) 
        elif(display_config["menu"] >= 231 and display_config["menu"] <=239):   # Timelapse photo submenu
            display_config["menu"] = ops.down(display_config["menu"],234,236) 
        elif(display_config["menu"] >= 241 and display_config["menu"] <=249):   # Timelapse video submenu
            display_config["menu"] = ops.down(display_config["menu"],245,247) 
        elif(display_config["menu"] >= 31 and display_config["menu"] <=39):     # System menu page
            display_config["menu"] = ops.down(display_config["menu"],31,35) 
            if(display_config["menu"] == 31):
                display_config["left_right"] = True
            else:
                display_config["left_right"] = False
        elif(display_config["menu"] == 3333 or display_config["menu"] == 333):  # After wiping data from system menu page
            display_config["menu"] = 34
        elif(display_config["menu"] == 3444 or display_config["menu"] == 344):  # After save settings from system menu page
            display_config["menu"] = 35
        elif(display_config["menu"] == 3555 or display_config["menu"] == 355):  # After reset settings from system menu page
            display_config["menu"] = 31
        elif(display_config["menu"] >= 41 and display_config["menu"] <=49):     # Power options page
            display_config["menu"] = ops.down(display_config["menu"],41,42) 
        else:
            blink(10)
        lcd.menu_control(display_config,shoot_config,camera_config)

    elif(input == 3):               # 'B' key on TouchPHAT being used as DECREMENT ( - )
        touchphat.set_led(input, False)
        if(display_config["menu"] == 31):                                       # Brightness decrease
            if(display_config["brightness"] > 5):
                display_config["brightness"] = ops.decrement(display_config["brightness"],5)
                backlight.ChangeDutyCycle(display_config["brightness"])
            else:
                blink(3)
        elif(display_config["menu"] == 14):                                     # Toggle bnw
            camera_config["bnw"] = not camera_config["bnw"]
        elif(display_config["menu"] == 15):                                     # Toggle raw
            camera_config["raw"] = not camera_config["raw"]
        lcd.menu_control(display_config,shoot_config,camera_config)

    elif(input == 4):               # 'C' key on TouchPHAT being used as INCREMENT ( + )
        touchphat.set_led(input, False)
        if(display_config["menu"] == 31):
            if(display_config["brightness"] < 100):
                display_config["brightness"] = ops.increment(display_config["brightness"],5)
                backlight.ChangeDutyCycle(display_config["brightness"])
            else:
                blink(3)
        elif(display_config["menu"] == 14):                                     # Toggle bnw
            camera_config["bnw"] = not camera_config["bnw"]
        elif(display_config["menu"] == 15):                                     # Toggle raw
            camera_config["raw"] = not camera_config["raw"]
        lcd.menu_control(display_config,shoot_config,camera_config)

    elif(input == 5):               # 'D' key on TouchPHAT being used as UP
        touchphat.set_led(input, False)
        if(display_config["menu"] == 0):
            display_config["menu"] = 1
        elif(display_config["menu"] >= 1 and display_config["menu"] <=9):       # Main menu page
            display_config["menu"] = ops.up(display_config["menu"],1,4) 
        elif(display_config["menu"] >= 11 and display_config["menu"] <=19):     # Image settings page
            display_config["menu"] = ops.up(display_config["menu"],11,16) 
        elif(display_config["menu"] >= 21 and display_config["menu"] <=29):     # Shooting mode page
            display_config["menu"] = ops.up(display_config["menu"],21,24) 
            shoot_config["shoot_mode"] = display_config["menu"] % 10
        elif(display_config["menu"] >= 221 and display_config["menu"] <=229):   # Bracketing mode page
            display_config["menu"] = ops.up(display_config["menu"],223,224) 
        elif(display_config["menu"] >= 231 and display_config["menu"] <=239):   # Timelapse photo submenu
            display_config["menu"] = ops.up(display_config["menu"],234,236) 
        elif(display_config["menu"] >= 241 and display_config["menu"] <=249):   # Timelapse video submenu
            display_config["menu"] = ops.up(display_config["menu"],245,247) 
        elif(display_config["menu"] >= 31 and display_config["menu"] <=39):     # System menu page
            display_config["menu"] = ops.up(display_config["menu"],31,35) 
            if(display_config["menu"] == 31):
                display_config["left_right"] = True
            else:
                display_config["left_right"] = False
        elif(display_config["menu"] == 3333 or display_config["menu"] == 333):  # Move up from wipe data option of system menu page
            display_config["menu"] = 32
        elif(display_config["menu"] == 3444 or display_config["menu"] == 344):  # Move up from save setting option of system menu page
            display_config["menu"] = 33
        elif(display_config["menu"] == 3555 or display_config["menu"] == 355):  # Move up from reset setting option of system menu page
            display_config["menu"] = 34
        elif(display_config["menu"] >= 41 and display_config["menu"] <=49):     # Power options page navigation
            display_config["menu"] = ops.up(display_config["menu"],41,42) 
        else:
            blink(10)
        lcd.menu_control(display_config,shoot_config,camera_config)

    else:                           # ENTER key on TouchPHAT used as ENTER
        touchphat.set_led(input, False)
        if(display_config["menu"] == 1):                                        # Select image settings from main menu page
            display_config["menu"] = 11
            display_config["left_right"] = True
        elif(display_config["menu"] == 2):                                      # Select shooting mode from main menu page
            if(shoot_config["shoot_mode"] == 1):
                display_config["menu"] = 21
            if(shoot_config["shoot_mode"] == 2):
                display_config["menu"] = 22
            if(shoot_config["shoot_mode"] == 3):
                display_config["menu"] = 23
            if(shoot_config["shoot_mode"] == 4):
                display_config["menu"] = 24 
        elif(display_config["menu"] == 22):                                     # Select bracketing mode from shooting mode page
            display_config["menu"] = 223
            display_config["left_right"] = True
            shoot_config["shoot_mode"]=2
        elif(display_config["menu"] == 23):                                     # Select timelapse photo mode from shooting mode page
            display_config["menu"] = 234
            display_config["left_right"] = True
            shoot_config["shoot_mode"]=3
        elif(display_config["menu"] == 24):                                     # Select timelapse photo mode from shooting mode page
            display_config["menu"] = 245
            display_config["left_right"] = True
            shoot_config["shoot_mode"]=4
        elif(display_config["menu"] == 3):                                      # Select system menu from main menu page
            display_config["menu"] = 31
            display_config["left_right"] = True
        elif(display_config["menu"] == 33):                                     # Select wipe data from system menu page
            display_config["menu"] = 333
        elif(display_config["menu"] == 333):                                    # Confirm wipe data from system menu page
            targetDir=["Photo","Bracketing","Timelapse_Photo","Timelapse_Video"]
            for x in targetDir:
                path=os.path.join(shoot_config["storage_path"],x)
                shutil.rmtree(path, ignore_errors=True)
            display_config["menu"] = 3333
        elif(display_config["menu"] == 3333):                                   # After wiping data from system menu page
            display_config["menu"] = 33
        elif(display_config["menu"] == 34):                                     # Select save settings from system menu page
            display_config["menu"] = 344
        elif(display_config["menu"] == 344):                                    # Confirm save settings from system menu page
            save_settings()
            display_config["menu"] = 3444
        elif(display_config["menu"] == 3444):                                   # After saving settings from system menu page
            display_config["menu"] = 34
        elif(display_config["menu"] == 35):                                     # Select reset settings from system menu page
            display_config["menu"] = 355
        elif(display_config["menu"] == 355):                                    # Confirm reset settings from system menu page
            reset_settings()
            display_config["menu"] = 3555
        elif(display_config["menu"] == 3555):                                   # After resetting settings from system menu page
            display_config["menu"] = 35
        elif(display_config["menu"] == 4):                                      # Select power options menu from main menu page
            display_config["menu"] = 41
        else:
            blink(10)
        lcd.menu_control(display_config,shoot_config,camera_config)

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
    backlight.start(display_config["brightness"])
    lcd.boot_disp("PiCam")
    blink(100)
    lcd.camera_home(display_config,shoot_config,camera_config)
    signal.pause()

if __name__ == '__main__':
    main()
