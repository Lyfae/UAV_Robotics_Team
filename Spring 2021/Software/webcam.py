import numpy as np
import cv2
import imutils

# Define webcam used
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Import face-recgonition software
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

while(True):
    # Grabbing frame from webcam
    ret, frame = webcam.read()

    # Frame width and height + fps
    width = webcam.get(3)
    height = webcam.get(4)

    cv2.putText(frame, "Frame Max (x,y): ({},{})".format(width, height), (frame.shape[0] - 100, 465), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Defining box dimensions
    centerx = 0.0
    centery = 0.0
    object_detect = ""

    # Create a box around the face, if detected
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        frame = cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 3)
        centerx = x + 0.5 * float(w)
        centery = y + 0.5 * float(h)

    # Text to display dimensions
    cv2.putText(frame, "x: {}, y: {}".format(centerx, centery), (frame.shape[0] - 70, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Text to display object type
    if not centerx and not centery:
        object_detect = "None"
    else:
        object_detect = "Face"
    
    cv2.putText(frame, "Object: {}".format(object_detect), (frame.shape[0] - 70, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Show frame in seperate box
    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Safely close all windows
cap.release()
cv2.destroyAllWindows()