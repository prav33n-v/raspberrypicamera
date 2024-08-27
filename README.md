# RaspberryPiCamera

## Description
This is a project to make a Infrared light sensitive point and shoot camera using Raspberry Pi, microSD card, usb card reader, SPI display, a few switches and ofcourse a camera module (for my build I have used Arducam 16MP NoIR Camera).

## OS Installation
At the time of building this project, I have used Raspbian Pi OS (32bit) distro.

```
  pi@rpi-camera:~ $ cat /etc/*release
  PRETTY_NAME="Raspbian GNU/Linux 12 (bookworm)"
  NAME="Raspbian GNU/Linux"
  VERSION_ID="12"
  VERSION="12 (bookworm)"
  VERSION_CODENAME=bookworm
  ID=raspbian
  ID_LIKE=debian
  HOME_URL="http://www.raspbian.org/"
  SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
  BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"
```

### Initial Software setup
 -  Configuring raspberry pi by running
```
sudo raspi-config
```
 -  Enable the following and save the settings :
    -  Enable legacy camera support
    -  Enable SPI/I2C/1Wire
    -  Expand Filesystem

 -  Reboot after the changes are done. After reboot update your Raspberry Pi by running below commands one by one :
```
sudo apt update
sudo apt upgrade
sudo apt autoremove
```

### Storage Setup
If you want to setup the camera to store the images in an external storage (I used microSD card), you can setup the raspberry pi to automatically mount it to a specific path. Follow the below steps for the same :

 -  Plug in the storage device and list the devices on your Raspberry Pi running command <b>lsblk -fp</b>
```
  pi@rpi-camera:~ $ lsblk -fp
  NAME             FSTYPE FSVER LABEL  UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
  /dev/sda                                                                                 
  └─/dev/sda1      vfat   FAT32 SD32GB 6439-B4D1                              28.2G     5% /media/pi
  /dev/mmcblk0                                                                             
  ├─/dev/mmcblk0p1 vfat   FAT32 bootfs AAE0-77E1                             394.6M    23% /boot/firmware
  └─/dev/mmcblk0p2 ext4   1.0   rootfs ca2be9ef-61a4-4400-a5a1-dc17d7ea790d   23.6G    13% /
```
 -  If you want to mount card with label SD32GB (above) then run <b>sudo blkid /dev/sda1</b>
```
  pi@rpi-camera:~ $ sudo blkid /dev/sda1
  /dev/sda1: LABEL_FATBOOT="SD32GB" LABEL="SD32GB" UUID="6439-B4D1" BLOCK_SIZE="512" TYPE="vfat" PARTUUID="dec9100f-0771-43f2-ab9f-e0866e25869f"
  pi@rpi-camera:~ $
```
 -  Create a directory where you want to mount the storage device.
```
  pi@rpi-camera:~ $ sudo mkdir /mnt/data
  pi@rpi-camera:~ $ sudo chown pi:pi /mnt/data
  pi@rpi-camera:~ $ sudo chmod 777 /mnt/
```
 -  Add below line to /etc/fstab file using <b>sudo nano /etc/fstab</b>
```
/dev/sda1 /mnt/data vfat auto,nofail,noatime,rw,users,uid=1000,gid=1000 0 0
```
 -  Reboot your Raspberry Pi and check if device is mounted on your desired location by running <b>df -h</b>. As shown in below result /dev/sda1 is mounted on path /mnt/data
```
  pi@rpi-camera:~ $ df -h
  Filesystem      Size  Used Avail Use% Mounted on
  udev            325M     0  325M   0% /dev
  tmpfs            93M  2.1M   91M   3% /run
  /dev/mmcblk0p2   29G  3.7G   24G  14% /
  tmpfs           461M     0  461M   0% /dev/shm
  tmpfs           5.0M   12K  5.0M   1% /run/lock
  /dev/mmcblk0p1  510M  116M  395M  23% /boot/firmware
  /dev/sda1        30G  1.5G   29G   5% /mnt/data
  tmpfs            93M   36K   93M   1% /run/user/1000
  pi@rpi-camera:~ $ 
```
 - Create a directory for storing images in your storage device
```
mkdir /mnt/data/rpi-camera
```

### Samba Fileshare Setup
If you want to access the images stored on your rpi-camera directly via any devices connect to same network as Raspberry Pi the you can follow below steps :

 - Install samba
```
sudo apt install samba samba-common-bin
```
 - Configure samba fileshare by appending the below lines to /etc/samba/smb.conf . Please note that I have set value of writable, browsable and public as yes as I am not having any highly secure data here. You can change this parameters as per your need/requirement
```
[rpi-camera]
  path = /mnt/data/rpi-camera
  writable = yes
  browsable = yes
  public = yes
```
 - Setup a user to access your Samba share by running below command (sudo smbpasswd -a <USERNAME>) and then setup password for the same
```
sudo smbpasswd -a pi
```
 - Restart Samba services
```
sudo systemctl restart smbd
```

### Run scripts for Arducam 16MP NoIR Camera module

If you are using any other camera module then you do not need to run <b>install_pivariety_pkgs.sh</b>. If you are using the mentioned camera module then you can installl the same by following up the instructions from camera module manufacturer.
 - I have used a camera module with Sony IMX519 sensor for which documentation is availabe at https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/5MP-OV5647/
```
chmod +x ./install_pivariety_pkgs.sh
./install_pivariety_pkgs.sh -p libcamera_dev
./install_pivariety_pkgs.sh -p libcamera_apps
```

 - Add <b>dtoverlay=imx519</b> in the end of <b>/boot/firmware/config.txt</b> by switching to root user <b>sudo su</b> and executing below commands
```
echo " " >> /boot/firmware/config.txt
echo "dtoverlay=imx519" >>  /boot/firmware/config.txt
```

 - Reboot your raspberry pi.
 - Once your camera is connected correctly, run command <b>libcamera-still -o test.jpeg</b> to check if you are able to capture image. 

### Install required dependencies
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
Currently the code is witten to capture single Photo,Exposure Bracketing mode and Interval Timer shooting mode. Menu for the Timelapse Movie feature is added but not yet implemented. In future updates the below features will be added :
 - Generate Timelapse movies
 - Image playback

## Authors and acknowledgment
```
Author : Praveen Verma
Date   : August 27, 2024
```
Acknowledgement
```
- To write the code for this project I have referred and used the sample codes available online to understand how the hardware works. Below are the codes I referred and used to develop this project :
   - Pimoroni TouchPHAT example code : https://github.com/pimoroni/touch-phat/tree/master/examples
   - Pimoroni Pirate Audio example code : https://github.com/pimoroni/pirate-audio/tree/master/examples
- Fonts used in this project are from the Waveshare LCD interface example - https://www.waveshare.com/w/upload/a/a8/LCD_Module_RPI_code.7z
```
