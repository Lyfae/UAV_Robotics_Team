import numpy as np
import cv2
import imutils
import time
import json

# PORT = 8009
# IP = 127.0.0.1

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

while(True):
    start = time.time()
    # Grabbing frame from webcam
    _, frame = webcam.read()

    # Apply Grayscale
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blur = cv2.GaussianBlur(grayscale, (5,5), 0)

    # Create Mask/Threshold
    threshold = cv2.threshold(blur, 60, 255, cv2.THRESH_BINARY)[1]

    # Find largest contour
    contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    
    # Loop for all contours
    area_thresh = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > area_thresh:
            area = area_thresh
            big_c = c
    
    M = cv2.moments(big_c)
        
    try:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    except:
        print("Contour not found!")

    cv2.drawContours(frame, [big_c], -1, (0, 255, 0), 2)
    cv2.circle(frame, (cX, cY), 7, (255,255,255), -1)
    cv2.putText(frame, "center", (cX - 20, cY - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(frame, "Location: ({}, {})".format(cX, cY), (400, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Find Brightest and Dimmest points in frame (variable to white light)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(blur)

    # Print results of brightness analysis
    print(f"{minVal}, {maxVal}, {minLoc}, {maxLoc}")

    stop = time.time()

    seconds = stop - start

    # Calculate frames per second
    fps = 1 / seconds

    # Fps display
    cv2.putText(frame,"FPS: " + str(round(fps,2)), (50,50) ,cv2.FONT_HERSHEY_SIMPLEX, 0.75,(50,200,50),2)

    # Show frame
    cv2.imshow('mask', threshold)
    # cv2.imshow('blurred', blur)
    cv2.imshow('webcam', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()