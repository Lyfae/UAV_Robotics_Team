import numpy as np
import cv2
import imutils
import time
import matplotlib.pyplot as plt

def corner_detect(frame):
    # Using the shi_tomashi algorithm

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    corners = cv2.goodFeaturesToTrack(gray, 4, 0.01, 100)
    corners = np.int0(corners)
    corners = sorted(np.concatenate(corners).tolist())

    # print("Detected Corner Points:\n")

    ref = frame.copy()
    for i, c in enumerate(corners):
        x, y = c
        cv2.circle(ref, (x,y), 3, 255, -1)
        char = chr(65 + i)
        # print(char, ':', c)
        cv2.putText(frame, char, tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
        cv2.circle(frame, tuple(c), 5, (255,0,0), -1)
    
    # plt.imshow(ref)
    # plt.title('Corner Detection Using Shi-Tomashi Algorithm')
    # plt.show()
    return corners

def get_destination_points(scale, w_scr, h_scr):
    w = 215 * scale + w_scr
    h = 280 * scale + h_scr

    destination_corners = np.float32([(w_scr, h_scr + h - 1), (w_scr,h_scr), (w_scr + w-1, h_scr), (w_scr + w - 1, h_scr + h - 1)])

    # print("\nDestination Points:\n")

    for i, c in enumerate(destination_corners):
        char = chr(65 + i) + "'"
        # print(char, ':', c)

    # print(f"\nDimensions of Original Image Mapped (Ratio):\nHeight: {h}\tWidth: {w}")
    return destination_corners

def unwarp_frame(frame, corners, destination, H):
    h, w = frame.shape[:2]
    # print("\nHomography Matrix:\n", H)
    unwarp = cv2.warpPerspective(frame, H, (w,h), flags=cv2.INTER_LINEAR)
    return unwarp