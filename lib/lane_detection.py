import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=camera.resolution)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):  # use_video_port=True
    img = frame.array
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([60, 40, 40])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    #cv2.imshow("video", img)  # OpenCV image show
    #cv2.imshow("mask", mask)  # OpenCV image show
    edges = cv2.Canny(mask, 200, 400)
    cv2.imshow("edges", edges)
    rawCapture.truncate(0)  # Release cache

    k = cv2.waitKey(1) & 0xFF
    # 27 is the ESC key, which means that if you press the ESC key to exit
    if k == 27:
        camera.close()
        break
