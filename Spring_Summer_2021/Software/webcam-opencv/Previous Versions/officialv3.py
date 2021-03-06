# Official script official.py

import numpy as np
import cv2
import os
import imutils
import time
import datetime
import json

import sys
import socket
import tkinter as tk
import random
import math
#from PIL import Image, ImageTk

from _thread import *
import threading

# PORT = 8009
# IP = 127.0.0.1

# GLOBAL VARIABLES
global pX
global pY
global dX
global dY

global isScFrame
global isScMask
global isPointDetecting
global isState
global isBye
global isBye2
global isBye3

# DEFAULT CONSTRUCTORS
pX = 0
pY = 0
dX = 0
dY = 0

isScFrame = False
isScMask = False
isPointDetecting = False
isState = False
isTargetReached = True
isBye = True
isBye2 = True
isBye3 = True
firstTimeTrackbar = True

def nothing(x):
    pass

def saveFile(image):
    path = 'C:/Users/Chris/Documents/GitHub/UAV_Robotics_Team/Spring 2021/Software/webcam-opencv/data/images'
    filename = datetime.datetime.now().strftime("%m.%d.%Y_%I.%M.%S%p")
    cv2.imwrite(os.path.join(path, filename + '.jpg'), image)

def tkinter():
    # TKINTER DEFAULT VARIABLES
    HEIGHT = 900
    WIDTH = 360

    # INITIALIZATION
    # Creation of the program window (root)
    root = tk.Tk()
    root.resizable(False, False)
    main_canv = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg='black', highlightthickness=0)
    main_canv.pack()

    # GLOBAL VARIABLES
    global pX
    global pY
    global dX
    global dY

    # CANVAS
    control_canv = tk.Canvas(main_canv, width=240, height=800, highlightthickness=0, bg='black')   
    control_canv.place(x=60, y=60, anchor='nw') 

    # LABEL
    title = tk.Label(control_canv, text="ROBOTIS", font=('courier new',24,'bold italic'), justify='center', bg='black', fg='#f46500')
    title.place(relx=0.5,rely=0.05,anchor='center')

    subtitle = tk.Label(control_canv, text="Remote Control", font=('courier new',20,'bold'), justify='center', bg='black', fg='#4d7701')
    subtitle.place(relx=0.5,rely=0.1,anchor='center')

    # point = tk.Label(control_canv, text="Point: ({}, {})".format(pX, pY), font=('courier new',14,'bold'), justify='left', bg='black', fg='#f4f0f4')
    # point.place(relx=0.3,rely=0.65,anchor='center')

    # distanceX = tk.Label(control_canv, text="dX: {}".format(dX), font=('courier new',14,'bold'), justify='left', bg='black', fg='#f4f0f4')
    # distanceX.place(relx=0.115,rely=0.7,anchor='center')

    # distanceY = tk.Label(control_canv, text="dY: {}".format(dY), font=('courier new',14,'bold'), justify='left', bg='black', fg='#f4f0f4')
    # distanceY.place(relx=0.115,rely=0.75,anchor='center')

    # BUTTON FUNCTIONS
    def scFrame():
        global isScFrame
        isScFrame = True

    def scMask():
        global isScMask
        isScMask = True
        
    def rndPoint():
        global isPointDetecting
        isPointDetecting = True

    def changeState():
        global isState
        isState = True
    
    # OFF BUTTONS
    def bye():
        global isBye
        isBye=False

    def bye2():
        global isBye2
        isBye2=False

    def bye3():
        global isBye3
        isBye3=False

    # BUTTONS
    screenshot_frame = tk.Button(control_canv, text="sc frame", font=('courier new',18,'bold'), command=scFrame, justify='center', padx=40, pady=10, bg='black', fg='#9e8d8f')
    screenshot_frame.place(relx=0.5,rely=0.2,anchor='center')

    close_frame=tk.Button(control_canv, text="close frame", font=('courier new',18,'bold'), command=bye, justify='center', padx=20, pady=5, bg='black', fg='#9e8d8f')
    close_frame.place(relx=0.5,rely=0.275,anchor='center')
    
    screenshot_mask = tk.Button(control_canv, text="sc mask", font=('courier new',18,'bold'), command=scMask, justify='center', padx=40, pady=10, bg='black', fg='#9e8d8f')
    screenshot_mask.place(relx=0.5,rely=0.4,anchor='center')

    close_mask=tk.Button(control_canv, text="close mask", font=('courier new',18,'bold'), command=bye2, justify='center', padx=20, pady=5, bg='black', fg='#9e8d8f')
    close_mask.place(relx=0.5,rely=0.475,anchor='center')

    change_state = tk.Button(control_canv, text="--state--", font=('courier new',18,'bold'), command=changeState, justify='center', padx=40, pady=10, bg='black', fg='#9e8d8f')
    change_state.place(relx=0.5,rely=0.6,anchor='center')

    close_state=tk.Button(control_canv, text="close state", font=('courier new',18,'bold'), command=bye3, justify='center', padx=20, pady=5, bg='black', fg='#9e8d8f')
    close_state.place(relx=0.5,rely=0.675,anchor='center')
    
    rand_point = tk.Button(control_canv, text="rand point", font=('courier new',18,'bold'), command=rndPoint, justify='center', padx=40, pady=10, bg='black', fg='#9e8d8f')
    rand_point.place(relx=0.5,rely=0.8,anchor='center')

    exitButton = tk.Button(control_canv, text="EXIT", font=('courier new',18,'bold'), command=exit, justify='center', padx=40, pady=10, bg='black', fg='red')
    exitButton.place(relx=0.5,rely=.95,anchor='center')

    # LOOP
    root.mainloop()

# Define webcam used
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Check for compatibility. If not, force search webcam
_, frame = webcam.read()
# print(frame)
try:
    if frame == None:
        webcam = cv2.VideoCapture(-1)
except:
    print("Webcam Detected First Try.")

# Begin tkinter thread
thread_tk = threading.Thread(target = tkinter)
thread_tk.start()

while(True):
    start = time.time()
    # Grabbing frame from webcam
    _, frame = webcam.read()

    # Apply Grayscale
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blur = cv2.GaussianBlur(grayscale, (9,9), 0)

    # Create Mask/Threshold
    threshold = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 23, 3)

    # Find contours
    contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    
    # Test
    cv2.imshow('test', frame)

    # stop fps counter and calculate + show fps
    stop = time.time()

    seconds = stop - start

    # Calculate frames per second
    fps = 1 / seconds

    # Fps display
    cv2.putText(frame,"FPS: " + str(round(fps,2)), (25,40) ,cv2.FONT_HERSHEY_SIMPLEX, 0.75,(50,200,50),2)

    #swapping into the state
    if isState:
        if firstTimeTrackbar:
            # Create a window named trackbars.
            cv2.namedWindow("Trackbars")

            # Now create 6 trackbars that will control the lower and upper range of 
            # H,S and V channels. The Arguments are like this: Name of trackbar, 
            # window name, range,callback function. For Hue the range is 0-179 and
            # for S,V its 0-255.
            cv2.createTrackbar("L - H", "Trackbars", 0, 179, nothing)
            cv2.createTrackbar("L - S", "Trackbars", 0, 255, nothing)
            cv2.createTrackbar("L - V", "Trackbars", 0, 255, nothing)
            cv2.createTrackbar("U - H", "Trackbars", 179, 179, nothing)
            cv2.createTrackbar("U - S", "Trackbars", 255, 255, nothing)
            cv2.createTrackbar("U - V", "Trackbars", 255, 255, nothing)
            firstTimeTrackbar = False
 
        # Convert the BGR image to HSV image.
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Get the new values of the trackbar in real time as the user changes 
        # them
        l_h = cv2.getTrackbarPos("L - H", "Trackbars")
        l_s = cv2.getTrackbarPos("L - S", "Trackbars")
        l_v = cv2.getTrackbarPos("L - V", "Trackbars")
        u_h = cv2.getTrackbarPos("U - H", "Trackbars")
        u_s = cv2.getTrackbarPos("U - S", "Trackbars")
        u_v = cv2.getTrackbarPos("U - V", "Trackbars")
    
        # Set the lower and upper HSV range according to the value selected
        # by the trackbar
        lower_range = np.array([l_h, l_s, l_v])
        upper_range = np.array([u_h, u_s, u_v])
        
        # Filter the image and get the binary mask, where white represents 
        # your target color
        mask = cv2.inRange(hsv, lower_range, upper_range)
    
        # You can also visualize the real part of the target color (Optional)
        res = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Converting the binary mask to 3 channel image, this is just so 
        # we can stack it with the others
        mask_3 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        
        # stack the mask, orginal frame and the filtered result
        stacked = np.hstack((mask_3,frame,res))
        
        # Show this stacked frame at 40% of the size.
        cv2.imshow('Trackbars',cv2.resize(stacked,None,fx=0.5,fy=0.5))
    if isBye3==False:
        print("Hit3")
        isState = False
        cv2.destroyWindow('Trackbars')
        isBye3 = True
        firstTimeTrackbar = True

    # TKINTER-LINKED CONDITIONALS
    if isPointDetecting == True:
        data = {}
        if not isTargetReached:
            dX = pX - cX
            dY = pY - cY
            
            cv2.circle(frame, (pX, pY), 7, (0,0,255), -1)
            cv2.putText(frame, "Target", (pX - 23, pY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            cv2.putText(frame, "Target Location: ({}, {})".format(pX, pY), (25, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
            
            print("CONSOLE: \t dX = {} \t dY = {}".format(dX, dY))

            if dX < 25 and dX > -25 and dY < 25 and dY > -25:
                print("Target Successfully Aquired.")
                isTargetReached = True
                isPointDetecting = False
                pX = 0
                pY = 0     
        elif isPointDetecting == True and isTargetReached == True:
            pX = random.randint(0,640)
            pY = random.randint(0,480)
            isTargetReached = False

    # Turning on and off the webcam
    if isScFrame == True:
        # Loop for all contours
        contnum = 0
        for c in contours:
            area = cv2.contourArea(c)
            # Only display contour for those having an area threshold of > 1000
            if area > 1000:
                contnum += 1
                M = cv2.moments(c)
                try:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                except:
                    print("Contour not found!")

                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cX, cY), 7, (0,0,0), -1)
                cv2.putText(frame, "center", (cX - 23, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
                cv2.putText(frame, "Location: ({}, {})".format(cX, cY), (450, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            
            # Display number of contours detected
            cv2.putText(frame, "# of contours: {}".format(contnum), (450, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        
        cv2.imshow('webcam', frame)
    if isBye == False:
        print("hit1")
        isScFrame = False
        cv2.destroyWindow('webcam')
        isBye=True    

    # Turning on and off the mask
    if isScMask == True:
        cv2.imshow('mask', threshold)
    if isBye2 == False:
        print("hit2")
        isScMask = False
        cv2.destroyWindow('mask')
        isBye2=True     

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()