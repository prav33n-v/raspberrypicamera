import os
import shutil
import json
import time
from PIL import Image, ImageOps
import lib.audioDAC_lcd as lcd
import lib.camera as camera

def increment(value,num):
    return (value+num)

def decrement(value,num):
    return (value-num)

def down(value,minval,maxval):
    if(value < maxval):
        return (value+1)
    else:
        return minval

def up(value,minval,maxval):
    if(value > minval):
        return (value-1)
    else:
        return maxval

def check_left_right(value,lower_limit,higher_limit,difference):
    left_flag = True
    right_flag = True
    if((value > (lower_limit + difference)) and (value < higher_limit - difference)):
        left_flag = True
        right_flag = True
    elif(value <= (lower_limit + difference)):
        left_flag = False
        right_flag = True
    else:
        left_flag = True
        right_flag = False
    return left_flag,right_flag
        
def load_settings(file_type = "default"):
    dir="config"
    filename = "display_config-" + file_type + ".json"
    config_file= os.path.join(os.getcwd(),dir,filename)
    with open(config_file,'r') as openfile:
        display_config = json.load(openfile)
    filename = "shoot_config-" + file_type + ".json"
    config_file= os.path.join(os.getcwd(),dir,filename)
    with open(config_file,'r') as openfile:
        shoot_config = json.load(openfile)
    filename = "camera_config-" + file_type + ".json"
    config_file= os.path.join(os.getcwd(),dir,filename)
    with open(config_file,'r') as openfile:
        camera_config = json.load(openfile)
    if(shoot_config["shoot_mode"] == 2):
        if(camera_config["exposure"] <= (shoot_config["bkt_frame_count"] // 2)):
            camera_config["exposure"] += ((shoot_config["bkt_frame_count"] // 2)+1)
        elif(camera_config["exposure"] > (49 - (shoot_config["bkt_frame_count"] // 2))):
            camera_config["exposure"] -= (shoot_config["bkt_frame_count"] // 2)
    camera.initialize_camera(camera_config)
    return display_config,shoot_config,camera_config

def save_settings(display_config,shoot_config,camera_config,file_type = "default"):
    temp_menu = display_config["menu"]
    display_config["menu"] = 0
    dir="config"
    filename = "display_config-" + file_type + ".json"
    config_file= os.path.join(os.getcwd(),dir,filename)
    with open(config_file,'w') as outfile:
        json.dump(display_config,outfile)
    display_config["menu"] = temp_menu
    filename = "shoot_config-" + file_type + ".json"
    config_file= os.path.join(os.getcwd(),dir,filename)
    with open(config_file,'w') as outfile:
        json.dump(shoot_config,outfile)
    filename = "camera_config-" + file_type + ".json"
    config_file= os.path.join(os.getcwd(),dir,filename)
    with open(config_file,'w') as outfile:
        json.dump(camera_config,outfile)

def reset_settings():
    display_conf,shoot_conf,camera_conf = load_settings()
    save_settings(display_conf,shoot_conf,camera_conf,"custom")
    save_settings(display_conf,shoot_conf,camera_conf,"auto_saved")
    camera.initialize_camera(camera_conf)
    return display_conf,shoot_conf,camera_conf
    
def reboot(display_config,shoot_config,camera_config):
    display_config["menu"] = 0
    save_settings(display_config,shoot_config,camera_config,"auto_saved")
    display_config["menu"] = 5112
    lcd.menu_control(display_config,shoot_config,camera_config)
    display_config["menu"] = 5113
    lcd.menu_control(display_config,shoot_config,camera_config)
    display_config["menu"] = 5114
    lcd.menu_control(display_config,shoot_config,camera_config)
    lcd.boot_disp("camera_down_logo.jpeg")
    os.system("sudo reboot")
    time.sleep(5)
    
def single_shot(display_config,shoot_config,camera_config,path):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    image_filename = path + "img_" + str(timestr)
    camera.shoot(camera_config,image_filename)
    image=Image.open(image_filename+".jpg")
    lcd.camera_home(display_config,shoot_config,camera_config,image)

def bracketing(display_config,shoot_config,camera_config,path):
    os.mkdir(path)
    original_exposure_value = camera_config["exposure"]
    exposure_value = camera_config["exposure"] - (shoot_config["bkt_frame_count"]//2)
    for x in range(shoot_config["bkt_frame_count"]):
        image_filename=path+"BKT_"+str(x)
        camera_config["exposure"] = exposure_value + x
        print(camera_config)
        camera.initialize_camera(camera_config)
        camera.shoot(camera_config,image_filename)
        lcd.progress_bar(image_filename+".jpg",x,shoot_config,camera_config)
    camera_config["exposure"] = original_exposure_value
    camera.initialize_camera(camera_config)
    lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))

def interval_timer(display_config,shoot_config,camera_config,path):
    os.mkdir(path)
    for x in range(shoot_config["tlp_frame_count"]):
        image_filename=path+"InT_"+str(x)
        camera.shoot(camera_config,image_filename)
        time.sleep(shoot_config["tlp_interval"])
        lcd.progress_bar(image_filename+".jpg",x,shoot_config,camera_config)
    lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))

def timelapse(display_config,shoot_config,camera_config,path):
    os.mkdir(path)
    for x in range(shoot_config["tlv_frame_count"]):
        image_filename=path+"TLV_"+str(x)
        camera.shoot(camera_config,image_filename)
        time.sleep(shoot_config["tlv_interval"])
        lcd.progress_bar(image_filename+".jpg",x,shoot_config,camera_config)
    lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))
    
def poweroff(display_config,shoot_config,camera_config):
    display_config["menu"] = 0
    save_settings(display_config,shoot_config,camera_config,"auto_saved")
    display_config["menu"] = 5223
    lcd.menu_control(display_config,shoot_config,camera_config)
    display_config["menu"] = 5224
    lcd.menu_control(display_config,shoot_config,camera_config)
    display_config["menu"] = 5225
    lcd.menu_control(display_config,shoot_config,camera_config)
    lcd.boot_disp("camera_down_logo.jpeg")
    os.system("sudo poweroff")
    time.sleep(5)

    
def back_button(display_config,shoot_config,camera_config):
    if (display_config["menu"] == -1):
        camera.initialize_camera(camera_config)
        display_config["menu"] = 0
        lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))
    elif(display_config["menu"] == 0):
        lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))
    else:
        if(display_config["menu"] > 0 and display_config["menu"] < 9):          # Back from main menu page to home screen
            display_config["menu"] = 0
            lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))

        elif(display_config["menu"] > 10 and display_config["menu"] < 19):      # Back from image settings page to main menu page
            camera.initialize_camera(camera_config)
            display_config["menu"] = 1
            display_config["left"] = display_config["right"] = False

        elif(display_config["menu"] > 20 and display_config["menu"] < 29):      # Back from shooting mode page to main menu page
            display_config["menu"] = 2
            if(shoot_config["shoot_mode"] == 2):
                if(camera_config["exposure"] <= (shoot_config["bkt_frame_count"] // 2)):
                    camera_config["exposure"] += ((shoot_config["bkt_frame_count"] // 2)+1)
                elif(camera_config["exposure"] > (49 - (shoot_config["bkt_frame_count"] // 2))):
                    camera_config["exposure"] -= (shoot_config["bkt_frame_count"] // 2)

        elif(display_config["menu"] >= 221 and display_config["menu"] <=229):   # Back from bracketing mode submenu to shooting mode page
            display_config["menu"] = 22 
            display_config["left"] = display_config["right"] = False
            display_config["up"] = display_config["down"] = True

        elif(display_config["menu"] >= 231 and display_config["menu"] <=239):   # Back from timelapse photo mode submenu to shooting mode page
            display_config["menu"] = 23
            display_config["left"] = display_config["right"] = False

        elif(display_config["menu"] >= 241 and display_config["menu"] <=249):   # Back from timelapse video mode submenu to shooting mode page
            display_config["menu"] = 24
            display_config["left"] = display_config["right"] = False

        elif(display_config["menu"] > 30 and display_config["menu"] < 39):      # Back from image settings menu page to main menu page
            display_config["menu"] = 3

        elif(display_config["menu"] > 40 and display_config["menu"] < 49):      # Back from system menu page to main menu page
            display_config["menu"] = 4
            display_config["left"] = display_config["right"] = False

        elif(display_config["menu"] == 4333 or display_config["menu"] == 433):  # Back from wiping data of system menu page
            display_config["menu"] = 4

        elif(display_config["menu"] == 4444 or display_config["menu"] == 444):  # Back from save setting of system menu page
            display_config["menu"] = 4

        elif(display_config["menu"] == 4555 or display_config["menu"] == 455):  # Back from load setting of system menu page
            display_config["menu"] = 4

        elif(display_config["menu"] == 4666 or display_config["menu"] == 466):  # Back from reset setting of system menu page
            display_config["menu"] = 4

        elif(display_config["menu"] > 50 and display_config["menu"] < 59):      # Back from power options page to main menu page
            display_config["menu"] = 5

        elif(display_config["menu"] == 511):      # Back from reboot option confirmation to main menu page
            display_config["menu"] = 51

        elif(display_config["menu"] == 522):      # Back from poweroff option confirmation to main menu page
            display_config["menu"] = 52

        else:
            print("Unexpected menu value BACK button : ",display_config["menu"])
        lcd.menu_control(display_config,shoot_config,camera_config)
    return display_config,shoot_config,camera_config

def ok_shutter_button(display_config,shoot_config,camera_config):
    if (display_config["menu"] == -1):
        camera.initialize_camera(camera_config)
        display_config["menu"] = 0
        lcd.camera_home(display_config,shoot_config,camera_config,camera.shoot_preview(camera_config))
    elif (display_config["menu"] == 0):     # Capture
        if(shoot_config["shoot_mode"] == 1):  # Single shot
            if(os.path.exists(shoot_config["storage_path"] + "Photo/")):
                print("Photo directory exists. Writing in directory...")
            else:
                print("Photo directory not found. Creating directory...")
                os.mkdir(shoot_config["storage_path"] + "Photo/")
            path = shoot_config["storage_path"] + "Photo/"
            single_shot(display_config,shoot_config,camera_config,path)
        elif(shoot_config["shoot_mode"] == 2):  # Bracketing
            timestr = time.strftime("%Y%m%d-%H%M%S")
            if(os.path.exists(shoot_config["storage_path"] + "Bracketing/")):
                print("Bracketing directory exists. Writing in directory...")
            else:
                print("Bracketing directory not found. Creating directory...")
                os.mkdir(shoot_config["storage_path"] + "Bracketing/")
            path = shoot_config["storage_path"] + "Bracketing/BKT_" + str(timestr)+"/"
            bracketing(display_config,shoot_config,camera_config,path)
        elif(shoot_config["shoot_mode"] == 3):  # Start Interval timer shooting
            timestr = time.strftime("%Y%m%d-%H%M%S")
            if(os.path.exists(shoot_config["storage_path"] +"IntervalTimer/")):
                print("Writing in Interval Timer folder'")
            else:
                os.mkdir(shoot_config["storage_path"] +"IntervalTimer/")
            path = shoot_config["storage_path"]  + "IntervalTimer/TLS_" + str(timestr)+"/"
            interval_timer(display_config,shoot_config,camera_config,path)
        elif(shoot_config["shoot_mode"] == 4):
            timestr = time.strftime("%Y%m%d-%H%M%S")
            if(os.path.exists(shoot_config["storage_path"] +"TimelapseMovie/")):
                print("Writing in TimelapseMovie folder'")
            else:
                os.mkdir(shoot_config["storage_path"] +"TimelapseMovie/")
            path = shoot_config["storage_path"]  + "TimelapseMovie/TLV_" + str(timestr)+"/"
            timelapse(display_config,shoot_config,camera_config,path)
    elif(display_config["menu"] == 1):                                      # Select image settings from main menu page
        display_config["menu"] = 11
        display_config["left"] = display_config["right"] = True
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
        display_config["left"] = display_config["right"] = True
        display_config["up"] = display_config["down"] = False
        shoot_config["shoot_mode"]=2
    elif(display_config["menu"] == 23):                                     # Select timelapse photo mode from shooting mode page
        display_config["menu"] = 234
        if(shoot_config["tlp_frame_count"] > (shoot_config["tlp_max_frame"]-5)):  
            display_config["right"] = False
        else:
            display_config["right"] = True
        if(shoot_config["tlp_frame_count"] < (shoot_config["tlp_min_frame"]+5)):  
            display_config["left"] = False
        else:
            display_config["left"] = True
        shoot_config["shoot_mode"]=3
    elif(display_config["menu"] == 24):                                     # Select timelapse photo mode from shooting mode page
        display_config["menu"] = 245
        if(shoot_config["tlv_frame_count"] > 8):  
            display_config["right"] = False
        else:
            display_config["right"] = True
        if(shoot_config["tlv_frame_count"] < 4):  
            display_config["left"] = False
        else:
            display_config["left"] = True
        shoot_config["shoot_mode"]=4
    elif(display_config["menu"] == 3):                                      # Select image settings menu from main menu page
        display_config["menu"] = 31
    elif(display_config["menu"] == 4):                                      # Select system menu from main menu page
        display_config["menu"] = 41
        display_config["left"] = display_config["right"] = True
    elif(display_config["menu"] == 43):                                     # Select wipe data from system menu page
        display_config["menu"] = 433
    elif(display_config["menu"] == 433):                                    # Confirm wipe data from system menu page
        targetDir=["Photo","Bracketing","IntervalTimer","Timelapse_Movie"]
        for x in targetDir:
            path=os.path.join(shoot_config["storage_path"],x)
            shutil.rmtree(path, ignore_errors=True)
        display_config["menu"] = 4333
    elif(display_config["menu"] == 4333):                                   # After wiping data from system menu page
        display_config["menu"] = 43
    elif(display_config["menu"] == 44):                                     # Select save settings from system menu page
        display_config["menu"] = 444
    elif(display_config["menu"] == 444):                                    # Confirm save settings from system menu page
        save_settings(display_config,shoot_config,camera_config,"custom")
        display_config["menu"] = 4444
    elif(display_config["menu"] == 4444):                                   # After saving settings from system menu page
        display_config["menu"] = 44
    elif(display_config["menu"] == 45):                                     # Select load settings from system menu page
        display_config["menu"] = 455
    elif(display_config["menu"] == 455):                                    # Confirm load settings from system menu page
        display_config,shoot_config,camera_config = load_settings("custom")
        display_config["menu"] = 4555
    elif(display_config["menu"] == 4555):                                   # After loading settings from system menu page
        display_config["menu"] = 45
    elif(display_config["menu"] == 46):                                     # Select reset settings from system menu page
        display_config["menu"] = 466
    elif(display_config["menu"] == 466):                                    # Confirm reset settings from system menu page
        display_config,shoot_config,camera_config = reset_settings()
        display_config["menu"] = 4666
    elif(display_config["menu"] == 4666):                                   # After resetting settings from system menu page
        display_config["menu"] = 46
    elif(display_config["menu"] == 5):                                      # Select power options menu from main menu page
        display_config["menu"] = 51
    elif(display_config["menu"] == 51):										# Select standby mode
        display_config["menu"] = 511
    elif(display_config["menu"] == 511):                                    # Confirm standby option from power options
        display_config["menu"] = -2
        camera.stop_camera()
    elif(display_config["menu"] == 52):                                     # Select reboot option from power options
        display_config["menu"] = 522
    elif(display_config["menu"] == 522):                                    # Confirm reboot from power options
        reboot(display_config,shoot_config,camera_config)
    elif(display_config["menu"] == 53):                                     # Select poweroff option from power options
        display_config["menu"] = 533
    elif(display_config["menu"] == 533):                                    # Confirm poweroff from power options
        poweroff(display_config,shoot_config,camera_config)
    else:
        print("Unexpected menu value OK_SHUTTER button : ",display_config["menu"])
    lcd.menu_control(display_config,shoot_config,camera_config)
    return display_config,shoot_config,camera_config

def down_button(display_config,shoot_config,camera_config):
    if(display_config["menu"] >= 1 and display_config["menu"] <=9):         # Main menu page
        display_config["menu"] = down(display_config["menu"],1,5) 
    elif(display_config["menu"] >= 11 and display_config["menu"] <=19):     # Camera settings page
        display_config["menu"] = down(display_config["menu"],11,16) 
    elif(display_config["menu"] >= 21 and display_config["menu"] <=29):     # Shooting mode page
        display_config["menu"] = down(display_config["menu"],21,24) 
        shoot_config["shoot_mode"] = display_config["menu"] % 10
    elif(display_config["menu"] >= 31 and display_config["menu"] <=39):     # Image settings page
        display_config["menu"] = down(display_config["menu"],31,34)
    elif(display_config["menu"] >= 231 and display_config["menu"] <=239):   # Timelapse photo submenu
        display_config["menu"] = down(display_config["menu"],234,235) 
        if(display_config["menu"] == 234):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_frame_count"],shoot_config["tlp_min_frame"],shoot_config["tlp_max_frame"],5)
        if(display_config["menu"] == 235):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0) 
    elif(display_config["menu"] >= 241 and display_config["menu"] <=249):   # Timelapse video submenu
        display_config["menu"] = down(display_config["menu"],245,246) 
        if(display_config["menu"] == 245):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_frame_count"],shoot_config["tlv_min_frame"],shoot_config["tlv_max_frame"],15)
        if(display_config["menu"] == 246):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0)
    elif(display_config["menu"] >= 41 and display_config["menu"] <=49):     # System menu page
        display_config["menu"] = down(display_config["menu"],41,46) 
        if(display_config["menu"] == 41):
            display_config["left"],display_config["right"] = check_left_right(display_config["brightness"],5,100,2)
    elif(display_config["menu"] == 4333 or display_config["menu"] == 433):  # After wiping data from system menu page
        display_config["menu"] = 44
    elif(display_config["menu"] == 4444 or display_config["menu"] == 444):  # After save settings from system menu page
        display_config["menu"] = 45
    elif(display_config["menu"] == 4555 or display_config["menu"] == 455):  # After load settings from system menu page
        display_config["menu"] = 46
    elif(display_config["menu"] == 4666 or display_config["menu"] == 466):  # After reset settings from system menu page
        display_config["menu"] = 41
    elif(display_config["menu"] >= 51 and display_config["menu"] <=59):     # Power options page
        display_config["menu"] = down(display_config["menu"],51,53) 
    else:
        print("Unexpected menu value DOWN button : ",display_config["menu"])
    lcd.menu_control(display_config,shoot_config,camera_config)
    return display_config,shoot_config,camera_config


def up_button(display_config,shoot_config,camera_config):
    if(display_config["menu"] == 0):
        display_config["menu"] = 1
    elif(display_config["menu"] >= 1 and display_config["menu"] <=9):       # Main menu page
        display_config["menu"] = up(display_config["menu"],1,5) 
    elif(display_config["menu"] >= 11 and display_config["menu"] <=19):     # Camera settings page
        display_config["menu"] = up(display_config["menu"],11,16) 
    elif(display_config["menu"] >= 21 and display_config["menu"] <=29):     # Shooting mode page
        display_config["menu"] = up(display_config["menu"],21,24) 
        shoot_config["shoot_mode"] = display_config["menu"] % 10
    elif(display_config["menu"] >= 31 and display_config["menu"] <=39):     # Image settings page
        display_config["menu"] = up(display_config["menu"],31,34)
    elif(display_config["menu"] >= 231 and display_config["menu"] <=239):   # Timelapse photo submenu
        display_config["menu"] = up(display_config["menu"],234,235)
        if(display_config["menu"] == 234):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_frame_count"],shoot_config["tlp_min_frame"],shoot_config["tlp_max_frame"],5)
        if(display_config["menu"] == 235):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0) 
    elif(display_config["menu"] >= 241 and display_config["menu"] <=249):   # Timelapse video submenu
        display_config["menu"] = up(display_config["menu"],245,246) 
        if(display_config["menu"] == 245):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_frame_count"],shoot_config["tlv_min_frame"],shoot_config["tlv_max_frame"],15)
        if(display_config["menu"] == 246):
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0)
    elif(display_config["menu"] >= 41 and display_config["menu"] <=49):     # System menu page
        display_config["menu"] = up(display_config["menu"],41,46) 
        if(display_config["menu"] == 41):
            display_config["left"],display_config["right"] = check_left_right(display_config["brightness"],5,100,2)
    elif(display_config["menu"] == 4333 or display_config["menu"] == 433):  # Move up from wipe data option of system menu page
        display_config["menu"] = 42
    elif(display_config["menu"] == 4444 or display_config["menu"] == 444):  # Move up from save setting option of system menu page
        display_config["menu"] = 43
    elif(display_config["menu"] == 4555 or display_config["menu"] == 455):  # Move up from load setting option of system menu page
        display_config["menu"] = 44
    elif(display_config["menu"] == 4666 or display_config["menu"] == 466):  # Move up from reset setting option of system menu page
        display_config["menu"] = 45
    elif(display_config["menu"] >= 51 and display_config["menu"] <=59):     # Power options page navigation
        display_config["menu"] = up(display_config["menu"],51,53) 
    else:
        print("Unexpected menu value UP button : ",display_config["menu"])
    lcd.menu_control(display_config,shoot_config,camera_config)
    return display_config,shoot_config,camera_config


def left_button(display_config,shoot_config,camera_config):
    if(display_config["menu"] == 41):                                       # Brightness decrease
        if(display_config["brightness"] > 5):
            display_config["brightness"] = decrement(display_config["brightness"],5)
            display_config["left"],display_config["right"] = check_left_right(display_config["brightness"],5,100,2)
    elif(display_config["menu"] == 11):
        min_exposure = 0
        max_exposure = 49
        if(shoot_config["shoot_mode"] == 2):
            min_exposure = (shoot_config["bkt_frame_count"] // 2) + 1
            max_exposure = (49 - (shoot_config["bkt_frame_count"] // 2))
        if(camera_config["exposure"] > min_exposure):
            camera_config["exposure"] = decrement(camera_config["exposure"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["exposure"],min_exposure,max_exposure,0)
    elif(display_config["menu"] == 12):
        if(camera_config["analogue_gain"] > camera_config["min_analogue_gain"]):
            camera_config["analogue_gain"] = decrement(camera_config["analogue_gain"],0.5)
            display_config["left"],display_config["right"] = check_left_right(camera_config["analogue_gain"],camera_config["min_analogue_gain"],camera_config["max_analogue_gain"],0)
    elif(display_config["menu"] == 13):
        if(camera_config["contrast"] > camera_config["min_contrast"]):
            camera_config["contrast"] = decrement(camera_config["contrast"],0.5)
            display_config["left"],display_config["right"] = check_left_right(camera_config["contrast"],camera_config["min_contrast"],camera_config["max_contrast"],0)
    elif(display_config["menu"] == 14):
        if(camera_config["sharpness"] > camera_config["min_sharpness"]):
            camera_config["sharpness"] = decrement(camera_config["sharpness"],0.5)
            display_config["left"],display_config["right"] = check_left_right(camera_config["sharpness"],camera_config["min_sharpness"],camera_config["max_sharpness"],0)
    elif(display_config["menu"] == 15):
        if(camera_config["noise_reduction"] > camera_config["min_noise_reduction"]):
            camera_config["noise_reduction"] = decrement(camera_config["noise_reduction"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["noise_reduction"],camera_config["min_noise_reduction"],camera_config["max_noise_reduction"],0)
    elif(display_config["menu"] == 16):
        if(camera_config["white_balance"] > camera_config["min_white_balance"]):
            camera_config["white_balance"] = decrement(camera_config["white_balance"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["white_balance"],camera_config["min_white_balance"],camera_config["max_white_balance"],0)
    elif(display_config["menu"] == 223):                                    # Decrease bracket frame count
        if(shoot_config["bkt_frame_count"] > 3):
            shoot_config["bkt_frame_count"] = decrement(shoot_config["bkt_frame_count"],2)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["bkt_frame_count"],3,9,1)  
    elif(display_config["menu"] == 234):                                    # Decrease Timelapse photo frame count
        if(shoot_config["tlp_frame_count"] > shoot_config["tlp_min_frame"]):
            shoot_config["tlp_frame_count"] = decrement(shoot_config["tlp_frame_count"],10)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_frame_count"],shoot_config["tlp_min_frame"],shoot_config["tlp_max_frame"],5)
    elif(display_config["menu"] == 235):                                    # Decrease Timelapse photo interval count
        if(shoot_config["tlp_interval"] > shoot_config["min_interval"]):
            shoot_config["tlp_interval"] = decrement(shoot_config["tlp_interval"],1)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0)
    elif(display_config["menu"] == 245):                                    # Decrease Timelapse video frame count
        if(shoot_config["tlv_frame_count"] > shoot_config["tlv_min_frame"]):
            shoot_config["tlv_frame_count"] = decrement(shoot_config["tlv_frame_count"],30)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_frame_count"],shoot_config["tlv_min_frame"],shoot_config["tlv_max_frame"],15)
    elif(display_config["menu"] == 246):                                    # Decrease Timelapse video interval count
        if(shoot_config["tlv_interval"] > shoot_config["min_interval"]):
            shoot_config["tlv_interval"] = decrement(shoot_config["tlv_interval"],1)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0)
    elif(display_config["menu"] == 31):
        if(camera_config["image_size"] > camera_config["min_image_size"]):
            camera_config["image_size"] = decrement(camera_config["image_size"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["image_size"],camera_config["min_image_size"],camera_config["max_image_size"],0)
    elif(display_config["menu"] == 32):                                     # Toggle bnw
        camera_config["bnw"] = not camera_config["bnw"]
    elif(display_config["menu"] == 33):                                     # Toggle raw
        camera_config["raw"] = not camera_config["raw"]
    elif(display_config["menu"] == 34):                                     # Toggle status led
        display_config["status_led"] = not display_config["status_led"]
    lcd.menu_control(display_config,shoot_config,camera_config)
    return display_config,shoot_config,camera_config


def right_button(display_config,shoot_config,camera_config):
    if(display_config["menu"] == 41):
        if(display_config["brightness"] < 100):
            display_config["brightness"] = increment(display_config["brightness"],5)
            display_config["left"],display_config["right"] = check_left_right(display_config["brightness"],5,100,2)
    elif(display_config["menu"] == 11):
        min_exposure = 0
        max_exposure = 49
        if(shoot_config["shoot_mode"] == 2):
            min_exposure = (shoot_config["bkt_frame_count"] // 2) + 1
            max_exposure = (49 - (shoot_config["bkt_frame_count"] // 2))
        if(camera_config["exposure"] < max_exposure):
            camera_config["exposure"] = increment(camera_config["exposure"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["exposure"],min_exposure,max_exposure,0)
    elif(display_config["menu"] == 12):
        if(camera_config["analogue_gain"] < camera_config["max_analogue_gain"]):
            camera_config["analogue_gain"] = increment(camera_config["analogue_gain"],0.5)
            display_config["left"],display_config["right"] = check_left_right(camera_config["analogue_gain"],camera_config["min_analogue_gain"],camera_config["max_analogue_gain"],0)
    elif(display_config["menu"] == 13):
        if(camera_config["contrast"] < camera_config["max_contrast"]):
            camera_config["contrast"] = increment(camera_config["contrast"],0.5)
            display_config["left"],display_config["right"] = check_left_right(camera_config["contrast"],camera_config["min_contrast"],camera_config["max_contrast"],0)
    elif(display_config["menu"] == 14):
        if(camera_config["sharpness"] < camera_config["max_sharpness"]):
            camera_config["sharpness"] = increment(camera_config["sharpness"],0.5)
            display_config["left"],display_config["right"] = check_left_right(camera_config["sharpness"],camera_config["min_sharpness"],camera_config["max_sharpness"],0)
    elif(display_config["menu"] == 15):
        if(camera_config["noise_reduction"] < camera_config["max_noise_reduction"]):
            camera_config["noise_reduction"] = increment(camera_config["noise_reduction"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["noise_reduction"],camera_config["min_noise_reduction"],camera_config["max_noise_reduction"],0)
    elif(display_config["menu"] == 16):
        if(camera_config["white_balance"] < camera_config["max_white_balance"]):
            camera_config["white_balance"] = increment(camera_config["white_balance"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["white_balance"],camera_config["min_white_balance"],camera_config["max_white_balance"],0)
    elif(display_config["menu"] == 223):                                    # Increase bracket frame count
        if(shoot_config["bkt_frame_count"] < 9):
            shoot_config["bkt_frame_count"] = increment(shoot_config["bkt_frame_count"],2)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["bkt_frame_count"],3,9,1) 
    elif(display_config["menu"] == 234):                                    # Increase Timelapse photo frame count
        if(shoot_config["tlp_frame_count"] < shoot_config["tlp_max_frame"]):
            shoot_config["tlp_frame_count"] = increment(shoot_config["tlp_frame_count"],10)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_frame_count"],shoot_config["tlp_min_frame"],shoot_config["tlp_max_frame"],5)
    elif(display_config["menu"] == 235):                                    # Increase Timelapse photo interval count
        if(shoot_config["tlp_interval"] < shoot_config["max_interval"]):
            shoot_config["tlp_interval"] = increment(shoot_config["tlp_interval"],1)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlp_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0)
    elif(display_config["menu"] == 245):                                    # Increase Timelapse video frame count
        if(shoot_config["tlv_frame_count"] < shoot_config["tlv_max_frame"]):
            shoot_config["tlv_frame_count"] = increment(shoot_config["tlv_frame_count"],30)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_frame_count"],shoot_config["tlv_min_frame"],shoot_config["tlv_max_frame"],15)
    elif(display_config["menu"] == 246):                                    # Increase Timelapse video interval count
        if(shoot_config["tlv_interval"] < shoot_config["max_interval"]):
            shoot_config["tlv_interval"] = increment(shoot_config["tlv_interval"],1)
            display_config["left"],display_config["right"] = check_left_right(shoot_config["tlv_interval"],shoot_config["min_interval"],shoot_config["max_interval"],0)
    elif(display_config["menu"] == 31):
        if(camera_config["image_size"] < camera_config["max_image_size"]):
            camera_config["image_size"] = increment(camera_config["image_size"],1)
            display_config["left"],display_config["right"] = check_left_right(camera_config["image_size"],camera_config["min_image_size"],camera_config["max_image_size"],0)
    elif(display_config["menu"] == 32):                                     # Toggle bnw
        camera_config["bnw"] = not camera_config["bnw"]
    elif(display_config["menu"] == 33):                                     # Toggle raw
        camera_config["raw"] = not camera_config["raw"]
    elif(display_config["menu"] == 34):                                     # Toggle status led
        display_config["status_led"] = not display_config["status_led"]
    lcd.menu_control(display_config,shoot_config,camera_config)
    return display_config,shoot_config,camera_config

def menu_fn_button(display_config,shoot_config,camera_config):
    return display_config,shoot_config,camera_config

