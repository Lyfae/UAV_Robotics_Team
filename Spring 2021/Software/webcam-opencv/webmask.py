import numpy as np
import cv2
import imutils
import time

# Define initial search radius
radius = 90

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

    # Convert frame to grayscale
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur the frame
    grayscale = cv2.GaussianBlur(grayscale, (radius, radius), 0)

    # Find Brightest and Dimmest points in frame (variable to white light)
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(grayscale)

    # Print results of brightness analysis
    # print(f"{minVal}, {maxVal}, {minLoc}, {maxLoc}")

    # Create a circle around brightest point
    cv2.circle(grayscale, maxLoc, radius, (0,255,0), 2)
    cv2.circle(frame, maxLoc, radius, (0,255,0), 2)

    stop = time.time()

    seconds = stop - start

    # Calculate frames per second
    fps = 1 / seconds

    # Fps display
    cv2.putText(frame,"FPS: " + str(round(fps,2)), (50,50) ,cv2.FONT_HERSHEY_SIMPLEX, 0.75,(50,200,50),2)

    # Show frame
    cv2.imshow('webcam', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()