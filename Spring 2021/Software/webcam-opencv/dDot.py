import cv2
import numpy as np

# set the image using the abosolute path
path = r'C:\Users\usuik\Documents\GitHub\UAV_Robotics_Team\Spring 2021\Software\webcam-opencv\circles.png'
img = cv2.imread(path)
# convert RGB/BGR to HLS (hue lightness saturation) with H range 0..180 if 8 bit image
#hsv - Hue, Saturation, Value
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# reading the color range
low_range = np.array([161,15,84])
high_range = np.array([179,255,255])

# mask 
mask = cv2.inRange(hsv,low_range,high_range)

# show image
cv2.imshow("Image",img)
cv2.imshow("Mask",mask)

cv2.waitKey(0)
cv2.destroyAllWindows()