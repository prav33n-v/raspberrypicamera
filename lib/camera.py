# Using picamera2 module capture image in jpg and dng format as per requirement
import time
from PIL import Image, ImageOps
from picamera2 import Picamera2, Preview
from libcamera import controls
picam2 = Picamera2()

exposure_time=[0,625,800,1000,1250,1562,2000,2500,3125,4000,5000,6250,8000,10000,12500,16667,20000,25000,33333,40000,50000,66667,76923,100000,125000,166667,200000,250000,333333,400000,500000,625000,769231,1000000,1300000,1600000,2000000,2500000,3000000,4000000,5000000,6000000,8000000,10000000,13000000,15000000,20000000,25000000,30000000,60000000]
image_height=[1600,2048,2464,3008,3264,3888,4000,4656]
image_width=[1200,1536,1632,2000,2448,2592,2800,3496]

def initialize_camera(camera_config):
    picam2.stop()
    configuration = picam2.create_still_configuration(raw={}, main={"size": (image_height[camera_config["image_size"]], image_width[camera_config["image_size"]])}, lores={"size": (640, 480)}, display=None,queue=False)
    #configuration = picam2.create_still_configuration(raw={}, main={"size": (image_height[camera_config["image_size"]], image_width[camera_config["image_size"]])}, queue=False)
    # camera_config = picam2.create_still_configuration( main={"size": (img_h, img_w)}, lores={"size": (640, 480)}, display=None, raw=picam2.sensor_modes[4],queue=False)
    # Setting up image quality to highest
#    picam2.options['quality'] = 100  # values from 0 to 100
    # Configure camera as per above parameters
    picam2.configure(configuration)
    # Initialize camera
    picam2.start()
    if(camera_config["exposure"] != 0):
        picam2.set_controls({"ExposureTime": exposure_time[camera_config["exposure"]], "AnalogueGain": camera_config["analogue_gain"], "Contrast": camera_config["contrast"], "Sharpness": camera_config["sharpness"], "NoiseReductionMode": camera_config["noise_reduction"], "AwbMode": camera_config["white_balance"] })

def shoot_preview(camera_config):
    image = picam2.capture_image()
    if(camera_config["bnw"]):
        image=ImageOps.grayscale(image)
    return image

def shoot(camera_config,image_filename):
    r = picam2.capture_request()
    r.save("main",image_filename+".jpg")
    if (camera_config["raw"]):       # Save dng RAW file if flag set to True
        r.save_dng(image_filename+".dng")
    r.release()
    if (camera_config["bnw"]):
        image=Image.open(image_filename+".jpg")
        img=ImageOps.grayscale(image)
        img.save(image_filename+".jpg")

def stop_camera():
    picam2.stop()
