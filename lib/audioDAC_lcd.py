import RPi.GPIO as GPIO
import os
import shutil
import time
from ST7789 import ST7789
from PIL import Image, ImageDraw, ImageFont

# Variables for display/screen
brightness = 50
SPI_SPEED_MHZ = 80
exposure_time=["Auto","1/1600","1/1250","1/1000","1/800","1/640","1/500","1/400","1/320","1/250","1/200","1/160","1/125","1/100","1/80","1/60","1/50","1/40","1/30","1/25","1/20","1/15","1/13","1/10","1/8","1/6","1/5","1/4","1/3","1/2.5","1/2","1/1.6","1/1.3",'1"','1.3"','1.6"','2"','2.5"','3"','4"','5"','6"','8"','10"','13"','15"','20"','25"','30"','60"']

image_h=[1600,2048,2464,3008,3264,3888,4000,4656]
image_w=[1200,1536,1632,2000,2448,2592,2800,3496]

# Define colors
RED=(255,0,0)
GREEN=(0,255,0)
BLACK=(0,0,0)
GRAY=(120,120,120)
WHITE=(255,255,255)
YELLOW=(255,255,0)
MENU_SELECT=(200,200,200)
MENU_TEXT=(10,200,200)
MENU_TITLE=(128,255,10)

# Path for fonts
# Fonts used are taken from the waveshare LCD interface example code
# URL : https://www.waveshare.com/w/upload/a/a8/LCD_Module_RPI_code.7z
boot_screen = ImageFont.truetype("./font/Font01.ttf",50)
menu_icon_large = ImageFont.truetype("./font/Font02.ttf",30)
menu_icon = ImageFont.truetype("./font/Font02.ttf",24)
home_info = ImageFont.truetype("./font/Font02.ttf",19)
menu_title = ImageFont.truetype("./font/Font02.ttf",30)
menu_line = ImageFont.truetype("./font/Font02.ttf",24)

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

def draw_bar(image,value,background_color=GRAY,bar_fill_color=WHITE):
    draw = ImageDraw.Draw(image)
    # Draw a handy on-screen bar to show us the current brightness
    bar_width = int((225 / 100.0) * value)
    draw.rectangle((10,216,230,216), background_color)
    draw.rectangle((10,216,5+bar_width,216), bar_fill_color)
    # return the resulting image
    return image

def progress_bar(image_file,value,x,imagecount,mode,background_color=GRAY,bar_fill_color=WHITE):
    basewidth = 240
    image = Image.open(image_file)
    wpercent = (basewidth/float(image.size[0]))
    hsize = int((float(image.size[1])*float(wpercent)))
    image= image.resize((basewidth,hsize), resample=Image.BICUBIC)
    new_image=Image.new("RGB",(240,240),color='black')
    new_image.paste(image,(0,30))
    draw = ImageDraw.Draw(new_image)
    # Draw a handy on-screen bar to show us the current brightness
    bar_width = int((225 / 100.0) * value)
    if( mode == 1 ):                # mode 1 - stills
        draw.text((60,5),"PIC", fill = MENU_TEXT,font = home_info)
    elif( mode == 3 ):              # mode 3 - timelapse stills
        draw.text((60,5),"TLP", fill = MENU_TEXT,font = home_info)
    elif( mode == 4 ):              # mode 4 - timelapse video
        draw.text((60,5),"TLV", fill = MENU_TEXT,font = home_info)
    draw.text((80,5),str(x)+" / "+str(imagecount), fill = YELLOW,font = home_info)
    draw.rectangle((10,216,230,216), background_color)
    draw.rectangle((10, 216,5+bar_width, 216), bar_fill_color)
    st7789.display(new_image)

#############################################################################
# Functions to print specific menu options for camera
#############################################################################

def boot_disp(file_name):
    dir= "logo"
    camera_logo_file= os.path.join(os.getcwd(),dir,file_name)
    image=Image.open(camera_logo_file)
    image=image.resize((240,240), resample=Image.BICUBIC)
    draw = ImageDraw.Draw(image)
    st7789.display(image)

def menu_display(header,menu_item,display_config,bar_value=0):
    item_number = display_config["menu"] % 10
    image=Image.new("RGB",(240,240),color='black')
    draw = ImageDraw.Draw(image)
################# Interface Buttons #########################
    if(display_config["left"]):
        draw.text((80,215),"<", fill = RED,font = menu_icon)
    if(display_config["right"]):
        draw.text((145,215),">",fill = RED,font = menu_icon)
    if(display_config["down"]):
        draw.text((5,215),"↓", fill = RED,font = menu_icon_large)
    if(display_config["up"]):
        draw.text((212,215),"↑", fill = RED,font = menu_icon_large)
#############################################################
    draw.text((0,5),header,fill = MENU_TITLE,font = menu_title)
    count = 0
    for item in menu_item:
        if(item_number == (count+1)):
            draw.rectangle([(230,(36+(25*(count+1)))),(10,(36+(25*count)))],fill = MENU_SELECT)
            draw.text((15,(33+(25*count))),item,fill = BLACK,font = menu_line)
        else:
            draw.text((15,(33+(25*count))),item,fill = MENU_TEXT,font = menu_line)
        count += 1
    if(display_config["menu"] == 41):
        st7789.display(draw_bar(image,display_config["brightness"]))
    elif(display_config["menu"] == 42):
        if(bar_value < 50):
            COLOR = GREEN
        elif(bar_value >= 50 and bar_value <=75):
            COLOR = YELLOW
        else:
            COLOR = RED
        st7789.display(draw_bar(image,bar_value,bar_fill_color=COLOR))
    st7789.display(image)

def camera_home(display_config,shoot_config,camera_config):
#    img= img.resize((240,180), resample=Image.BICUBIC)
    image=Image.new("RGB",(240,240),color='black')
#    image.paste(img,(0,30))
    draw = ImageDraw.Draw(image)
    if(camera_config["exposure"] == 0):
        draw.text((130,5),exposure_time[camera_config["exposure"]],fill = MENU_TEXT, font = home_info)
    else:
        draw.text((130,5),exposure_time[camera_config["exposure"]],fill = MENU_TITLE, font = home_info)
    if( shoot_config["shoot_mode"] == 1 ):                # mode 1 - stills
        draw.text((55,5),"PIC", fill = MENU_TEXT,font = home_info)
    elif( shoot_config["shoot_mode"] == 2 ):              # mode 2 - bracketing
        draw.text((55,5),"BKT", fill = MENU_TEXT,font = home_info)
    elif( shoot_config["shoot_mode"] == 3 ):              # mode 3 - timelapse stills
        draw.text((55,5),"TLP", fill = MENU_TEXT,font = home_info)
    elif( shoot_config["shoot_mode"] == 4 ):              # mode 4 - timelapse video
        draw.text((55,5),"TLV", fill = MENU_TEXT,font = home_info)
    if(camera_config["bnw"]):
        draw.text((5,5),"B & W", fill = MENU_TEXT,font = home_info)
    else:
        draw.text((5,5),"COLOR", fill = MENU_TITLE,font = home_info)
    if (camera_config["raw"]):
        draw.text((90,5),"RAW", fill = MENU_TEXT,font = home_info)
    else:
        draw.text((90,5),"JPG", fill = MENU_TEXT,font = home_info)
    draw.text((3,215),"[•]", fill = RED,font = menu_icon)
    if(display_config["left"]):
        draw.text((80,215),"<", fill = RED,font = menu_icon)
    if(display_config["right"]):
        draw.text((145,215),">",fill = RED,font = menu_icon)
    draw.rectangle([(210,220),(232,221)],fill = RED)
    draw.rectangle([(210,229),(232,230)],fill = RED)
    draw.rectangle([(210,238),(232,239)],fill = RED)
    st7789.display(image)

def menu_control(display_config,shoot_config,camera_config):
    menu = display_config.get("menu")
    if( menu >= 1 and menu <= 9):
        items=["Camera Control","Shooting Mode","Global Settings","System Menu","Power Options"]
        menu_display("Menu",items,display_config)

    elif( menu >= 11 and menu <= 19 ):        # Image settings
        items=["Exposure","Contrast","Sharpness","Output","Format","Size"]
        if(shoot_config["shoot_mode"] == 1):
            menu_page_title = "Single Image Setup"
        elif(shoot_config["shoot_mode"] == 2):
            menu_page_title = "Bracketing Setup"
        elif(shoot_config["shoot_mode"] == 3):
            menu_page_title = "Interval Timer Setup"
        elif(shoot_config["shoot_mode"] == 4):
            menu_page_title = "Timelapse Movie Setup"
        items[0] = items[0] + " → " + exposure_time[camera_config["exposure"]]
        items[1] = items[1] + " → " + str(camera_config["contrast"])
        items[2] = items[2] + " → " + str(camera_config["sharpness"])
        if(camera_config["bnw"]):
            items[3] = items[3] + " → B & W"
        else:
            items[3] = items[3] + " → COLOR"
        if(camera_config["raw"]):
            items[4] = items[4] + " → JPG + RAW"
        else:
            items[4] = items[4] + " → JPG"
        items[5] = items[5] + " → " + str(image_h[camera_config["image_size"]]) +" X " + str(image_w[camera_config["image_size"]])
        menu_display(menu_page_title,items,display_config)

    elif( menu >= 21 and menu <= 29 ):        # Shooting mode
        items=["Single Shot","Bracketing","Interval Timer Shoot","Timelapse Movie"]
        menu_display("Shooting Mode",items,display_config)

    elif( menu >= 222 and menu <= 229 ):      # Bracketing submenu
        items=["Single Shot","Bracketing","* Frames","Interval Timer Shoot","Timelapse Movie"]
        
        items[2]=items[2] + " → " + str(shoot_config["bkt_frame_count"])
        menu_display("Shooting Mode",items,display_config)

    elif( menu >= 233 and menu <= 239 ):      # Timelapse photo submenu
        items=["Single Shot","Bracketing","Interval Timer Shoot","* Frames","* Interval","Timelapse Movie"]
        items[3]=items[3] + " → " + str(shoot_config["tlp_frame_count"])
        items[4]=items[4] + " → " + str(shoot_config["tlp_interval"])
        menu_display("Shooting Mode",items,display_config)

    elif( menu >= 244 and menu <= 249 ):      # Timelapse video submenu
        items=["Single Shot","Bracketing","Interval Timer Shoot","Timeplapse Movie","* Frames","* Interval"]
        items[4]=items[4] + " → " + str(shoot_config["tlv_frame_count"])
        items[5]=items[5] + " → " + str(shoot_config["tlv_interval"])
        menu_display("Shooting Mode",items,display_config)

    elif( menu >= 41 and menu <= 49 ):        # System Menu
        items=["Screen Brightness","Disk","Wipe Data","Save Settings","Load Settings","Reset Settings"]
        usage = 0
        if(menu == 41):                             # Brightness Control
            items[0] = items[0] + " → " + str(display_config["brightness"])

        elif(menu == 42):                           # Disk space usage info
            memory=shutil.disk_usage(shoot_config["storage_path"])
            usage=int((memory[1]/memory[0])*100)
            used=(memory[1]/1024)
            total=(memory[0]/1024)/1024
            if(used > 0 and used < 1024):
                value = str(round(used,2)) + "k /" + str(round((total/1024),2)) + "g"
            elif(used >= 1024 and used < 1048576): # and used < 1073741824):
                value = str(round((used/1024),2)) + "m /" + str(round((total/1024),2)) + "g"
            else:
                value = str(round(((used/1024)/1024),2)) + "g /" + str(round((total/1024),2)) + "g"
            items[1] = items[1] + " → " + value
        menu_display("System Menu",items,display_config,usage)

    elif( menu == 433 ):                            # Wipe data
        items=["Screen Brightness","Disk","Wipe Data → Sure ?","Save Settings","Load Settings","Reset Settings"]
        menu_display("System Menu",items,display_config)

    elif( menu == 4333 ):                           # Wipe data confirmation
        items=["Screen Brightness","Disk","Wipe Data → Done !","Save Settings","Load Settings","Reset Settings"]
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[2] = "Wipe Data"
        menu_display("System Menu",items,display_config)

    elif( menu == 444 ):                            # Save settings
        items=["Screen Brightness","Disk","Wipe Data","Save Settings → Sure ?","Load Settings","Reset Settings"]
        menu_display("System Menu",items,display_config)

    elif( menu == 4444 ):                           # Save settings confirmation
        items=["Screen Brightness","Disk","Wipe Data","Save Settings → Done !","Load Settings","Reset Settings"]
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[3] = "Save Settings"
        menu_display("System Menu",items,display_config)

    elif( menu == 455 ):                            # Load settings
        items=["Screen Brightness","Disk","Wipe Data","Save Settings","Load Settings → Sure ?","Reset Settings"]
        menu_display("System Menu",items,display_config)

    elif( menu == 4555 ):                           # Load settings confirmation
        items=["Screen Brightness","Disk","Wipe Data","Save Settings","Load Settings → Done !","Reset Settings"]
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[4] = "Load Settings"
        menu_display("System Menu",items,display_config)

    elif( menu == 466 ):                            # Load settings
        items=["Screen Brightness","Disk","Wipe Data","Save Settings","Load Settings","Reset Settings → Sure ?"]
        menu_display("System Menu",items,display_config)

    elif( menu == 4666 ):                           # Load settings confirmation
        items=["Screen Brightness","Disk","Wipe Data","Save Settings","Load Settings","Reset Settings → Done !"]
        menu_display("System Menu",items,display_config)
        time.sleep(1)
        items[5] = "Reset Settings"
        menu_display("System Menu",items,display_config)

    elif( menu >= 51 and menu <= 59 ):              # Power Options
        items=["Reboot","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 511 ):
        items=["Reboot → Sure ?","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5112 ):
        items=["Reboot","→ Configs saved","Poweroff"]
        menu_display("Power Options",items,display_config)
    
    elif( menu == 5113 ):
        items=["Reboot","→ Configs saved","→ Camera stopped","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5114 ):
        items=["Reboot","→ Configs saved","→ Camera stopped","→ Rebooting now . . .","Poweroff"]
        menu_display("Power Options",items,display_config)

    elif( menu == 522 ):
        items=["Reboot","Poweroff → Sure ?"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5223 ):
        items=["Reboot","Poweroff","→ Configs saved"]
        menu_display("Power Options",items,display_config)

    elif( menu == 5224 ):
        items=["Reboot","Poweroff","→ Configs saved","→ Camera stopped"]
        menu_display("Power Options",items,display_config)
    elif( menu == 5225 ):
        items=["Reboot","Poweroff","→ Configs saved","→ Camera stopped","→ Bye Bye !!!"]
        menu_display("Power Options",items,display_config)

