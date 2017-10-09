'''
    Author: Methusael Murmu
    An example for detecting and overlaying contours
'''

import sys, cv2
import tkinter as tk
from cvisionlib.camfeed import *

import numpy as np

WIN_CAM_FEED = 'Camera Feed'

def nopFunc(pos): pass

if __name__ == '__main__':
    try:
        camera = CameraFeed(0)
        stream = camera.stream
    except CameraFeedException as e:
        print(srt(e)); sys.exit(1)

    # Camera resolution
    capw = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
    caph = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Window mid point
    win_mx, win_my = capw // 2, caph // 2

    # Screen resolution
    root = tk.Tk()
    scrw, scrh = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
    scr_mx, scr_my = scrw // 2, scrh // 2

    # Create placeholder for image window
    cv2.namedWindow(WIN_CAM_FEED, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
    # Center the window
    cv2.moveWindow(WIN_CAM_FEED, scr_mx - win_mx, scr_my - win_my)
    # Start polling camera frames
    camera.start()

    while True:
        ret, frame = camera.read()
        if not ret: continue

        # Process image
        frame = cv2.flip(frame, 1)

        # Denoise
        frame_blur = cv2.GaussianBlur(frame, (21, 21), 0)
        # Contour detection
        frame_gray = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2GRAY)
        # Threshold
        _, frame_gray = cv2.threshold(frame_gray, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        
        # Find contours
        frame_gray, contours, heirarchy = cv2.findContours(frame_gray.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # Filter contour with max area
        cnt = max(contours, key = lambda x: cv2.contourArea(x))
        # Draw contours
        cv2.drawContours(frame, [cnt], 0, (0, 0, 255), 2)

        cv2.imshow(WIN_CAM_FEED, frame)
        if (cv2.waitKey(1) & 0xFF) == 27:
            break

    camera.stop()
    camera.release()
