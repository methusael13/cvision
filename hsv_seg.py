'''
    Author: Methusael Murmu
    Utility for blob detection using HSV color segmentation
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
    cv2.namedWindow(WIN_CAM_FEED, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_NORMAL)
    # Center the window
    cv2.moveWindow(WIN_CAM_FEED, scr_mx - win_mx, scr_my - win_my)
    # Start polling camera frames
    camera.start()

    kernel = np.ones((5, 5), np.uint8)
    # Create trackbars
    # Sane defaults for skin detection
    cv2.createTrackbar('MinH', WIN_CAM_FEED, 6, 180, nopFunc)
    cv2.createTrackbar('MaxH', WIN_CAM_FEED, 48, 180, nopFunc)
    cv2.createTrackbar('MinS', WIN_CAM_FEED, 18, 255, nopFunc)
    cv2.createTrackbar('MaxS', WIN_CAM_FEED, 174, 255, nopFunc)
    cv2.createTrackbar('MinV', WIN_CAM_FEED, 4, 255, nopFunc)
    cv2.createTrackbar('MaxV', WIN_CAM_FEED, 144, 255, nopFunc)

    while True:
        ret, frame = camera.read()
        if not ret: continue

        # Process image
        frame = cv2.flip(frame, 1)

        # Denoise
        frame_blur = cv2.GaussianBlur(frame, (21, 21), 0)
        # HSV segmentation
        hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)
        # HSV low filter vars
        minh = cv2.getTrackbarPos('MinH', WIN_CAM_FEED)
        mins = cv2.getTrackbarPos('MinS', WIN_CAM_FEED)
        minv = cv2.getTrackbarPos('MinV', WIN_CAM_FEED)
        # HSV high filter vars
        maxh = cv2.getTrackbarPos('MaxH', WIN_CAM_FEED)
        maxs = cv2.getTrackbarPos('MaxS', WIN_CAM_FEED)
        maxv = cv2.getTrackbarPos('MaxV', WIN_CAM_FEED)
        # Create hsv filter
        hsvLowFilter = np.array([minh, mins, minv], dtype = 'uint8')
        hsvHighFilter = np.array([maxh, maxs, maxv], dtype = 'uint8')
        # HSV filter mask
        mask = cv2.inRange(hsv, hsvLowFilter, hsvHighFilter)
        # Apply morph_open
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        # Apply mask to frame
        frame = cv2.bitwise_and(frame, frame, mask = mask)

        cv2.imshow(WIN_CAM_FEED, frame)
        if (cv2.waitKey(1) & 0xFF) == 27:
            break

    camera.stop()
    camera.release()
