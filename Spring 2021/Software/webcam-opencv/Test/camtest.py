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

    # Show frame in seperate box
    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
webcam.release()
cv2.destroyAllWindows()