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
    low_range = np.array([161,15,84])
    high_range = np.array([179,255,255])

    # Create Mask/Threshold 
    threshold = cv2.inRange(hsv,low_range,high_range)
            
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