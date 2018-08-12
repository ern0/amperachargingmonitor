# Ampera Charging Monitor

*Visual monitoring of EV charging (Opel Ampera), using a Raspberry Pi with a webcam and an old Android phone*

## Disclaimer

I made this installation for myself, so probably you can't use it out-of box, but it has an open architechture, so it's easy to modify or tweak.

## The problem

Opel Ampera (aka. Vauxhall Ampera, Chevrolet Volt etc.) is an early EV with no  quickcharger. You can charge it from the wallet, it takes 5-6 hours with 10A, or 8-10 hours with 6A.

What I want is simple: check the status of charging remotely. 

## The solution

I have no ODB2 interface (yet), and AFAIK it works only when the car is tudned on. Anyway, if it works when the car is turned off, I don't really want to use it, I think, it's a huge secutiry hole.

Fortunately, there is a led indicator in the middle of the front window. After plugging the charging cord, it turns to yellow for a while, and if there's no error, it turns constant green during charging, then flashing green, when the car is fully charged.

The wall charger also has some leds. They light green if everything is okay, or flashing red, if there's some error.

The car led blinks quickly, it's not enough to make a still image and analyze it. So there is a Raspberry Pi and a cheap webcam for checking it, by taking a short video, then process it. For charger leds, an old Android phone is used with a IP webcam app, Raspberry Pi can request photos periodically from it, and process them.

## The installation

### Raspberry Pi

- Install Raspbian
- Enable SSH service by creating an empty file called *ssh* in the root of boot partition
- Connect the Raspberry Pi to your network by cable or wifi. If it has no on-board wifi, buy a cheap USB dongle
- If you're using wifi, configure your Raspberry Pi to automatically connect your AP
- Configure your DHCP server (usually, it's your router) to assign static IP address
- Install *ffmpeg* by *sudo apt install -y ffmpeg*
- Plug the cam, it should appear as */dev/video0*
- Install this stuff

### Webcam

You can use a real webcam, but the cheapest solution s to use some old Android device for it:
- Downloar IP Cam app: https://play.google.com/store/apps/details?id=com.pas.webcam
- In the app's settings, set up autostart
- Configure your DHCP server (usually, it's your router) to assign static IP address to the device.
