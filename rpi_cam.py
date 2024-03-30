#!/usr/bin/env python3

import os
import time
import json
import shutil
import signal
import touchphat
import RPi.GPIO as GPIO
from PIL import Image,ImageFont

import lib.camera as camera
import lib.audioDAC_lcd as lcd
import lib.operations as ops

# We must set the backlight pin up as an output first
GPIO.setup(13, GPIO.OUT)
# Set up our pin as a PWM output at 500Hz
backlight = GPIO.PWM(13, 500)

# Define LCD display width, height
width = 240
height = 240

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)
# try changing 24 to 20 if your Y button doesn't work.
BUTTONS = [5, 6, 16, 24]
# These correspond to buttons A, B, X and Y respectively
LABELS = ['A', 'B', 'X', 'Y']
# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define all operation flag variables
bnw=False       # True / Flase
raw=False       # True / Flase
menu=0
brightness=5  # Range = 1 - 100
mode=1          # Value to select shooting mode Stills/Timelapse Stills/Timelapse Video
interval=1      # Interval between each shot for timelapse
imageCount=10   # Default number of shots for timelapse
imageQuality=4    # Value used to select output image resolution/size
exposure=0
# Exposure time OR Shutter Speed in microseconds
exposureTime=[0,625,800,1000,1250,1562,2000,2500,3125,4000,5000,6250,8000,10000,12500,16667,20000,25000,33333,40000,50000,66667,76923,100000,125000,166667,200000,250000,333333,400000,500000,625000,769231,1000000,1300000,1600000,2000000,2500000,3000000,4000000,5000000,6000000,8000000,10000000,13000000,15000000,20000000,25000000,30000000,60000000,90000000,120000000,150000000,180000000]
img_h=[1600,2048,2464,3008,3264,3888,4000,4656]
img_w=[1200,1536,1632,2000,2448,2592,2800,3496]
image=Image.new("RGB",(240,240),color='black')
quickSwitch=False
exp=False

# Define path for storing images
storagePath = "/mnt/usb/"

def loadSettings():
    global bnw,raw,brightness,interval,mode,imageCount,imageQuality
    dir="config"
    filename="config.json"
    configFile= os.path.join(os.getcwd(),dir,filename)
    with open(configFile,'r') as openfile:
        config = json.load(openfile)
    bnw,raw,mode,interval,imageCount,imageQuality,brightness,exposure=config['bnw'],config['raw'],config['mode'],config['interval'],config['imageCount'],config['imageQuality'],config['brightness'],config['exposure']
    # Start the PWM at 50% duty cycle
    backlight.start(brightness)

def saveSettings():
    global bnw,raw,brightness,interval,mode,imageCount,imageQuality
    settings = {
        "bnw":bnw,
        "raw":raw,
        "mode":mode,
        "interval":interval,
        "imageCount":imageCount,
        "imageQuality":imageQuality,
        "brightness":brightness,
        "exposure":exposure
    }
    dir="config"
    filename="config.json"
    configFile= os.path.join(os.getcwd(),dir,filename)
    with open(configFile,"w") as outfile:
        json.dump(settings, outfile)

def resetSettings():
    global bnw,raw,brightness,interval,mode,imageCount,imageQuality
    dir="config"
    filename="defaultConfig.json"
    configFile= os.path.join(os.getcwd(),dir,filename)
    with open(configFile,'r') as openfile:
        config = json.load(openfile)
    bnw,raw,mode,interval,imageCount,imageQuality,brightness,exposure=config['bnw'],config['raw'],config['mode'],config['interval'],config['imageCount'],config['imageQuality'],config['brightness'],config['exposure']
    saveSettings()
    # Start the PWM at 50% duty cycle
    backlight.start(brightness)

def preview():
    lcd.camera_home(raw,bnw,camera.shoot_preview(bnw),mode,exposure,exp)

def clickPic():
    global image_filename
    timestr = time.strftime("%Y%m%d-%H%M%S")
    if(os.path.exists(storagePath+"Stills/")):
        print("Writing in Stills folder")
    else:
        os.mkdir(storagePath+"Stills/")
    image_filename = storagePath + "Stills/img_" + str(timestr)
    camera.shoot(raw,bnw,image_filename)
    image=Image.open(image_filename+".jpg")
    lcd.camera_home(raw,bnw,image,mode,exposure,exp)

def timelapse(path):
    global mode
    os.mkdir(path)
    for x in range(imageCount):
        image_filename=path+"Timelapse_"+str(x)
        camera.shoot(raw,bnw,image_filename)
        time.sleep(interval)
        lcd.progress_bar(image_filename+".jpg",int(((x+1)/imageCount)*100),(x+1),imageCount,mode)
    image=Image.open(image_filename+".jpg")
    lcd.camera_home(raw,bnw,image,mode,exposure,exp)

def blink(count):
    for x in range (1,count+1,1):
        for y in range (1,7,1):
            touchphat.set_led(y, True)
            touchphat.set_led(y, False)

def display():
    global menu,raw,bnw,brightness,mode,interval,imageCount,imageQuality,exposure
    lcd.menuDisplay(raw,bnw,menu,mode,brightness,interval,imageCount,imageQuality,storagePath,exposure)

def touchInput(input):
    global menu,raw,bnw,brightness,mode,interval,imageCount,imageQuality,quickSwitch,exposure,exp
    if(input == 1):                 # BACK key on TouchPHAT
        touchphat.set_led(input, False)
        if(menu == 0):              # Do Nothing
            blink(1)
        elif(menu >= 1 and menu <= 9):    # Back from Power option to camera home
            menu=0
            preview()
        elif(menu >=11 and menu <=99 and quickSwitch):
            quickSwitch = False
            menu = 0
            preview()
        else:
            if(menu >= 11 and menu <= 19):
                menu=1
                camera.initialize_camera(img_h[imageQuality],img_w[imageQuality],exposureTime[exposure])
            elif(menu >= 21):
                menu= menu // 10
            else:
                blink(1)
            display()

    elif(input == 2):               # 'A' Key on TouchPHAT being used as DOWN
        touchphat.set_led(input, False)
        if (menu == 0):     # Show preview
            preview()
        else:
            if(menu >= 1 and menu <=9):
                menu = ops.down(menu,1,4)
            elif(menu >= 11 and menu <= 19):
                menu = ops.down(menu,11,14)
            elif(menu >= 21 and menu <= 29):
                menu = ops.down(menu,21,23)
            elif(menu >= 221 and menu <= 229):
                menu = ops.down(menu,221,222)
            elif(menu >= 231 and menu <= 239):
                menu = ops.down(menu,231,232)
            elif(menu >= 31 and menu <= 39):
                menu = ops.down(menu,31,33)
            elif(menu >= 321 and menu <= 329):
                menu = ops.down(menu,321,322)
            elif(menu >= 331 and menu <= 339):
                menu = ops.down(menu,331,332)
            elif(menu >= 41 and menu <= 42):
                menu = ops.down(menu,41,42)
            else:
                blink(1)
            display()

    elif(input == 3):               # 'B' key on TouchPHAT being used as DECREMENT ( - )
        touchphat.set_led(input, False)
        if(menu == 0 and exp == False):
            print("Feature to be added")
        elif (menu == 0 and exp == True):     # Adjust Exposure time OR Shutter speed
            if(exposure < 53):
                exposure = ops.increment(exposure,1)
            else:
                blink(1)
            preview()
        else:
            if( menu == 211 ):
                if(contrast > -100):
                    contrast = ops.decrement(contrast,5)
                else:
                    blink(3)
            elif(menu == 212):
                metering = ops.up(metering,0,1)
            elif(menu == 231 or menu == 221):
                if(interval > 1):
                    interval = ops.decrement(interval,1)
                else:
                    blink(3)
            elif(menu == 232 or menu == 222):
                if(imageCount > 10):
                    imageCount = ops.decrement(imageCount,10)
                else:
                    blink(3)
            elif(menu == 14):
                if(exposure < 53):
                    exposure = ops.increment(exposure,1)
                else:
                    blink(3)
            elif(menu == 31):
                if(brightness > 5):
                    brightness = ops.decrement(brightness,5)
                    backlight.ChangeDutyCycle(brightness)
                else:
                    blink(3)
            elif(menu == 13):
                if(imageQuality > 0):
                    imageQuality = ops.decrement(imageQuality,1)
                else:
                    blink(3)
            else:
                blink(1)
            display()

    elif(input == 4):               # 'C' key on TouchPHAT being used as INCREMENT ( + )
        touchphat.set_led(input, False)
        if (menu == 0 and exp == False):
            print("New feature to be added")
        elif (menu == 0 and exp == True):             # Adjust Exposure time OR Shutter speed
            if(exposure > 0):
                exposure = ops.decrement(exposure,1)
            else:
                blink(1)
            preview()
        else:
            if( menu == 211 ):
                if(contrast < 100):
                    contrast = ops.increment(contrast,5)
                else:
                    blink(3)
            elif(menu == 212):
                metering = ops.down(metering,0,1)
            elif(menu == 231 or menu == 221):
                interval = ops.increment(interval,1)
            elif(menu == 232 or menu == 222):
                imageCount = ops.increment(imageCount,10)
            elif(menu == 14):
                if(exposure > 0):
                    exposure = ops.decrement(exposure,1)
                else:
                    blink(3)
            elif(menu == 31):
                if(brightness < 100):
                    brightness = ops.increment(brightness,5)
                    backlight.ChangeDutyCycle(brightness)
                else:
                    blink(3)
            elif(menu == 13):
                if(imageQuality < 7 ):
                    imageQuality = ops.increment(imageQuality,1)
                else:
                    blink(3)
            else:
                blink(1)
            display()

    elif(input == 5):               # 'D' key on TouchPHAT being used as UP
        touchphat.set_led(input, False)
        if (menu == 0):     # Menu selected
            menu=1
        elif(menu >= 1 and menu <=9):
            menu = ops.up(menu,1,4)
        elif(menu >= 11 and menu <= 19):
            menu = ops.up(menu,11,14)
        elif(menu >= 21 and menu <= 29):
            menu = ops.up(menu,21,23)
        elif(menu >= 221 and menu <= 229):
            menu = ops.up(menu,221,222)
        elif(menu >= 231 and menu <= 239):
            menu = ops.up(menu,231,232)
        elif(menu >= 31 and menu <= 39):
            menu = ops.up(menu,31,33)
        elif(menu >= 321 and menu <= 329):
            menu = ops.up(menu,321,322)
        elif(menu >= 331 and menu <= 339):
            menu = ops.up(menu,331,332)
        elif(menu >= 41 and menu <= 42):
            menu = ops.up(menu,41,42)
        else:
            blink(1)
        display()
    else:                           # ENTER key on TouchPHAT used as ENTER
        touchphat.set_led(input, False)
        if (menu == 0):     # Capture
            if(mode == 1):  # Single shot
                clickPic()
            elif(mode==2):  # Start Timelapse Stills capture
                timestr = time.strftime("%Y%m%d-%H%M%S")
                if(os.path.exists(storagePath+"Timelapse/")):
                    print("Writing in Timelapse folder'")
                else:
                    os.mkdir(storagePath+"Timelapse/")
                path = storagePath + "Timelapse/TLS_" + str(timestr)+"/"
                timelapse(path)
            elif(mode==3):
                timestr = time.strftime("%Y%m%d-%H%M%S")
                if(os.path.exists(storagePath+"Timelapse_Video/")):
                    print("Writing in Timelapse_Video folder'")
                else:
                    os.mkdir(storagePath+"Timelapse_Video/")
                path = storagePath + "Timelapse_Video/TLV_" + str(timestr)+"/"
                timelapse(path)
        else:
            if(menu == 1):
                menu = 11
            elif(menu == 11):    # Toggle between Grayscale and Color
                bnw = not bnw
            elif(menu == 12):    # Toggle output file type between JPG and RAW+JPG
                raw = not raw
            elif(menu == 2):     # Shooting menu selected
                menu = 21
            elif(menu == 21 ):   # Single shot mode selected
                mode = 1
            elif(menu == 22):    # Timelapse Stills mode selected open submenu
                menu = 221
                mode = 2
            elif(menu == 23):    # Timelapse Video mode selected open submenu
                menu = 231
                mode = 3
            elif(menu == 3):     # System menu selected
                menu = 31
            elif(menu == 32):    # Storage space menu selected
                menu = 321
            elif(menu == 322):   # Format Data selected
                menu = 3222
            elif(menu == 3222):  # Delete all data from storage folder
                targetDir=["Stills","Timelapse","Timelapse_Video"]
                for x in targetDir:
                    path=os.path.join(storagePath,x)
                    shutil.rmtree(path, ignore_errors=True)
                menu = 322
            elif(menu == 33):    # User settings menu selected
                menu = 331
            elif(menu == 331):   # Save user settings selected
                menu = 3311
            elif(menu == 3311):  # Save user settings confirmed
                saveSettings()
                menu = 331
            elif(menu == 332):   # Reset Settings selected
                menu = 3321
            elif(menu == 3321):  # Reset Settings to default
                resetSettings()
                menu = 332
            elif(menu == 4):
                menu = 41
            elif(menu == 41):
                menu = 0
                lcd.reboot_disp()
                saveSettings()
                os.system("sudo reboot")
            elif(menu == 42):
                menu = 0
                lcd.poweroff_disp()
                saveSettings()
                os.system("sudo poweroff")
            else:
                blink(1)
            display()

# Code to get input from Pimoroni Touchphat 
# Based on the example code provided by pimoroni
# https://github.com/pimoroni/touch-phat/tree/master/examples
@touchphat.on_touch(['Back','A','B','C','D','Enter'])
def handle_touch(event):
    touchInput(event.pad)

def button_input(pin):
    global bnw,raw,menu,quickSwitch,exp,img_h,img_w,imageQuality,exposureTime,exposure
    label = LABELS[BUTTONS.index(pin)]
    if(label == 'A'):     # Grayscale/Color quick switch
        if(menu == 0):
            bnw = not bnw
            preview()
    elif(label == 'B'):   # RAW file output quick switch
        if(menu == 0):
            raw = not raw
            preview()
    elif(label == 'X'):   # Not defined any function yet
        if(menu == 0):
            menu = 21
            quickSwitch=True
            display()
    else:                 # Jump to preview from any menu page
        if(menu != 0):
            menu = 0
            quickSwitch=False
            preview()
        else:
            exp = not exp
            camera.initialize_camera(img_h[imageQuality],img_w[imageQuality],exposureTime[exposure])
            preview()

# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 200ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, button_input, bouncetime=500)

###############################################################################################################
# main()
###############################################################################################################

def main():
    loadSettings()
    camera.initialize_camera(img_h[imageQuality],img_w[imageQuality],exposureTime[exposure])
    lcd.init_disp()
    preview()
    signal.pause()

if __name__ == '__main__':
    main()

