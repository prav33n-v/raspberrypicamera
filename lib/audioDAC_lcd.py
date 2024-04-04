import RPi.GPIO as GPIO
import shutil
from ST7789 import ST7789
from PIL import Image, ImageDraw, ImageFont

# Variables for display/screen
brightness = 50
SPI_SPEED_MHZ = 80
exposureValue=["Auto","1/1600","1/1250","1/1000","1/800","1/640","1/500","1/400","1/320","1/250","1/200","1/160","1/125","1/100","1/80","1/60","1/50","1/40","1/30","1/25","1/20","1/15","1/13","1/10","1/8","1/6","1/5","1/4","1/3","1/2.5","1/2","1/1.6","1/1.3",'1"','1.3"','1.6"','2"','2.5"','3"','4"','5"','6"','8"','10"','13"','15"','20"','25"','30"','60"','90"','120"','150"','180"']

# Define colors
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
BLACK=(0,0,0)
GRAY=(120,120,120)
WHITE=(255,255,255)
YELLOW=(255,255,0)

# Path for fonts
# Fonts used are taken from the waveshare LCD interface example code
# URL : https://www.waveshare.com/w/upload/a/a8/LCD_Module_RPI_code.7z
Font1 = ImageFont.truetype("./font/Font01.ttf",50)
Font2 = ImageFont.truetype("./font/Font02.ttf",40)
Font3 = ImageFont.truetype("./font/Font02.ttf",30)
Font4 = ImageFont.truetype("./font/Font02.ttf",24)
Font5 = ImageFont.truetype("./font/Font02.ttf",19)
Font6 = ImageFont.truetype("./font/Font00.ttf",16)

st7789 = ST7789(
    rotation=90,  # Needed to display the right way up on Pirate Audio
    port=0,       # SPI port
    cs=1,         # SPI port Chip-select channel
    dc=9,         # BCM pin used for data/command
    backlight=13,
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

# LCD : Show image_file on screen
def show_image(image):
    basewidth = 240
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image= image.resize((basewidth,hsize), resample=Image.BICUBIC)
    new_image=Image.new("RGB",(240,240),color='black')
    new_image.paste(image,(0,0))
    st7789.display(new_image)

def draw_bar(image,value):
    draw = ImageDraw.Draw(image)
    # Draw a handy on-screen bar to show us the current brightness
    bar_width = int((210 / 100.0) * value)
    draw.rectangle([(15,225),(15,235)],fill = BLACK)
    draw.rectangle((15, 225,5+bar_width, 235), WHITE)
    # return the resulting image
    return image

# LCD : Write text on screen
def write_text(image,xpos,ypos,string,text_color,bg_color,str_font):
    draw = ImageDraw.Draw(image)
    draw.rectangle([(240,ypos+30),(xpos,ypos)],fill = bg_color)
    draw.text((xpos, ypos),string, fill = text_color,font = str_font)
    st7789.display(image)

def progress_bar(image_file,value,x,imagecount,mode):
    basewidth = 240
    image = Image.open(image_file)
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image= image.resize((basewidth,hsize), resample=Image.BICUBIC)
    new_image=Image.new("RGB",(240,240),color='black')
    new_image.paste(image,(0,30))
    draw = ImageDraw.Draw(new_image)
    # Draw a handy on-screen bar to show us the current brightness
    bar_width = int((210 / 100.0) * value)
    if( mode == 1 ):                # mode 1 - stills
        draw.text((210,5),"PIC", fill = RED,font = Font5)
    elif( mode == 2 ):              # mode 2 - timelapse stills
        draw.text((210,5),"TLS ", fill = RED,font = Font5)
    elif( mode == 3 ):              # mode 2 - timelapse video
        draw.text((210,5),"TLV ", fill = RED,font = Font5)
    draw.text((80,5),str(x)+" / "+str(imagecount), fill = YELLOW,font = Font5)
    draw.rectangle([(15,225),(15,235)],fill = BLACK)
    draw.rectangle((15, 225,15+bar_width, 235), GRAY)
    st7789.display(new_image)

#############################################################################
# Functions to print specific menu options for camera
#############################################################################

def init_disp():
    image=Image.new("RGB",(240,240),color='black')
    draw = ImageDraw.Draw(image)
    draw.text((45,70),"PiCam", fill = GREEN,font = Font1)
    draw.text((75,130),"INFRA", fill = WHITE,font = Font4)
    draw.text((130,130),"RED", fill = RED,font = Font4)
    st7789.display(image)

def reboot_disp():
    image=Image.new("RGB",(240,240),color='black')
    draw = ImageDraw.Draw(image)
    draw.text((45,100),"Reboot", fill = YELLOW,font = Font1)
    st7789.display(image)

def poweroff_disp():
    image=Image.new("RGB",(240,240),color='black')
    draw = ImageDraw.Draw(image)
    draw.text((15,100),"Poweroff", fill = RED,font = Font1)
    st7789.display(image)

#

def camera_home(raw,bnw,img,mode,exposure,exp):
    img= img.resize((240,180), resample=Image.BICUBIC)
    image=Image.new("RGB",(240,240),color='black')
    image.paste(img,(0,30))
    draw = ImageDraw.Draw(image)
    if(exp):
        draw.text((80,5),exposureValue[exposure],fill = GREEN, font = Font5)
    else:
        draw.text((80,5),exposureValue[exposure],fill = RED, font = Font5)
    if( mode == 1 ):                # mode 1 - stills
        draw.text((210,5),"PIC", fill = RED,font = Font5)
    elif( mode == 2 ):              # mode 2 - timelapse stills
        draw.text((210,5),"TLS ", fill = RED,font = Font5)
    elif( mode == 3 ):              # mode 2 - timelapse video
        draw.text((210,5),"TLV ", fill = RED,font = Font5)
    if(bnw):
        draw.text((5,5),"BnW", fill = RED,font = Font5)
    else:
        draw.text((5,5),"CLR", fill = RED,font = Font5)
    if (raw):
        draw.text((35,5)," RAW", fill = GREEN,font = Font5)

    draw.text((0,215),"↓", fill = GREEN,font = Font4)
    draw.text((20,215),"VIEW", fill = RED,font = Font5)
    draw.text((183,215),"MENU", fill = RED,font = Font5)
    draw.text((220,215),"↑", fill = GREEN,font = Font4)
    st7789.display(image)

def menuDisplay(raw,bnw,menu,mode,brightness,interval,imageCount,imageQuality,storagePath,exposure):
    image=Image.new("RGB",(240,240),color='black')
    draw = ImageDraw.Draw(image)
    if( menu >= 1 and menu <= 9):
        draw.text((0,0),"Menu", fill = WHITE,font = Font3)
        if (menu == 1):             # Image Settings
            draw.rectangle([(220,70),(20,40)],fill = GRAY)
        elif (menu == 2):           # Shooting Mode
            draw.rectangle([(220,100),(20,70)],fill = GRAY)
        elif (menu == 3):           # System Menu
            draw.rectangle([(220,130),(20,100)],fill = GRAY)
        elif (menu == 4):           # Power options
            draw.rectangle([(220,160),(20,130)],fill = GRAY)
        else:
            print("Something went wrong !")
        draw.text((25,40),"Image Settings",fill = WHITE,font = Font4)
        draw.text((25,70),"Shooting Mode",fill = WHITE,font = Font4)
        draw.text((25,100),"System Menu",fill = WHITE,font = Font4)
        draw.text((25,130),"Power Options",fill = WHITE,font = Font4)

    elif( menu >= 11 and menu <= 19):       # Image Settings menu
        draw.text((0,5),"Image Settings",fill = WHITE,font = Font3)
        if ( menu == 11):
            draw.rectangle([(220,70),(20,40)],fill = GRAY)
        elif(menu == 12):
            draw.rectangle([(220,100),(20,70)],fill = GRAY)
        elif(menu == 13):
            draw.rectangle([(220,130),(20,100)],fill = GRAY)
            draw.text((2,102),"-",fill = GREEN,font = Font4)
            draw.text((222,102),"+",fill = GREEN,font = Font4)
        elif(menu == 14):
            draw.rectangle([(220,160),(20,130)],fill = GRAY)
            draw.text((2,132),"-",fill = GREEN,font = Font4)
            draw.text((222,132),"+",fill = GREEN,font = Font4)
        else:
            print("ERROR !")

        if(bnw):
            draw.text((25,40),"BnW : Enabled",fill = WHITE,font = Font4)
        else:
            draw.text((25,40),"BnW : Disabled",fill = WHITE,font = Font4)
        if(raw):
            draw.text((25,70),"File : JPG + RAW",fill = WHITE,font = Font4)
        else:
            draw.text((25,70),"File : JPG",fill = WHITE,font = Font4)
        if(imageQuality == 0):
            draw.text((25,100),"Size : 1600 x 1200",fill = WHITE,font = Font4)
        elif(imageQuality == 1):
            draw.text((25,100),"Size : 2048 x 1536",fill = WHITE,font = Font4)
        elif(imageQuality == 2):
            draw.text((25,100),"Size : 2464 x 1632",fill = WHITE,font = Font4)
        elif(imageQuality == 3):
            draw.text((25,100),"Size : 3008 x 2000",fill = WHITE,font = Font4)
        elif(imageQuality == 4):
            draw.text((25,100),"Size : 3264 x 2448",fill = WHITE,font = Font4)
        elif(imageQuality == 5):
            draw.text((25,100),"Size : 3888 x 2592",fill = WHITE,font = Font4)
        elif(imageQuality == 6):
            draw.text((25,100),"Size : 4000 x 2800",fill = WHITE,font = Font4)
        else:
            draw.text((25,100),"Size : 4656 x 3496",fill = WHITE,font = Font4)
        draw.text((25,130),"Shutter : ",fill = WHITE,font = Font4)
        draw.text((100,130),exposureValue[exposure],fill = WHITE,font = Font4)

    elif( menu >= 21 and menu <= 29):       # Shooting Mode menu
        draw.text((0,5),"Shooting Mode",fill = WHITE,font = Font3)
        if ( menu == 21):
            draw.rectangle([(220,70),(20,40)],fill = GRAY)
        elif(menu == 22):
            draw.rectangle([(220,100),(20,70)],fill = GRAY)
        elif(menu == 23):
            draw.rectangle([(220,130),(20,100)],fill = GRAY)
        else:
            print("ERROR !")
        if ( mode == 1):                   # Single Shot
            draw.text((25,40),"Single shot",fill = GREEN,font = Font4)
            draw.text((25,70),"Timelapse Stills",fill = WHITE,font = Font4)
            draw.text((25,100),"Timelapse Video",fill = WHITE,font = Font4)
        elif(mode == 2):                   # Timelapse stills
            draw.text((25,40),"Single shot",fill = WHITE,font = Font4)
            draw.text((25,70),"Timelapse Stills",fill = GREEN,font = Font4)
            draw.text((25,100),"Timelapse Video",fill = WHITE,font = Font4)
        elif(mode == 3):                   # Timelapse Video
            draw.text((25,40),"Single shot",fill = WHITE,font = Font4)
            draw.text((25,70),"Timelapse Stills",fill = WHITE,font = Font4)
            draw.text((25,100),"Timelapse Video",fill = GREEN,font = Font4)
        else:
            print("ERROR !")

    elif( menu >= 221 and menu <= 229 ):    # Shooting mode : Timelapse stills submenu
        draw.text((0,5),"Mode Select",fill = WHITE,font = Font3)
        draw.text((25,40),"Single shot",fill = WHITE,font = Font4)
        draw.text((25,70),"Timelapse Stills",fill = GREEN,font = Font4)
        draw.text((25,100),"Timelapse Video",fill = WHITE,font = Font4)
        if ( menu == 221):
            draw.rectangle([(220,160),(20,130)],fill = GRAY)
            draw.text((2,132),"-",fill = GREEN,font = Font4)
            draw.text((222,132),"+",fill = GREEN,font = Font4)
        elif(menu == 222):
            draw.rectangle([(220,190),(20,160)],fill = GRAY)
            draw.text((2,162),"-",fill = GREEN,font = Font4)
            draw.text((222,162),"+",fill = GREEN,font = Font4)
        else:
            print("ERROR !")
        draw.text((25,130),"Interval(sec)",fill = YELLOW,font = Font4)
        draw.text((25,160),"No. of shots",fill = YELLOW,font = Font4)
        draw.text((140,130),"= "+str(interval),fill = YELLOW,font = Font4)
        draw.text((140,160),"= "+str(imageCount),fill = YELLOW,font = Font4)


    elif( menu >= 231 and menu <= 239 ):    # Shooting mode : Timelapse video submenu
        draw.text((0,5),"Mode Select",fill = WHITE,font = Font3)
        draw.text((25,40),"Single shot",fill = WHITE,font = Font4)
        draw.text((25,70),"Timelapse Stills",fill = WHITE,font = Font4)
        draw.text((25,100),"Timelapse Video",fill = GREEN,font = Font4)
        if ( menu == 231):
            draw.rectangle([(220,160),(20,130)],fill = GRAY)
            draw.text((2,132),"-",fill = GREEN,font = Font4)
            draw.text((222,132),"+",fill = GREEN,font = Font4)
        elif(menu == 232):
            draw.rectangle([(220,190),(20,160)],fill = GRAY)
            draw.text((2,162),"-",fill = GREEN,font = Font4)
            draw.text((222,162),"+",fill = GREEN,font = Font4)
        else:
            print("ERROR !")
        draw.text((25,130),"Interval(sec)",fill = YELLOW,font = Font4)
        draw.text((25,160),"No. of shots ",fill = YELLOW,font = Font4)
        draw.text((140,130),"= "+str(interval),fill = YELLOW,font = Font4)
        draw.text((140,160),"= "+str(imageCount),fill = YELLOW,font = Font4)

    elif( menu >= 31 and menu <= 39 ):      # System Settings
        draw.text((0,5),"System Menu",fill = WHITE,font = Font3)
        if(menu == 31):
            draw.rectangle([(220,70),(20,40)],fill = GRAY)
            draw.text((2,42),"-",fill = GREEN,font = Font4)
            draw.text((222,42),"+",fill = GREEN,font = Font4)
            draw_bar(image,brightness)
        elif(menu == 32):
            draw.rectangle([(220,100),(20,70)],fill = GRAY)
        elif(menu == 33):
            draw.rectangle([(220,130),(20,100)],fill = GRAY)
        draw.text((25,40),"Display Brightness",fill = WHITE,font = Font4)
        draw.text((25,70),"Storage Space",fill = WHITE,font = Font4)
        draw.text((25,100),"User Settings",fill = WHITE,font = Font4)

    elif( menu >= 321 and menu <= 329 ):      # Storage Submenu
        draw.text((0,5),"System Menu",fill = WHITE,font = Font3)
        if(menu == 321):
            draw.rectangle([(220,160),(20,130)],fill = GRAY)
            memory=shutil.disk_usage(storagePath)
            usage=int((memory[1]/memory[0])*100)
            used=(memory[1]/1024)
            total=(memory[0]/1024)/1024

            if(used > 0 and used < 1024):
                value = str(round(used,2)) + " KB / " + str(round((total/1024),2)) + " GB"
            elif(used >= 1024 and used < 1048576): # and used < 1073741824):
                value = str(round((used/1024),2)) + " MB / " + str(round((total/1024),2)) + " GB"
            else:
                value = str(round(((used/1024)/1024),2)) + " GB / " + str(round((total/1024),2)) + " GB"

            if(usage < 50):
                COLOR = GREEN
            elif(usage >= 50 and usage <=75):
                COLOR = YELLOW
            else:
                COLOR = RED
            draw.text((25,190),value,fill = COLOR,font = Font4)
            draw_bar(image,usage)
        elif(menu == 322):
            draw.rectangle([(220,190),(20,160)],fill = GRAY)
        draw.text((25,40),"Display Brightness",fill = WHITE,font = Font4)
        draw.text((25,70),"Storage Space",fill = WHITE,font = Font4)
        draw.text((25,100),"User Settings",fill = WHITE,font = Font4)
        draw.text((25,130),"Memory Used",fill = YELLOW,font = Font4)
        draw.text((25,160),"Format data",fill = YELLOW,font = Font4)

    elif( menu == 3222 ):                     # Data Format Confirmation
        draw.text((0,5),"System Menu",fill = WHITE,font = Font3)
        draw.rectangle([(220,190),(20,160)],fill = GRAY)
        draw.text((25,40),"Display Brightness",fill = WHITE,font = Font4)
        draw.text((25,70),"Storage Space",fill = WHITE,font = Font4)
        draw.text((25,100),"User Settings",fill = WHITE,font = Font4)
        draw.text((25,130),"Memory Used ",fill = YELLOW,font = Font4)
        draw.text((25,160),"Format data ???",fill = RED,font = Font4)

    elif( menu >= 331 and menu <= 339 ):      # User Settings Submenu
        draw.text((0,5),"System Menu",fill = WHITE,font = Font3)
        if(menu == 331):
            draw.rectangle([(220,160),(20,130)],fill = GRAY)
        elif(menu == 332):
            draw.rectangle([(220,190),(20,160)],fill = GRAY)
        draw.text((25,40),"Display Brightness",fill = WHITE,font = Font4)
        draw.text((25,70),"Storage Space",fill = WHITE,font = Font4)
        draw.text((25,100),"User Settings",fill = WHITE,font = Font4)
        draw.text((25,130),"Save current settings",fill = YELLOW,font = Font4)
        draw.text((25,160),"Reset settings",fill = YELLOW,font = Font4)

    elif( menu == 3311 ):                     # Save User Settings Confirmation
        draw.text((0,5),"System Menu",fill = WHITE,font = Font3)
        draw.rectangle([(220,160),(20,130)],fill = GRAY)
        draw.text((25,40),"Display Brightness",fill = WHITE,font = Font4)
        draw.text((25,70),"Storage Space",fill = WHITE,font = Font4)
        draw.text((25,100),"User Settings",fill = WHITE,font = Font4)
        draw.text((25,130),"Save current settings ?",fill = RED,font = Font4)
        draw.text((25,160),"Reset settings",fill = YELLOW,font = Font4)

    elif( menu == 3321 ):                     # Reset User Settings Confirmation
        draw.text((0,5),"System Menu",fill = WHITE,font = Font3)
        draw.rectangle([(220,190),(20,160)],fill = GRAY)
        draw.text((25,40),"Display Brightness",fill = WHITE,font = Font4)
        draw.text((25,70),"Storage Space",fill = WHITE,font = Font4)
        draw.text((25,100),"User Settings",fill = WHITE,font = Font4)
        draw.text((25,130),"Save current settings",fill = YELLOW,font = Font4)
        draw.text((25,160),"Reset settings ???",fill = RED,font = Font4)

    elif( menu >= 41 and menu <= 49 ):        # Power options
        draw.text((0,0),"Power options", fill = WHITE,font = Font3)
        if(menu == 41 ):
            draw.rectangle([(220,70),(20,40)],fill = GRAY)
        elif(menu == 42):
            draw.rectangle([(220,100),(20,70)],fill = GRAY)
        draw.text((25,40),"Reboot", fill = WHITE,font = Font4)
        draw.text((25,70),"Poweroff", fill = WHITE,font = Font4)

    st7789.display(image)
