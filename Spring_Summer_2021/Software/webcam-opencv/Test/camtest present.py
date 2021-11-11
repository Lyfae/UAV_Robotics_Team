import numpy as np
import cv2
import imutils
import time

# Define webcam used
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Check for compatibility. If not, force search webcam
ret, frame = webcam.read()
print(frame)
try:
    if frame == None:
        webcam = cv2.VideoCapture(-1)
except:
    print("Task Failed Successfully. Move on.")

while(True):
    # Grabbing frame from webcam
    ret, frame = webcam.read()

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
            pass

    # Show frame in seperate box
    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()