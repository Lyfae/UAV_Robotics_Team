import numpy as np
import cv2
import imutils

# Define webcam used
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while(True):
    # Grabbing frame from webcam
    ret, frame = webcam.read()

    # Show frame in seperate box
    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
cap.release()
cv2.destroyAllWindows()