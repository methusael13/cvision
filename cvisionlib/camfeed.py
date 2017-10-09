'''
    Author: Methusael Murmu
    Module implementing parallel Camera I/O feed
'''

import cv2
from threading import Thread

class CameraFeedException(Exception):
    def __init__(self, src, msg = None):
        if msg is None:
            msg = 'Unable to open camera devive: %d' % src
        super(CameraFeedException, self).__init__(msg)


class CameraFeed:
    def __init__(self, src = 0):
        self.__stream = cv2.VideoCapture(src)
        if not self.__stream.isOpened():
            raise CameraFeedException(src)

        self.__active = True
        self.__ret, self.__frame = self.__stream.read()
        self.__cam_thread = None

    @property
    def stream(self):
        return self.__stream

    def read(self):
        return self.__ret, self.__frame

    def start(self):
        if self.__cam_thread is None:
            self.__cam_thread = Thread(target = self.update)
        self.__cam_thread.start()

    def update(self):
        while True:
            self.__ret, self.__frame = self.__stream.read()
            if not self.__active:
                break

    def stop(self):
        self.__active = False

    def release(self):
        while self.__cam_thread.is_alive(): pass
        self.__stream.release()
        self.__cam_thread = None
