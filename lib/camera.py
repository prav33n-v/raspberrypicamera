# Using picamera2 module capture image in jpg and dng format as per requirement

from PIL import Image, ImageOps
from picamera2 import Picamera2, Preview
from libcamera import controls

picam2 = Picamera2()

def initialize_camera(img_h,img_w):
    picam2.stop()
    # camera_config = picam2.create_still_configuration(raw={}, main={"size": (img_h, img_w)}, lores={"size": (640, 480)}, display=None)
    camera_config = picam2.create_still_configuration( main={"size": (img_h, img_w)}, lores={"size": (640, 480)}, display=None, raw=picam2.sensor_modes[4])
    # Setting up image quality to highest
    picam2.options['quality'] = 100  # values from 0 to 100
    # Configure camera as per above parameters
    picam2.configure(camera_config)
    # Initialize camera
    picam2.start()

def shoot_preview(bnw):
    image = picam2.capture_image()
    if(bnw):
        img=ImageOps.grayscale(image)
    else:
        img=image
    return img

def shoot(raw_flag,bnw_flag,image_filename):
    if (raw_flag):      # Save both jpg and dng raw file
        r = picam2.capture_request()
        r.save("main",image_filename+".jpg")
        r.save_dng(image_filename+".dng")
        r.release()
    else:               # Save only jpg file
        image = picam2.capture_image()
        image.save(image_filename+".jpg")
    if (bnw_flag):
        image=Image.open(image_filename+".jpg")
        img=ImageOps.grayscale(image)
        img.save(image_filename+".jpg")

