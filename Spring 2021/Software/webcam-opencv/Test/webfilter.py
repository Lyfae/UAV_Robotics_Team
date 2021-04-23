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
    blur = cv2.GaussianBlur(grayscale, (9,9), 0)

    # Create Mask/Threshold
    threshold = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 23, 3)

    # Find contours and filter using contour area
    cnts = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 10:
            cv2.drawContours(frame, [c], -1, (36,255,12), 1)

    stop = time.time()

    seconds = stop - start

    # Calculate frames per second
    fps = 1 / seconds

    # Fps display
    cv2.putText(frame,"FPS: " + str(round(fps,2)), (50,50) ,cv2.FONT_HERSHEY_SIMPLEX, 0.75,(50,200,50),2)

    # Show frame
    cv2.imshow('mask', threshold)
    cv2.imshow('webcam', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()