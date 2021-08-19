import numpy as np
import cv2
import tkinter as tk
from _thread import *
import threading
import time

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

    # UPDATE / REFRESH
    root.after(REFRESH_RATE, updateData)

    # LOOP
    root.mainloop()


# Begin tkinter thread
thread_tk = threading.Thread(target = tkinter)
thread_tk.start()