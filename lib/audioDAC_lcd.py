import RPi.GPIO as GPIO
import shutil
from ST7789 import ST7789
from PIL import Image, ImageDraw, ImageFont

# Variables for display/screen
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
    draw.rectangle([(15,210),(15,215)],fill = BLACK)
    draw.rectangle((15, 210,5+bar_width, 215), WHITE)
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
    elif( mode == 3 ):              # mode 3 - timelapse stills
        draw.text((210,5),"TLS ", fill = RED,font = Font5)
    elif( mode == 4 ):              # mode 4 - timelapse video
        draw.text((210,5),"TLV ", fill = RED,font = Font5)
    draw.text((80,5),str(x)+" / "+str(imagecount), fill = YELLOW,font = Font5)
    draw.rectangle([(15,210),(15,215)],fill = BLACK)
    draw.rectangle((15, 210,15+bar_width, 215), GRAY)
    st7789.display(new_image)

#############################################################################
# Functions to print specific menu options for camera
#############################################################################

def init_disp():
    image=Image.new("RGB",(240,240),color='black')
    draw = ImageDraw.Draw(image)
    draw.text((45,70),"PiCam", fill = GREEN,font = Font1)
    draw.text((75,130),"INFRA", fill = YELLOW,font = Font4)
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

def menu_display(header,menu_item,menu):
    item_number = menu % 10
    image=Image.new("RGB",(240,240),color='black')
    draw = ImageDraw.Draw(image)
################# Interface Buttons #########################
    draw.text((5,215),"↓", fill = RED,font = Font3)
    draw.text((85,215),"<", fill = RED,font = Font4)
    draw.text((145,215),">",fill = RED,font = Font4)
    draw.text((212,215),"↑", fill = RED,font = Font3)
#############################################################
    draw.text((0,5),header,fill = WHITE,font = Font3)
    count = 0
    for item in menu_item:
        if(item_number == (count+1)):
            draw.rectangle([(220,(37+(25*(count+1)))),(20,(37+(25*count)))],fill = GRAY)
            draw.text((25,(35+(25*count))),item,fill = GREEN,font = Font4)
        else:
            draw.text((25,(35+(25*count))),item,fill = WHITE,font = Font4)
        count += 1
    
    st7789.display(image)

#def camera_home(raw,bnw,mode,img,exposure,exp):
#    img= img.resize((240,180), resample=Image.BICUBIC)
def camera_home():
    raw=True
    bnw=True
    mode=1
    exposure = 0
    exp=False
    image=Image.new("RGB",(240,240),color='black')
#    image.paste(img,(0,30))
    draw = ImageDraw.Draw(image)
    if(exp):
        draw.text((100,5),exposureValue[exposure],fill = GREEN, font = Font5)
    else:
        draw.text((100,5),exposureValue[exposure],fill = RED, font = Font5)
    if( mode == 1 ):                # mode 1 - stills
        draw.text((210,5),"PIC", fill = RED,font = Font5)
    elif( mode == 2 ):              # mode 2 - bracketing
        draw.text((210,5),"BKT", fill = RED,font = Font5)
    elif( mode == 3 ):              # mode 2 - timelapse stills
        draw.text((210,5),"TLS", fill = RED,font = Font5)
    elif( mode == 4 ):              # mode 2 - timelapse video
        draw.text((210,5),"TLV", fill = RED,font = Font5)
    if(bnw):
        draw.text((5,5),"B & W", fill = WHITE,font = Font5)
    else:
        draw.text((5,5),"COLOR", fill = RED,font = Font5)
    if (raw):
        draw.text((60,5),"RAW", fill = GREEN,font = Font5)

    draw.text((5,215),"[•]", fill = RED,font = Font4)
    draw.text((85,215),"<", fill = RED,font = Font4)
    draw.text((145,215),">",fill = RED,font = Font4)
    draw.text((211,202),"—", fill = RED,font = Font3)
    draw.text((211,210),"—", fill = RED,font = Font3)
    draw.text((211,218),"—", fill = RED,font = Font3)
    st7789.display(image)

def menu_control(display_config,shoot_config,camera_config):
    menu = display_config.get("menu")
    if( menu >= 1 and menu <= 9):
        items=["Image Settings","Shooting Mode","System Menu","Power Options"]
        menu_display("Menu",items,menu)

    elif( menu >= 41 and menu <= 49 ):        # Power options
        items=["Reboot","Poweroff"]
        menu_display("Power options",items,menu)

