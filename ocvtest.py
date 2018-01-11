'''
    Author: Methusael Murmu
    Simple utility for face and eye detection
'''

import sys, cv2
import tkinter as tk
from cvisionlib.camfeed import *

WIN_TITLE = 'Video Feed'
WIN_PROC_TITLE = 'Postprocess Feed'

# Define Cascade Classifiers
face_cascade = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('cascades/haarcascade_eye.xml')

# Font to be used on ROI
cap_font = cv2.FONT_HERSHEY_PLAIN

# Face detection on camera feed
def detectFacesGeneric(frame, detect_eyes = False, get_anchor = False):
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect face and eye
    faces = face_cascade.detectMultiScale(frame_gray, 1.3, 3)
    # Define anchor
    anchor_roi = []
    if len(faces) > 0: anchor_roi.append(faces[0])

    for (x, y, w, h) in faces:
        # Draw face ROI
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(frame, 'Human', (x, y - 10), cap_font, 0.8, (255, 255, 255), 1, cv2.LINE_8)

        if detect_eyes:
            # Extract ROI for face from frame_gray
            roi_face_gray = frame_gray[y:y+h, x:x+w]
            roi_face_color = frame[y:y+h, x:x+h]

            # Detect eyes using the above ROI
            eyes = eye_cascade.detectMultiScale(roi_face_gray)
            # Draw eye ROI
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_face_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    if get_anchor:
        anchor_pt = []
        # Append mid-point of ROI
        if anchor_roi:
            # (x + w / 2)
            anchor_pt.append(anchor_roi[0][0] + anchor_roi[0][2] // 2)
            # (y + h / 2)
            anchor_pt.append(anchor_roi[0][1] + anchor_roi[0][3] // 2)
        return frame, anchor_pt
    return frame


# Face detection on a single image
def detectFacesFromImage(image, detect_eyes = False):
    h, w, c = image.shape
    aspect, max_fac = w / h, 800

    if w > h:
        # Landscape format
        w = max_fac; h = int(w / aspect)
    else:
        # Portrait format
        h = max_fac; w = int(h * aspect)

    img_res = cv2.resize(image, (w, h))
    cv2.imshow(WIN_PROC_TITLE, detectFacesGeneric(img_res, detect_eyes))

    if (cv2.waitKey(0) & 0xFF) == 27:
        return


# Detection on camera feed
def detectFacesFromCamera(detect_eyes = False, anchor_window = False):
    try:
        # Use default camera device
        camera = CameraFeed(0)
        stream = camera.stream
    except CameraFeedException as e:
        print(str(e))
        return

    # Camera resolution
    capw = int(stream.get(cv2.CAP_PROP_FRAME_WIDTH))
    caph = int(stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Window mid point
    win_mx, win_my = capw // 2, caph // 2

    # Screen resolution
    root = tk.Tk()
    scrw, scrh = int(root.winfo_screenwidth()), int(root.winfo_screenheight())
    scr_mx, scr_my = scrw // 2, scrh // 2
    # Relative scale
    aspw, asph = scrw / capw, scrh / caph

    # Create window placeholder
    cv2.namedWindow(WIN_PROC_TITLE, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_NORMAL)
    # Center the window
    cv2.moveWindow(WIN_PROC_TITLE, scr_mx - win_mx, scr_my - win_my)

    # Start polling camera frames
    camera.start()
    delta_anchor = [0, 0]
    while 1:
        # Camera polling runs on a separate thread, reduces Camera IO latency
        ret, frame = camera.read()
        # Skip processing if frame was dropped
        if not ret: continue;

        # Flip horizontally
        frame = cv2.flip(frame, 1)

        # Trace anchor
        if anchor_window:
            frame, anchor = detectFacesGeneric(frame, detect_eyes, anchor_window)
            if anchor:
                # Scale anchor delta to screen
                delta_anchor[0] = int((anchor[0] - win_mx) * aspw)
                delta_anchor[1] = int((anchor[1] - win_my) * asph)
                # Move window, reflecting relative position of face on camera
                # For some reason the window has an extra vertical offset - (Subtracted to adjust)
                cv2.moveWindow(WIN_PROC_TITLE, scr_mx + delta_anchor[0] - win_mx, scr_my + delta_anchor[1] - win_my - 50)
        else:
            frame = detectFacesGeneric(frame, detect_eyes)
        cv2.imshow(WIN_PROC_TITLE, frame)

        if (cv2.waitKey(1) & 0xFF) == 27:
            break

    camera.stop()
    camera.release()


if __name__ == '__main__':
    cmd_args = sys.argv
    if len(cmd_args) > 1:
        try:
            img = cv2.imread(cmd_args[1])
            detectFacesFromImage(img, True)

        except Exception as e:
            print(str(e))
    else:
        detectFacesFromCamera(False, True)

    cv2.destroyAllWindows()
