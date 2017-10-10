# QR-code-recognition
QR code recognition and following using Raspberry Pi and SimpleCV

This project implements QR code recognition and following utilizing the hardware abilities of Raspberry Pi 3 and Python 2.7. 
The image recognition is done thanks to SimpleCV library, for image processing, while the following of the QR code is done by a vehicle, controlled by Raspberry Pi.

The time of vehicle movement depends on the destination of the QR code from the Picamera and (unfortunately) from constant numbers, which result from testing and battery voltage amount. So as long as there is no implementation to continuously measure and input the voltage level inside the code we rely on constants.

Below is the schematic of the vehicle
![alt text](https://raw.githubusercontent.com/hlkyt/QR-code-recognition/master/img/Raspberry_fritig_2.png)

Note: There will be updates with comments and optimization in the code.

