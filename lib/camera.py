# Using picamera2 module capture image in jpg and dng format as per requirement

from PIL import Image, ImageOps
from picamera2 import Picamera2, Preview
from libcamera import controls
picam2 = Picamera2()

def initialize_camera(img_h,img_w,exposure):
    picam2.stop()
    camera_config = picam2.create_still_configuration(raw={}, main={"size": (img_h, img_w)}, lores={"size": (640, 480)}, display=None,queue=False)
    # camera_config = picam2.create_still_configuration( main={"size": (img_h, img_w)}, lores={"size": (640, 480)}, display=None, raw=picam2.sensor_modes[4],queue=False)
    # Setting up image quality to highest
    picam2.options['quality'] = 100  # values from 0 to 100
    # Configure camera as per above parameters
    picam2.configure(camera_config)
    # Initialize camera
    picam2.start()
    if(exposure != 0):
        picam2.set_controls({"ExposureTime": exposure})

def shoot_preview(bnw,exposure):
#    picam2.set_controls({"ExposureTime": 4000})
    image = picam2.capture_image()
    if(bnw):
        img=ImageOps.grayscale(image)
    else:
        img=image
#    picam2.set_controls({"ExposureTime": exposure})
    return img

def shoot(raw_flag,bnw_flag,image_filename):
    r = picam2.capture_request()
    r.save("main",image_filename+".jpg")
    if (raw_flag):       # Save dng RAW file if flag set to True
        r.save_dng(image_filename+".dng")
    r.release()
    if (bnw_flag):
        image=Image.open(image_filename+".jpg")
        img=ImageOps.grayscale(image)
        img.save(image_filename+".jpg")
