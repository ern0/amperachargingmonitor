# Ampera Charging Monitor

*Visual monitoring of EV charging (Opel Ampera), using a Raspberry Pi with a webcam and an old Android phone*

## Purpose

I made this installation for myself, so probably you can't use it out-of box, but it has an open architechture, so it's easy to modify or tweak.

Other hand, I made this project for educational purposes, the program code is optimized for reading, not for speed.

Even if you can't understand the program 100%, you can understand the steps of the image processing procerure.


## The problem

Opel Ampera (aka. Vauxhall Ampera, Chevrolet Volt etc.) is an early EV with no  quickcharger. You can charge it from the wallet, it takes 5-6 hours with 10A, or 8-10 hours with 6A.

What I want is simple: check the status of charging remotely. 


## The solution

I have no ODB2 interface (yet), and AFAIK it works only when the car is tudned on. Anyway, if it works when the car is turned off, I don't really want to use it, I think, it's a huge secutiry hole.

Fortunately, there is a led indicator in the middle of the front window. After plugging the charging cord, it turns to yellow for a while, and if there's no error, it turns constant green during charging, then flashing green, when the car is fully charged.

The wall charger also has some leds. They light green if everything is okay, or flashing red, if there's some error.

The car led blinks quickly, it's not enough to make a still image and analyze it. So there is a Raspberry Pi and a cheap webcam for checking it, by taking a short video, then process it. For charger leds, an old Android phone is used with a IP webcam app, Raspberry Pi can request photos periodically from it, and process them.


## Artifical constraints

As mentioned, it's an educational project. I hope it's useful for ones interested in image processing basics, but first of all, it was a good lesson for myself. I was familiar with image processing basics, but I've never used this knowledge "on the field".

So I laid down some general rules for the architecture:

- Use Python3. Programs written in C/C++ are faster, but Python is better choice for rewriting steps 3-4 times (as happened), and also it's easier to read.
- Don't use image processing library, like OpenCV. I want to write every pixel operation myself, even if it's 100 times slower.
- Don't use machine learning, I want to know exactly what happening. The characteristics of the feature is very simple: it's green, light, cca. 3x3 pixels, and surrounded by darknkess.
- Don't analyze video, only still images: don't find the position of the green spot on a frame, then use this information when processing other frames.
- Use lo-res, bad quality images (that was given, thanks to my $10 camera).
- Don't crop image, let the program work on the full picture, which contains various objects appears on the scene. (Later I broke this rule for gaining some speed.)


## The installation

### Raspberry Pi

- Install Raspbian
- Enable SSH service by creating an empty file called *ssh* in the root of boot partition
- Connect the Raspberry Pi to your network by cable or wifi. If it has no on-board wifi, buy a cheap USB dongle
- If you're using wifi, configure your Raspberry Pi to automatically connect your AP
- Configure your DHCP server (usually, it's your router) to assign static IP address
- Install *ffmpeg* by *sudo apt install -y ffmpeg*
- Plug the cam, it should appear as */dev/video0*
- Create a RAM disk avoid using SD card frequently, create a directory */mnt/ram*, then in */etc/fstab* add *tmpfs /mnt/ram tmpfs*
- Install this stuff

- sudo apt install python3-pil

### Webcam

You can use a real webcam, but the cheapest solution s to use some old Android device for it:
- Downloar IP Cam app: https://play.google.com/store/apps/details?id=com.pas.webcam
- In the app's settings, set up autostart
- Configure your DHCP server (usually, it's your router) to assign static IP address to the device.
