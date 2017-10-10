# -*- coding: utf-8 -*-
import time
import picamera
import math
import threading
from SimpleCV import *
import RPi.GPIO as GPIO

rwheelback = 16
rwheelfor= 18
lwheelback = 13
lwheelfor = 15


GPIO.setmode(GPIO.BOARD)
GPIO.cleanup()

GPIO.setup(22,GPIO.OUT)
p=GPIO.PWM(22,50)
CycleValue=0
p.start(3.5)
p.ChangeDutyCycle(7.5)
tries=0
flag=0
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

#saving captured images from stream
def filenames(lock):
        print('Waiting for lock')
        lock.acquire()
        try:
            print('Acquired lock')
            yield 'image.jpg'
            print("True")
        finally:
            lock.release()
            print("released")
        time.sleep(0.3)

#Image capturing with 604x480 resolution and 30 fps
def capture(lock):
    with picamera.PiCamera(resolution=(640,480), framerate=30) as camera:
        camera.start_preview()
        time.sleep(1)
        start = time.time()
        camera.capture_sequence(filenames(lock), use_video_port=True)
        finish = time.time()

#function for acquiring thread and passing it to processing function
def acquire(lock):
    num_tries = 0
    num_acquires = 0
    logging.debug('Trying to acquire')
    have_it = lock.acquire()
    try:
        num_tries += 1
        if have_it:
            logging.debug('Iteration %d: Acquired',  num_tries)
            s=time.time()
            processing()
            print("Third function time",(time.time()-s))
            num_acquires += 1
        else:
            logging.debug('Iteration %d: Not acquired', num_tries)
    finally:
        if have_it:
            lock.release()
            time.sleep(1)
    logging.debug('Done after %d iterations', num_tries)

#function for image processing,qr code recognition and following
def processing():
    delay=0
    delayt=0
    indelay=0
    global flag
    global tries
    global CycleValue
    global p
    ok=0

    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(rwheelback,GPIO.OUT)
        GPIO.setup(rwheelfor,GPIO.OUT)
        GPIO.setup(lwheelfor,GPIO.OUT)
        GPIO.setup(lwheelback,GPIO.OUT)
        GPIO.setup(22,GPIO.OUT)
        try:
            if(Image("image.jpg")):
                im=Image("image.jpg")
                print("Got an image!")
                if(im.findBarcode()):
                    bar=im.findBarcode()
                    for i in range(len(bar)):
                        #Here we check the data below with the one the QR code has
                        if(bar[i].data=="https://weather.com"):
                            center=bar.center()
                            center=center[0][0]
                            center_im=im.width/2
                            bound=im.width
                            area=bar.area()
                            if(area<(0.05*im.area())):
                                delay=(im.area()/area)*0.02
                                delayt=delay/10
                            elif(area>(25/100*im.area())  and area<(im.area())):
                                delay=(im.area()/area)*0.1
                                delayt=delay/15
                            else:
                                delay=0
                                delayt=0
                            print "Delay", delay
                            print "Image area: ", im.area()
                            print "Barcode area: ", area
                            print "Center is: ", center
                            print "Bound is: ", bound
                            print("\n")
                            if(flag==1):
                                if((CycleValue>9 and CycleValue<10)or (CycleValue<6 and CycleValue>5)):
                                    indelay=0.35
                                    if(center<((40*bound)/100) ):
                                        indelay=0.5
                                    elif(center>((60*bound)/100)):
                                        indelay=0.5
                                elif(CycleValue>11 or CycleValue<4):
                                    indelay=0.8
                                delayt=indelay*delay*0.65

                            print "Turn delay", delayt
                            print "CycleValue: ",CycleValue
                            ok=0
                            if((CycleValue==7.5 and flag==1) or (flag==0 and center>=((40*bound)/100) and center<=((60*bound)/100))):
                                if(area>(im.area()*15/100) and area<(im.area())):
                                    print("Going back!")
                                    GPIO.output(rwheelback,GPIO.HIGH)
                                    GPIO.output(lwheelback,GPIO.HIGH)
                                    time.sleep(delay)
                                    GPIO.output(rwheelback,GPIO.LOW)
                                    GPIO.output(lwheelback,GPIO.LOW)
                                elif(area<(im.area()*5/100)):
                                    print("Going forward!")
                                    GPIO.output(rwheelfor,GPIO.HIGH)
                                    GPIO.output(lwheelfor,GPIO.HIGH)
                                    time.sleep(delay)
                                    GPIO.output(rwheelfor,GPIO.LOW)
                                    GPIO.output(lwheelfor,GPIO.LOW)
                                else:
                                    print "It's fine"

                            elif((CycleValue>9 and CycleValue<20 and flag==1) or (center<((40*bound)/100) and flag==0)):
                                flag=0
                                if(area>(im.area()*15/100) and area<(im.area())):
                                    print ("Back Right")
                                    GPIO.output(lwheelback,GPIO.HIGH)
                                    time.sleep(delayt)
                                    GPIO.output(lwheelback,GPIO.LOW)
                                elif(area<(im.area()*5/100)):
                                    print("Going Left!")
                                    GPIO.output(rwheelfor,GPIO.HIGH)
                                    time.sleep(delayt)
                                    GPIO.output(rwheelfor,GPIO.LOW)
                                else:
                                    print("It's fine.")
                                    ok=1
                            elif((CycleValue<6 and CycleValue>0 and flag==1) or (center>((60*bound)/100) and flag==0)):
                                flag=0
                                if(area>(im.area()*15/100) and area<(im.area())):
                                    print ("Back Left")
                                    GPIO.output(rwheelback,GPIO.HIGH)
                                    time.sleep(delayt)
                                    GPIO.output(rwheelback,GPIO.LOW)
                                elif(area<(im.area()*5/100)):
                                    print("Going Right!")
                                    GPIO.output(lwheelfor,GPIO.HIGH)
                                    time.sleep(delayt)
                                    GPIO.output(lwheelfor,GPIO.LOW)
                                else:
                                    print("It's fine.")
                                    ok=1
                            time.sleep(0.1)
                            if(ok==1 and CycleValue>0 and CycleValue<12):
                                p.ChangeDutyCycle(CycleValue)
                                flag=1
                            elif(ok==0 and CycleValue>0 and CycleValue<12 and (CycleValue<7.5 or CycleValue>7.5)):
                                if(center<((30*bound/100))):
                                    if(CycleValue>7.5 and CycleValue<12):
                                        CycleValue=CycleValue-2
                                    elif(CycleValue<7.5 and CycleValue>0):
                                        CycleValue=CycleValue+2
                                elif(center>((70*bound)/100)):
                                    if(CycleValue>7.5 and CycleValue<12):
                                        CycleValue=CycleValue-2
                                    elif(CycleValue<7.5 and CycleValue>0):
                                        CycleValue=CycleValue+2
                                p.ChangeDutyCycle(CycleValue)
                                flag=1
                            elif(ok==0 and (CycleValue==0 or CycleValue==7.5)):
                                p.ChangeDutyCycle(7.5)
                                flag=0
                            tries=0
                            print("\n")


                else:

                    print ("Nothing found. Looking around...")
                    tries=tries+1
                    print tries
                    if(tries>=5):
                        tries=0
                        if(CycleValue==0):
                            CycleValue=1.5
                            p.start(CycleValue)
                        flag=1
                        CycleValue = CycleValue+2
                        if(CycleValue>12):
                            print("Nothing to be found!")
                            CycleValue=0
                            p.ChangeDutyCycle(7.5)
                        elif(CycleValue>1 and CycleValue<12):
                            p.ChangeDutyCycle(CycleValue)
                            print "Val:", CycleValue
                            time.sleep(1)
        except IOError:
            print("No image file to open")
        if(GPIO.setmode()):
            print("True")
            GPIO.cleanup()
        else:
            print("No setmode!")
    except:
        print("No setmode trying again")

if __name__ == '__main__':

    lock=threading.Lock()
    while True:
        t = threading.Thread(target=first,args=(lock,))
        t.start()
        time.sleep(2)
        t1= threading.Thread(target=second,args=(lock,))
        t1.start()
