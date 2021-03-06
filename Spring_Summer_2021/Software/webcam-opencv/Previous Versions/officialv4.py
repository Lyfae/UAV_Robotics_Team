# Official script [officialv4.py]

# Import Libraries
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

from PIL import Image, ImageTk

from _thread import *
import threading

# PORT = 8009
# IP = 127.0.0.1

# GLOBAL VARIABLES
global pX
global pY
global dX
global dY

# Default Variables for Color
l_h = 0 
l_s = 38
l_v = 132
u_h = 255
u_s = 255
u_v = 255

# Default Variables for Position
pX = 0
pY = 0
dX = 0
dY = 0

# Logic Variables
global isFrameBtnPressed
isFrameBtnPressed = False
isFrameOpen = False

global isMaskBtnPressed
isMaskBtnPressed = False
isMaskOpen = False

global isMAlgBtnPressed
isMAlgBtnPressed = False
maskAlg = 0 # Adaptive Threshold Alg by default

global isContourBtnPressed
isContourBtnPressed = False
isContourShowing = False

global isRandBtnPressed
isRandBtnPressed = False
isTargetReached = True

global isTBarBtnPressed
isTBarBtnPressed = False
isTBarOpen = False
firstTimeTrackbar = True

def nothing(f):
    pass

# def saveFile(image):
#     path = 'C:/Users/Chris/Documents/GitHub/UAV_Robotics_Team/Spring 2021/Software/webcam-opencv/data/images'
#     filename = datetime.datetime.now().strftime("%m.%d.%Y_%I.%M.%S%p")
#     cv2.imwrite(os.path.join(path, filename + '.jpg'), image)

def tkinter():
    # TKINTER DEFAULT VARIABLES
    HEIGHT = 900
    WIDTH = 360
    BGCOLOR = '#3BDCED'
    BTCOLOR = '#DCE8E9'

    # INITIALIZATION
    # Creation of the program window (root)
    root = tk.Tk()
    root.resizable(False, False)
    main_canv = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg=BGCOLOR, highlightthickness=0)
    main_canv.pack()

    # GLOBAL VARIABLES
    global pX
    global pY
    global dX
    global dY

    # ICONS (Courtesy of Icons8.com)
    camera_icon = tk.PhotoImage(file='icons\\camera.png')
    frame_icon = tk.PhotoImage(file='icons\\frame.png')
    mask_icon = tk.PhotoImage(file='icons\\switch-maskalg.png')
    contour_icon = tk.PhotoImage(file='icons\\contour.png')
    target_icon = tk.PhotoImage(file='icons\\rand-point.png')
    trackbar_icon = tk.PhotoImage(file='icons\\trackbar.png')
    workflow_icon = tk.PhotoImage(file='icons\\testrun.png')

    # CANVAS
    control_canv = tk.Canvas(main_canv, width=240, height=800, highlightthickness=0, bg=BGCOLOR)   
    control_canv.place(x=60, y=60, anchor='nw') 

    # LABEL
    title = tk.Label(main_canv, text="LabelBot2000", font=('courier new',24,'bold italic'), justify='center', bg=BGCOLOR, fg='#E556E6')
    title.place(relx=0.5,rely=0.085,anchor='center')

    subtitle = tk.Label(main_canv, text="Remote Control", font=('courier new',20,'bold'), justify='center', bg=BGCOLOR, fg='#914FA6')
    subtitle.place(relx=0.5,rely=0.125,anchor='center')

    # BUTTON FUNCTIONS
    def toggleFrame():
        global isFrameBtnPressed
        isFrameBtnPressed = True

    def toggleMask():
        global isMaskBtnPressed
        isMaskBtnPressed = True
        
    def toggleMaskAlg():
        global isMAlgBtnPressed
        isMAlgBtnPressed = True

    def toggleContour():
        global isContourBtnPressed
        isContourBtnPressed = True

    def toggleTrackbar():
        global isTBarBtnPressed
        isTBarBtnPressed = True

    def rndPoint():
        global isRandBtnPressed
        global isFrameOpen
        if isFrameOpen:
            isRandBtnPressed = True
        else:
            print("[WARNING]: Frame is not detected. Please open frame before continuing.")

    # BUTTONS
    display_frame = tk.Button(control_canv, image = camera_icon, command=toggleFrame, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_frame.place(relx=0.5,rely=0.167,anchor='center')
    
    display_mask = tk.Button(control_canv, image = frame_icon, command=toggleMask, justify='center', padx=40, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_mask.place(relx=0.5,rely=0.333,anchor='center')

    change_maskalg = tk.Button(control_canv, image = mask_icon, command=toggleMaskAlg, justify='center', padx=40, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    change_maskalg.place(relx=0.3,rely=0.5,anchor='center')

    display_contour = tk.Button(control_canv, image = contour_icon, command=toggleContour, justify='center', padx=40, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_contour.place(relx=0.7,rely=0.5,anchor='center')

    display_trackbar = tk.Button(control_canv, image = trackbar_icon, command=toggleTrackbar, justify='center', padx=40, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_trackbar.place(relx=0.5,rely=0.667,anchor='center')
    
    rand_point = tk.Button(control_canv, image = target_icon, command=rndPoint, justify='center', padx=40, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    rand_point.place(relx=0.5,rely=0.833,anchor='center')

    exitButton = tk.Button(control_canv, text="EXIT", font=('courier new',18,'bold'), command=exit, justify='center', padx=40, pady=10, bg='#D55C8D', fg='white')
    exitButton.place(relx=0.5,rely=.95,anchor='center')

    # LOOP
    root.mainloop()

# Define webcam used
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Check for compatibility. If not, force search webcam
_, frame = webcam.read()
webcam.set(3, 640)
webcam.set(4, 480)

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

    # Toggle Taskbars
    if isTBarBtnPressed:
        if not isTBarOpen:
            isTBarOpen = True
        else:
            cv2.destroyWindow('Trackbars')
            firstTimeTrackbar = True
            isTBarOpen = False
        isTBarBtnPressed = False
    if isTBarOpen:
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

        # Get the new values of the trackbar in real time as the user changes them
        l_h = cv2.getTrackbarPos("L - H", "Trackbars")
        l_s = cv2.getTrackbarPos("L - S", "Trackbars")
        l_v = cv2.getTrackbarPos("L - V", "Trackbars")
        u_h = cv2.getTrackbarPos("U - H", "Trackbars")
        u_s = cv2.getTrackbarPos("U - S", "Trackbars")
        u_v = cv2.getTrackbarPos("U - V", "Trackbars")

    # Decide on which mask algorithm to use based on button [0 = AdaptiveThreshold, 1 = HSV Color Isolation]
    if isMAlgBtnPressed:
        if maskAlg == 0: maskAlg = 1 
        else: maskAlg = 0 
        isMAlgBtnPressed = False
    if maskAlg == 0:
        mask = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 23, 3)
    else:
        l_range_hsv = np.array([l_h, l_s, l_v])
        u_range_hsv = np.array([u_h, u_s, u_v])
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, l_range_hsv, u_range_hsv)

    # Run contour detection and display if toggled
    if isContourBtnPressed:
        if not isContourShowing:
            isContourShowing = True
        else:
            isContourShowing = False
        isContourBtnPressed = False
    
    if isContourShowing:
        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        # Loop for all contours
        contnum = 0
        # Dictionary for all contour information
        contdict = {}
        for c in contours:
            area = cv2.contourArea(c)
            # Only display contour for those having an area threshold of > 1000
            if area > 1000:
                M = cv2.moments(c)
                try:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                except:
                    print("Contour not found!")
                
                contdict[str(contnum)] = {}
                contdict[str(contnum)]['ID'] = contnum
                contdict[str(contnum)]['area'] = area
                contdict[str(contnum)]['cX'] = cX
                contdict[str(contnum)]['cY'] = cY

                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cX, cY), 7, (0,0,0), -1)
                cv2.putText(frame, "ID: {}".format(contnum), (cX - 23, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
                cv2.putText(frame, "Location: ({}, {})".format(cX, cY), (450, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                contnum += 1        
        # Find smallest contour in dictionary and get its cX and cY value
        tempsize = 123456789
        location = 0
        for i in range(0, contnum):
            local_area = contdict[str(i)]['area']
            if local_area < tempsize:
                location = i
                tempsize = local_area
        cX = contdict[str(location)]['cX']
        cY = contdict[str(location)]['cY']
        # Display number of contours detected
        cv2.putText(frame, "# of contours: {}".format(contnum), (450, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
        cv2.putText(frame, "Currently Tracking ID {}".format(contdict[str(location)]['ID']), (450, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

    # Stop fps counter, calculate, and show fps
    stop = time.time()
    seconds = stop - start
    try:
        fps = 1 / seconds
    except:
        print("FPS Counter attempted to divide by 0!")
    cv2.putText(frame,"FPS: " + str(round(fps,2)), (25,40) ,cv2.FONT_HERSHEY_SIMPLEX, 0.75,(50,200,50),2)

    # Begin Random Point Test
    if isRandBtnPressed:
        if not isTargetReached:
            dX = pX - cX
            dY = pY - cY
            
            cv2.circle(frame, (pX, pY), 7, (0,0,255), -1)
            cv2.putText(frame, "Target", (pX - 23, pY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            cv2.putText(frame, "Target Location: ({}, {})".format(pX, pY), (25, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
            
            print("CONSOLE: \t dX = {} \t dY = {}".format(dX, dY))

            if dX < 25 and dX > -25 and dY < 25 and dY > -25:
                print("Target Successfully Acquired.")
                isTargetReached = True
                isRandBtnPressed = False
                pX = 0
                pY = 0     
        elif isRandBtnPressed == True and isTargetReached == True:
            pX = random.randint(50,600)
            pY = random.randint(50,430)
            isTargetReached = False

    # Toggle Frame
    if isFrameBtnPressed:
        if not isFrameOpen:
            isFrameOpen = True
        else:
            cv2.destroyWindow('Frame')
            isFrameOpen = False
        isFrameBtnPressed = False
    if isFrameOpen: 
        cv2.imshow('Frame', frame)

    # Toggle Mask
    if isMaskBtnPressed:
        if not isMaskOpen:
            isMaskOpen = True
        else:
            cv2.destroyWindow('Mask')
            isMaskOpen = False
        isMaskBtnPressed = False
    if isMaskOpen: cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()