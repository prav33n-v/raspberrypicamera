# RaspberryPiCamera

## Description
This is a project to make a Infrared light sensitive point and shoot camera using the below hardware :
 - Raspberry Pi 4
 - Arducam 16MP NoIR Camera Module
 - Pimoroni TouchPHAT
 - Pimoroni Pirate Audio HAT
 - Pimoroni Hacker HAT

## Installation
To implement this project you need the hardware mentioned in the above decription. I have tested the project in Raspberry Pi 4. I have used Raspbian (32bit) distro during the development of this project on Raspberry Pi 4. Below are the details of distro :

```
Distributor ID:	Raspbian
Description:	Raspbian GNU/Linux 11 (bullseye)
Release:	11
Codename:	bullseye
```

### Installing dependencies
 - To set up this Raspberry Pi camera you need to run the command 
```
   sudo raspi-config

   Enable the following :
	- Enable legacy camera support
	- Enable SPI/I2C/1Wire
	- Expand Filesystem
	- Increase GPU mem to 128

   Reboot after the chnages are done.
```

 - Install the depedencies for Pimoroni TouchPhat by running the below command
```
sudo curl https://get.pimoroni.com/touchphat | bash
```
 - In case of you get <b>error: externally-managed-environment</b> , run below command and the try running the above command again.
```
sudo mv /usr/lib/python3.11/EXTERNALLY-MANAGED /usr/lib/python3.11/EXTERNALLY-MANAGED.old
```
 - Install the python modules/libraries
```
sudo apt install -y build-essential python3-dev python3-smbus python3-pip python3-pil python3-numpy fonts-dejavu imagemagick
sudo pip3 install pidi-display-pil pidi-display-st7789
```

 - If you are using any other camera module then you do not need to execute <b>install_pivariety_pkgs.sh</b>. If you are using the mentioned camera module then you can run the below commands :

```
cd scripts 
./install_pivariety_pkgs.sh -p libcamera
./install_pivariety_pkgs.sh -p libcamera_apps
```

 - Add <b>dtoverlay=imx519,vcm=off</b> in the end of <b>/boot/config.txt</b>
```
sudo echo " " >> /boot/config.txt
sudo echo "dtoverlay=imx519,vcm=off" >>  /boot/config.txt
```

 - Reboot your raspberry pi.

 - To run the program after installing all dependecies you can go to the project directory and run the code
```
pi@rpi4-32bit:~ $ cd raspberrypicamera/
pi@rpi4-32bit:~/raspberrypicamera $ sudo python3 ./rpi_cam.py 
```

 - To start the program on boot, add the below line to your crontab by running <b> sudo crontab -e </b> after replacing the path with <location> to rpi_cam.py file

```
@reboot cd < location > ; python3 rpi_cam.py
```

## Support
In case of any issue or suggestion you can reach out to raspberry2003pi@gmail.com .

## Roadmap
Currently the code is witten to capture stills and timelapse stills. Menu for the timelapse video feature is added but not yet implemented. In future I will be working on updating and optimizing the code adding below features :
 - Generate Timelapse videos
 - Exposure bracketing
 - Disk space usage - Implemented(18 Sep,2023)
 - Saving existing settings - Implemented(17 Sep,2023)
 - Image playback

## Authors and acknowledgment
```
Author : Praveen Verma
Date   : September 18, 2023
```
Acknowledgement
```
- To write the code for this project I have referred and used the sample codes available online to understand how the hardware works. Below are the codes I referred and used to develop this project :
   - Pimoroni TouchPHAT example code : https://github.com/pimoroni/touch-phat/tree/master/examples
   - Pimoroni Pirate Audio example code : https://github.com/pimoroni/pirate-audio/tree/master/examples
- Fonts used in this project are from the Waveshare LCD interface example - https://www.waveshare.com/w/upload/a/a8/LCD_Module_RPI_code.7z
```
