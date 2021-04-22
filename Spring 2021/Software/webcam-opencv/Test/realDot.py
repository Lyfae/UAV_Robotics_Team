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
    # grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Apply Gaussian Blur
    #blur = cv2.GaussianBlur(grayscale, (5,5), 0)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # reading the color range
    low_range = np.array([0,157,157])
    high_range = np.array([179,255,255])

    # Create Mask/Threshold 
    threshold = cv2.inRange(hsv,low_range,high_range)
    threshold = cv2.erode(threshold, None, iterations=2)
    threshold = cv2.dilate(threshold, None, iterations=2)  

    # Find contours
    contours = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    
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

    stop = time.time()

    # Calculate frames per second
    seconds = stop - start
    fps = float(1) / seconds

    # Fps display
    cv2.putText(frame,"FPS: " + str(round(fps,2)), (50,50) ,cv2.FONT_HERSHEY_SIMPLEX, 0.75,(50,200,50),2)

    # Show frame
    cv2.imshow('mask', threshold)
    # cv2.imshow('blurred', blur)
    cv2.imshow('webcam', frame)
    #show the bitwise of the red color objects only
    res = cv2.bitwise_and(frame,frame,mask=threshold)
    cv2.imshow('res',res)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()