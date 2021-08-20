# Official script [officialv6.py]
# WORKING VERSION WITH [serverv3.py]
VERSION = 'HsController.py'

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
from tkinter import *
import random
import math

from PIL import Image, ImageTk

from _thread import *
import threading

import calibration

if len(sys.argv) != 2:
    print("Usage: python3 HsController.py <hostID>")
    sys.exit(1)

HOST = sys.argv[1]
PORT = 8009

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# GLOBAL VARIABLES
global pX
global pY
global dX
global dY

# Default Variables for Color
l_h = 8
l_s = 0
l_v = 0
u_h = 19
u_s = 255
u_v = 153

# Default Variables for Position
pX = 0
pY = 0
dX = 0
dY = 0

# Logic Variables
global isFrameBtnPressed
isFrameBtnPressed = False
isFrameOpen = False

global isFrameRcdBtnPressed
isFrameRcdBtnPressed = False

global isMaskBtnPressed
isMaskBtnPressed = False
isMaskOpen = False

global isMaskRcdButtonPressed
isMaskRcdButtonPressed = False

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

global isCalibrateBtnPressed
isCalibrateBtnPressed = False
isCalibrateStateReached = False
firstTimeHomography = True

global isSendPacketBtnPressed
isSendPacketBtnPressed = False

global frameReq
global maskReq
global contourReq    

#initialize the variables to false
frameReq = False
maskReq = False
contourReq = False

# Conversion Variables
global MmtoPixelRatio
MmtoPixelRatio = 1.1
global H

def nothing(f):
    pass

def saveFile(image, typeI):
    path = 'data/images/'
    filename = typeI + "_" + datetime.datetime.now().strftime("%m.%d.%Y_%I.%M.%S%p")
    cv2.imwrite(path + filename + '.jpg', image)

def findArucoMarkers(img, markerSize, totalMarkers, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(cv2.aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = cv2.aruco.Dictionary_get(key)
    arucoParam = cv2.aruco.DetectorParameters_create()
    corners, ids, rejected = cv2.aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
    return corners, ids

def sendToServerAsync(connOut, data, cX, cY, QcX, QcY):
    print("Sending Packet...")
    connOut.sendall(bytes(json.dumps(data), encoding='utf-8'))
    data_recv = connOut.recv(8162).decode('utf-8')
    print(f"cX = {cX}, cY = {cY}")
    print(f"QcX = {QcX}, QcY = {QcY}")
    print(f"Sent: {data}")
    print(f"Recieved: {data_recv}")
    print("Packet Successfully Sent + Recovered!")

def tkinter():
    # TKINTER DEFAULT VARIABLES
    HEIGHT = 900
    WIDTH = 500
    BGCOLOR = '#003300'
    BTCOLOR = 'black'
    TITLECOLOR = '#FF0000'
    SUBTITLECOLOR = '#914FA6'
    BTNLABELCOLOR = 'white'
    BTNLABELCOLORACTIVE = '#3fb559'
    BTNLABELCOLORINACTIVE = '#cf483c'
    REFRESH_RATE = 50

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
    global rndpt_start
    rndpt_start = 0

    # REQUIREMENT VARIABLES
    global frameReq
    global maskReq
    global contourReq    

    # ICONS (Courtesy of Icons8.com)
    camera_icon = tk.PhotoImage(file='icons/one.png')
    frame_icon = tk.PhotoImage(file='icons/two.png')
    #record_icon = tk.PhotoImage(file='icons/three.png')
    mask_icon = tk.PhotoImage(file='icons/three.png')
    contour_icon = tk.PhotoImage(file='icons/four.png')
    trackbar_icon = tk.PhotoImage(file='icons/five.png')
    target_icon = tk.PhotoImage(file='icons/six.png')
    testrun_icon = tk.PhotoImage(file='icons/seven.png')
    pinpoint_icon = tk.PhotoImage(file='icons/eight.png')

    # CANVAS
    control_canv = tk.Canvas(main_canv, width=350, height=150, highlightthickness=0, bg=BGCOLOR)   
    control_canv.place(x=75, y=160, anchor='nw')

    contour_canv = tk.Canvas(main_canv, width=350, height=150, highlightthickness=0, bg=BGCOLOR)   
    contour_canv.place(x=75, y=310, anchor='nw')

    calibration_canv = tk.Canvas(main_canv, width=350, height=150, highlightthickness=0, bg=BGCOLOR)   
    calibration_canv.place(x=75, y=460, anchor='nw')

    testing_canv = tk.Canvas(main_canv, width=350, height=150, highlightthickness=0, bg=BGCOLOR)   
    testing_canv.place(x=75, y=610, anchor='nw')

    # LABEL
    title = tk.Label(main_canv, text="LabelBot2000", font=('courier new',24,'bold italic'), justify='center', bg=BGCOLOR, fg=TITLECOLOR)
    title.place(relx=0.5,rely=0.065,anchor='center')

    subtitle = tk.Label(main_canv, text= "Controller", font=('courier new',20,'bold'), justify='center', bg=BGCOLOR, fg='#FF6633')
    subtitle.place(relx=0.5,rely=0.100,anchor='center')

    subtitle2 = tk.Label(main_canv, text="Click on the Buttons in Order\nto see what they do!", font=('courier new',20,'bold'), justify='center', bg=BGCOLOR, fg='#66FFFF')
    subtitle2.place(relx=0.5,rely=0.15,anchor='center')

    # control_title = tk.Label(control_canv, text="Control Center", font=('courier new',20,'bold'), justify='center', bg=BGCOLOR, fg=TITLECOLOR)
    # control_title.place(relx=0.5,rely=0.1,anchor='center')

    # control_subtitle = tk.Label(control_canv, text="Frame and Mask Display", font=('courier new',12,'bold'), justify='center', bg=BGCOLOR, fg=SUBTITLECOLOR)
    # control_subtitle.place(relx=0.5,rely=0.145,anchor='center')

    # contour_title = tk.Label(contour_canv, text="Contour Toggle", font=('courier new',20,'bold'), justify='center', bg=BGCOLOR, fg=TITLECOLOR)
    # contour_title.place(relx=0.5,rely=0.1,anchor='center')

    # contour_subtitle = tk.Label(contour_canv, text="Detection Methods", font=('courier new',12,'bold'), justify='center', bg=BGCOLOR, fg=SUBTITLECOLOR)
    # contour_subtitle.place(relx=0.5,rely=0.145,anchor='center')

    # calibration_title = tk.Label(calibration_canv, text="Calibration", font=('courier new',20,'bold'), justify='center', bg=BGCOLOR, fg=TITLECOLOR)
    # calibration_title.place(relx=0.5,rely=0.1,anchor='center')

    # calibration_subtitle = tk.Label(calibration_canv, text="Situational Accommodation", font=('courier new',12,'bold'), justify='center', bg=BGCOLOR, fg=SUBTITLECOLOR)
    # calibration_subtitle.place(relx=0.5,rely=0.145,anchor='center')

    # testing_title = tk.Label(testing_canv, text="Testing", font=('courier new',20,'bold'), justify='center', bg=BGCOLOR, fg=TITLECOLOR)
    # testing_title.place(relx=0.5,rely=0.1,anchor='center')

    # testing_subtitle = tk.Label(testing_canv, text="Data & Results", font=('courier new',12,'bold'), justify='center', bg=BGCOLOR, fg=SUBTITLECOLOR)
    # testing_subtitle.place(relx=0.5,rely=0.145,anchor='center')

    # BUTTON LABELS
    frame_label = tk.Label(control_canv, text="Display Frame", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    frame_label.place(relx=0.3,rely=0.35,anchor='w')

    # rec_frame_label = tk.Label(control_canv, text="Screenshot Frame", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    # rec_frame_label.place(relx=0.35,rely=0.4,anchor='w')

    mask_label = tk.Label(control_canv, text="Display Mask", font=('courier new',12,'bold'), justify='right', bg=BGCOLOR, fg=BTNLABELCOLOR)
    mask_label.place(relx=0.35,rely=0.7,anchor='w')

    # rec_frame_label = tk.Label(control_canv, text="Screenshot Mask", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    # rec_frame_label.place(relx=0.35,rely=0.7,anchor='w')

    mask_alg_label = tk.Label(contour_canv, text="Detection Algorithm\nAdaptive/HSV", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    mask_alg_label.place(relx=0.3,rely=0.35,anchor='w')

    contour_label = tk.Label(contour_canv, text="Toggle Contour", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    contour_label.place(relx=0.3,rely=0.7,anchor='w')

    calib_hsv_label = tk.Label(calibration_canv, text="HSV Trackbars", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    calib_hsv_label.place(relx=0.3,rely=0.35,anchor='w')

    homography_label = tk.Label(calibration_canv, text="Homography Alg.", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    homography_label.place(relx=0.3,rely=0.7,anchor='w')

    rpt_label = tk.Label(testing_canv, text="Home Arm", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    rpt_label.place(relx=0.3,rely=0.35,anchor='w')

    send_packet_label = tk.Label(testing_canv, text="Send Test Packet", font=('courier new',12,'bold'), justify='left', bg=BGCOLOR, fg=BTNLABELCOLOR)
    send_packet_label.place(relx=0.25,rely=0.7,anchor='w')

    # BUTTON REQUIRED WARNING FUNCTION
    def warning(label):
        for x in range (0,3):
            label['fg'] = BTNLABELCOLORINACTIVE
            time.sleep(0.25)
            label['fg'] = BTNLABELCOLOR
            time.sleep(0.25)
            print("What")

    # BUTTON FUNCTIONS
    def toggleFrame():
        global isFrameBtnPressed
        isFrameBtnPressed = True

    def scFrame():
        global isFrameRcdBtnPressed
        global isFrameOpen
        if isFrameOpen:
            isFrameRcdBtnPressed = True
        else:
            print("[WARNING]: Frame is not detected. Please open frame before continuing.")

    def toggleMask():
        global isMaskBtnPressed
        isMaskBtnPressed = True

    def scMask():
        global isMaskRcdButtonPressed
        global isMaskOpen
        if isMaskOpen:
            isMaskRcdButtonPressed = True
        else:
            print("[WARNING]: Mask is not detected. Please open frame before continuing.")

    def toggleMaskAlg():
        global isMAlgBtnPressed
        global isMaskOpen
        global maskReq
        if isMaskOpen:
            isMAlgBtnPressed = True
        else:
            maskReq = True
            print("[WARNING]: No changes are shown. Please open mask to use this button!")

    def toggleContour():
        global isContourBtnPressed
        global isFrameOpen
        global frameReq
        if isFrameOpen:
            isContourBtnPressed = True
        else:
            frameReq = True
            print("[WARNING]: No changes are shown. Please open frame to use this button!")

    def toggleTrackbar():
        global isTBarBtnPressed
        global isMaskOpen
        global isFrameOpen
        global frameReq
        global maskReq
        if isMaskOpen and isFrameOpen:
            isTBarBtnPressed = True
        else:
            maskReq = True
            frameReq = True
            print("[WARNING]: The trackbar option is currently disabled. Please open frame and mask to use this button!")

    def rndPoint():
        global isRandBtnPressed
        global isFrameOpen
        global isContourShowing
        global frameReq
        global maskReq
        if isFrameOpen:
            isRandBtnPressed = True
        else:
            frameReq = True
            print("[WARNING]: Frame not detected. Please open frame before continuing.")

    def sndPacket():
        global isRandBtnPressed
        global isFrameOpen
        global isContourShowing
        global isSendPacketBtnPressed
        global frameReq
        global contourReq
        if isFrameOpen and isContourShowing:
            isSendPacketBtnPressed = True
        else:
            frameReq = True
            contourReq = True
            print("[WARNING]: Frame or Contours are not detected. Please open frame/contours before continuing.")

    def calibrate():
        global isCalibrateBtnPressed
        global isFrameOpen
        global isMaskOpen
        global isContourShowing
        global maskReq
        global frameReq
        if not isMaskOpen and isFrameOpen:
            isCalibrateBtnPressed = True
        else:
            maskReq = True
            frameReq = True
            print("[WARNING]: Please close mask and open frame before continuing.")

    # BUTTON DECLARATIONS
    # Control Buttons
    display_frame = tk.Button(control_canv, image = camera_icon, command=toggleFrame, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_frame.place(relx=0.15,rely=0.35,anchor='center')
    
    # sc_frame = tk.Button(control_canv, image = record_icon, command=scFrame, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    # sc_frame.place(relx=0.2,rely=0.4,anchor='center')

    display_mask = tk.Button(control_canv, image = frame_icon, command=toggleMask, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_mask.place(relx=.85,rely=0.7,anchor='center')

    # sc_mask = tk.Button(control_canv, image = record_icon, command=scMask, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    # sc_mask.place(relx=0.2,rely=0.7,anchor='center')

    # Contour Buttons
    change_maskalg = tk.Button(contour_canv, image = mask_icon, command=toggleMaskAlg, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    change_maskalg.place(relx=0.15,rely=0.35,anchor='center')

    display_contour = tk.Button(contour_canv, image = contour_icon, command=toggleContour, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_contour.place(relx=0.85,rely=0.7,anchor='center')

    # Calibration Buttons
    display_trackbar = tk.Button(calibration_canv, image = trackbar_icon, command=toggleTrackbar, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    display_trackbar.place(relx=0.15,rely=0.35,anchor='center')
    
    calibratebtn = tk.Button(calibration_canv, image = target_icon, command=calibrate, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    calibratebtn.place(relx=0.85,rely=0.7,anchor='center')

    # Testing Buttons
    rand_point = tk.Button(testing_canv, image = testrun_icon, command=rndPoint, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    rand_point.place(relx=0.15,rely=0.35,anchor='center')

    send_packet = tk.Button(testing_canv, image = pinpoint_icon, command=sndPacket, justify='center', padx=10, pady=10, bg=BTCOLOR, fg='#9e8d8f')
    send_packet.place(relx=0.85,rely=0.7,anchor='center')

    # Exit Button
    exitButton = tk.Button(main_canv, text="EXIT", font=('courier new',18,'bold'), command=exit, justify='center', padx=40, pady=10, bg='red', fg='white')
    exitButton.place(relx=0.5,rely=.885,anchor='center')

        # UPDATE FUNCTION
    def updateData():
        # Recursive function to update values.
        global isFrameOpen
        global isMaskOpen
        global isContourShowing
        global isSendPacketBtnPressed
        global frameReq 
        global maskReq 
        global contourReq

        if isFrameOpen: 
            frame_label['fg'] = BTNLABELCOLORACTIVE
            frameReq = False
        else: frame_label['fg'] = BTNLABELCOLOR

        if isMaskOpen: 
            mask_label['fg'] = BTNLABELCOLORACTIVE
            maskReq = False
        else: mask_label['fg'] = BTNLABELCOLOR
            

        if isContourShowing: 
            contour_label['fg'] = BTNLABELCOLORACTIVE
            contourReq = False
        else: contour_label['fg'] = BTNLABELCOLOR
            
        if frameReq:
            frame_label['fg'] = BTNLABELCOLORINACTIVE

        if maskReq:
            mask_label['fg'] = BTNLABELCOLORINACTIVE

        if contourReq:
            contour_label['fg'] = BTNLABELCOLORINACTIVE


        root.after(REFRESH_RATE, updateData)

    #hovering over the buttons
    #Bind the Enter and Leave Events to the Button
    #Define functions
    def on_enter_frame(a):
        display_frame.config(background='OrangeRed3', foreground= "white")
    def on_enter_mask(b):
        display_mask.config(background='OrangeRed3', foreground= "white")
    def on_enter_detect(c):
        change_maskalg.config(background='OrangeRed3', foreground= "white")
    def on_enter_contour(d):
        display_contour.config(background='OrangeRed3', foreground= "white")
    def on_enter_trackbar(e):
        display_trackbar.config(background='OrangeRed3', foreground= "white")
    def on_enter_calibration(f):
        calibratebtn.config(background='OrangeRed3', foreground= "white")
    def on_enter_random(g):
        rand_point.config(background='OrangeRed3', foreground= "white")
    def on_enter_packet(h):
        send_packet.config(background='OrangeRed3', foreground= "white")
    def on_enter_exit(i):
        exitButton.config(background='OrangeRed3', foreground= "white")

    def on_leave_frame(a):
        display_frame.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_mask(a):
        display_mask.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_detect(a):
        change_maskalg.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_contour(a):
        display_contour.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_trackbar(a):
        display_trackbar.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_calibration(a):
        calibratebtn.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_random(a):
        rand_point.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_packet(a):
        send_packet.config(background= 'SystemButtonFace', foreground= 'black')
    def on_leave_exit(a):
        exitButton.config(background= 'red', foreground= 'black')

    #bind the functions to the buttons
    #frame
    display_frame.bind('<Enter>', on_enter_frame)
    display_frame.bind('<Leave>', on_leave_frame)
    #mask
    display_mask.bind('<Enter>', on_enter_mask)
    display_mask.bind('<Leave>', on_leave_mask)
    #changing mask
    change_maskalg.bind('<Enter>', on_enter_detect)
    change_maskalg.bind('<Leave>', on_leave_detect)
    #contour
    display_contour.bind('<Enter>', on_enter_contour)
    display_contour.bind('<Leave>', on_leave_contour)
    #trackbars
    display_trackbar.bind('<Enter>', on_enter_trackbar)
    display_trackbar.bind('<Leave>', on_leave_trackbar)
    #calibration
    calibratebtn.bind('<Enter>', on_enter_calibration)
    calibratebtn.bind('<Leave>', on_leave_calibration)
    #random point
    rand_point.bind('<Enter>', on_enter_random)
    rand_point.bind('<Leave>', on_leave_random)
    #packets
    send_packet.bind('<Enter>', on_enter_packet)
    send_packet.bind('<Leave>', on_leave_packet)
    #exit
    exitButton.bind('<Enter>', on_enter_exit)
    exitButton.bind('<Leave>', on_leave_exit)


    # UPDATE / REFRESH
    root.after(REFRESH_RATE, updateData)

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

try:
    # Initial Test for H Matrix (Homography calibration)
    corners = calibration.corner_detect(frame)
    destination = calibration.get_destination_points(MmtoPixelRatio, 0, 0)
    H, _= cv2.findHomography(np.float32(corners), np.float32(destination), cv2.RANSAC, 3.0)
except:
    print("Did not detect frame on opening, trying again")
    time.sleep(1)

while(True):
    start = time.time()
    # Grabbing frame from webcam
    _, frame = webcam.read()

    if not firstTimeHomography:
        # Apply H-Matrix
        frame = calibration.unwarp_frame(frame, H)

    # Apply Grayscale
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blur = cv2.GaussianBlur(grayscale, (9,9), 0)

    # Check if calibration button is pressed
    if isCalibrateBtnPressed:
        if not isCalibrateStateReached:
            isCalibrateStateReached = True
        else:
            cv2.destroyWindow('unskewed')
            isCalibrateStateReached = False
            firstTimeHomography = False
        isCalibrateBtnPressed = False

    if isCalibrateStateReached: 
        # find ArUco markers
        corners, ids =  findArucoMarkers(frame, 6, 50)
        coordinates = [[0,0],[0,0],[0,0],[0,0]]
        try:
            # loop through all corners 
            for markerCorner, markerID in zip(corners, ids):
                corners = markerCorner.reshape((4,2))
                topLeft, topRight, bottomRight, bottomLeft = corners

                # convert each of the (x, y)-coordinate pairs to integers
                topRight = (int(topRight[0]), int(topRight[1]))
                bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                topLeft = (int(topLeft[0]), int(topLeft[1]))

                # draw the bounding box of the ArUCo detection
                cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                # compute and draw the center (x, y)-coordinates of the
                # ArUco marker
                cX = int((topLeft[0] + bottomRight[0]) / 2.0)
                cY = int((topLeft[1] + bottomRight[1]) / 2.0)
                cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
                # draw the ArUco marker ID on the frame
                cv2.putText(frame, str(markerID), (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # put coordinates in list
                coordinates[int(markerID)] = [cX, cY]
        except:
            # happens if the code doesn't find a aruco code (do nothing)
            print("No codes found!")

        # print(coordinates)
        ref = frame.copy()
        for i, c in enumerate(coordinates):
            x, y = c
            cv2.circle(ref, (x,y), 3, 255, -1)
            char = chr(65 + i)
            # print(char, ':', c)
            cv2.putText(frame, char, tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
            cv2.circle(frame, tuple(c), 5, (255,0,0), -1)

        try:
            destination = calibration.get_destination_points(MmtoPixelRatio, 38, 38)
            H, _= cv2.findHomography(np.float32(coordinates), np.float32(destination), cv2.RANSAC, 3.0)
            unwarp = calibration.unwarp_frame(frame, H)
            cv2.imshow('unskewed', unwarp)
        except:
            print("Coordinate Array was empty!!!")

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
        if len(contours) != 0:
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
            try:
                cX = contdict[str(location)]['cX']
                cY = contdict[str(location)]['cY']
                # Display number of contours detected
                cv2.putText(frame, "# of contours: {}".format(contnum), (450, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                cv2.putText(frame, "Currently Tracking ID {}".format(contdict[str(location)]['ID']), (450, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
            except:
                # print("No Contours Detected.")
                pass

            # find ArUco markers
            corners, ids =  findArucoMarkers(frame, 4, 50)

            try:
                # loop through all corners 
                for (markerCorner, markerID) in zip(corners, ids):
                    corners = markerCorner.reshape((4,2))
                    topLeft, topRight, bottomRight, bottomLeft = corners

                    # convert each of the (x, y)-coordinate pairs to integers
                    topRight = (int(topRight[0]), int(topRight[1]))
                    bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
                    bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
                    topLeft = (int(topLeft[0]), int(topLeft[1]))

                    # draw the bounding box of the ArUCo detection
                    cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                    cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                    cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                    cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
                    # compute and draw the center (x, y)-coordinates of the
                    # ArUco marker
                    QcX = int((topLeft[0] + bottomRight[0]) / 2.0)
                    QcY = int((topLeft[1] + bottomRight[1]) / 2.0)
                    cv2.circle(frame, (QcX, QcY), 4, (0, 0, 255), -1)
                    # draw the ArUco marker ID on the frame
                    cv2.putText(frame, f"({QcX},{QcY})", (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            except:
                # happens if the code doesn't find a aruco code (do nothing)
                pass
        else:
            # print("No Contours Detected.")
            pass

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
        
        keys = ['name','dX', 'dY', 'command']
        data = dict.fromkeys(keys)
        
        data['name'] = "Camera1"
        data['dX'] = 0
        data['dY'] = 0
        data['command'] = 3

        try:
            read_thread = threading.Thread(target = sendToServerAsync, args = (s, data, 0, 0, 0, 0))
            read_thread.start()    
        except:
            print("Server Not Found!")

        isRandBtnPressed = False
        '''
        keys = ['name','dX', 'dY', 'command']
        data = dict.fromkeys(keys)
        
        # data['date'] = datetime.datetime.now().strftime("%m.%d.%Y")
        # data['time'] = datetime.datetime.now().strftime("%I.%M.%S%p")
        # data['version'] = VERSION
        # data['Run Status'] = True

        if not isTargetReached:
            dX = pX - cX
            dY = pY - cY

            cv2.circle(frame, (pX, pY), 7, (0,0,255), -1)
            cv2.putText(frame, "Target", (pX - 23, pY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            cv2.putText(frame, "Target Location: ({}, {})".format(pX, pY), (25, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
            
            # print("CONSOLE: \t dX = {} \t dY = {}".format(dX, dY))

            if dX < 25 and dX > -25 and dY < 25 and dY > -25:
                print("Target Successfully Acquired.")
                isTargetReached = True
                isRandBtnPressed = False
                # data['Run Status'] = False

                data['name'] = "Camera1"
                data['dX'] = dX * MmtoPixelRatio # WILL SEND DIFFERENTIAL DATA IN MILLIMETERS!!!
                data['dY'] = dY * MmtoPixelRatio # WILL SEND DIFFERENTIAL DATA IN MILLIMETERS!!!
                data['command'] = 3

                print("Random Point Test Data Recording Complete.")
                
                try:
                    s.sendall(bytes(json.dumps(data), encoding='utf-8'))
                    data_recv = s.recv(8162).decode('utf-8')
                    print(f"Recieved: {data_recv}")
                except:
                    print("Server Not Found!")

                pX = 0
                pY = 0     
        elif isRandBtnPressed == True and isTargetReached == True:
            pX = random.randint(50,600)
            pY = random.randint(50,430)

            dX = pX - cX
            dY = pY - cY

            data['name'] = "Camera1"
            data['dX'] = dX
            data['dY'] = dY
            data['command'] = 1

            try:
                s.sendall(bytes(json.dumps(data), encoding='utf-8'))
                data_recv = s.recv(8162).decode('utf-8')
                print(f"Recieved: {data_recv}")
            except:
                print("Server Not Found!")

            rndpt_start = time.time()
            
            isTargetReached = False
            '''

    # Send a single test packet to the server WITH REAL MEASUREMENTS (Send Packet Command)
    if isSendPacketBtnPressed:
        keys = ['name','dX', 'dY', 'command']
        data = dict.fromkeys(keys)
        
        data['name'] = "Camera1"
        data['dX'] = int(((cX - QcX) * MmtoPixelRatio)/1.8) # Converts pixels to mm (real life measurement)
        data['dY'] = int(((QcY - cY) * MmtoPixelRatio)/2) # Converts pixels to mm (real life measurement)
        data['command'] = 1

        try:
            read_thread = threading.Thread(target = sendToServerAsync, args = (s, data, cX, cY, QcX, QcY))
            read_thread.start()    
        except:
            print("Server Not Found!")

        isSendPacketBtnPressed = False

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

    # Screenshots for Frame and Mask
    if isFrameRcdBtnPressed:
        saveFile(frame, "FRAME")
        isFrameRcdBtnPressed = False
    if isMaskRcdButtonPressed:
        saveFile(mask, "MASK")
        isMaskRcdButtonPressed = False

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()