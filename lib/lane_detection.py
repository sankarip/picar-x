import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import warnings
import time
import sys
sys.path.append(r'/home/pi/picar-x/lib')
from utils import reset_mcu
reset_mcu()
from picarx_improved import Picarx

warnings.simplefilter('ignore', np.RankWarning)
camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 24
rawCapture = PiRGBArray(camera, size=camera.resolution)
#start a list for steering angles
steering_angles=[]
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):  # use_video_port=True
    img = frame.array
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([60, 40, 40])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    #cv2.imshow("video", img)  # OpenCV image show
    #cv2.imshow("mask", mask)  # OpenCV image show
    edges = cv2.Canny(mask, 200, 400)
    #cv2.imshow("edges", edges)
    height, width = edges.shape
    mask = np.zeros_like(edges)

    # only focus bottom half of the screen
    polygon = np.array([[
        (0, height * 1 / 2),
        (width, height * 1 / 2),
        (width, height),
        (0, height),
    ]], np.int32)

    cv2.fillPoly(mask, polygon, 255)
    cropped_edges = cv2.bitwise_and(edges, mask)
    #cv2.imshow("cropped edges", cropped_edges)
    rho = 2  # distance precision in pixel, i.e. 1 pixel
    angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
    min_threshold = 20  # minimal of votes
    line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold,
                                    np.array([]), minLineLength=8, maxLineGap=4)
    #print(len(line_segments))
    #if line_segments is not None:
        #print(len(line_segments))
     #   for line in line_segments:
      #      x1, y1, x2, y2 = line[0]
       #     cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
    #cv2.imshow("lane lines", img)

    def make_points(h,w, line):
        height=h
        width=w
        slope, intercept = line
        if slope !=0:
            y1 = height  # bottom of the frame
            y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

            # bound the coordinates within the frame
            x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
            x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
        else:
            y1 = height  # bottom of the frame
            y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

            # bound the coordinates within the frame
            x1 = max(-width, min(2 * width, int((y1 - intercept) / .5)))
            x2 = max(-width, min(2 * width, int((y2 - intercept) / .5)))

        return [[x1, y1, x2, y2]]

    height, width = edges.shape
    left_fit = []
    right_fit = []
    lane_lines = []
    boundary = 1 / 3
    left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
    right_region_boundary = width * boundary  # right lane line segment should be on left 2/3 of the screen
    if line_segments is not None:
        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:

                #fit = np.polyfit((x1, x2), (y1, y2), 1)
                #slope = fit[0]
                #intercept = fit[1]
                #manually doing slope because polyfit breaks
                if x1 != x2:
                    #y=mx+b
                    slope=(y2-y1)/(x2-x1)
                    intercept=y2-slope*x2
                else:
                    #pretend vertical lines are very steep
                    slope=10000
                    intercept = y2 - slope * x2
                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(make_points(height,width, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(make_points(height,width, right_fit_average))
    #print(lane_lines)
    if lane_lines is not None:
        #print(len(line_segments))
        for line in lane_lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
    #cv2.imshow("lane lines", img)
    if len(lane_lines) ==2:
        #print(lane_lines)
        _, _, left_x2, _ = lane_lines[0][0]
        _, _, right_x2, _ = lane_lines[1][0]
        mid = int(width / 2)
        x_offset = (left_x2 + right_x2) / 2 - mid
        y_offset = int(height / 2)
        angle_to_mid_radian = np.arctan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / np.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg + 90 # this is the steering angle needed by picar front wheel
        #print(steering_angle)
        steering_angles.append(steering_angle)
        if len(steering_angles)==2:
            ang1=steering_angles[0]
            ang2=steering_angles[1]
            #if its within 5 degrees
            if ang1-5<ang2<ang1+5:
                steering_angle=steering_angle
            elif ang1-5>ang2:
                #only move by 5
                steering_angle=ang1-5
            elif ang1+5<ang2:
                steering_angle=ang1+5
        steering_angle_radian = steering_angle / 180.0 * np.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / np.tan(steering_angle_radian))
        y2 = int(height / 2)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 5)
        #get rid of the old entry
        steering_angles.pop(0)
        # convert to heading for car
        steering_angle = steering_angle - 90
        # drive a little bit
        px = Picarx()
        px.set_dir_servo_angle(steering_angle)
        time.sleep(0.5)
        px.forward(10)
        time.sleep(.1)
        px.forward(0)
        time.sleep(1)


    elif len(lane_lines) ==1:
        x1, _, x2, _ = lane_lines[0][0]
        x_offset = x2 - x1
        y_offset = int(height / 2)
        angle_to_mid_radian = np.arctan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / np.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel
        steering_angle_radian = steering_angle / 180.0 * np.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / np.tan(steering_angle_radian))
        y2 = int(height / 2)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 5)
        #print(steering_angle)
        steering_angles.append(steering_angle)

        if len(steering_angles)==2:
            ang1=steering_angles[0]
            ang2=steering_angles[1]
            #if its within 5 degrees
            if ang1-5<ang2<ang1+5:
                steering_angle=steering_angle
            elif ang1-5>ang2:
                #only move by 5
                steering_angle=ang1-5
            elif ang1+5<ang2:
                steering_angle=ang1+5
        steering_angle_radian = steering_angle / 180.0 * np.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / np.tan(steering_angle_radian))
        y2 = int(height / 2)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 5)
        #get rid of the old entry
        steering_angles.pop(0)
        #convert to heading for car
        steering_angle=steering_angle-90
        #drive a little bit
        px = Picarx()
        px.set_dir_servo_angle(steering_angle)
        time.sleep(0.5)
        px.forward(10)
        time.sleep(.1)
        px.forward(0)
        time.sleep(1)
    else:
        print("no steering lines found")
        #don't move
        px = Picarx()
        px.forward(0)
        time.sleep(1)
    cv2.imshow("steering", img)
    rawCapture.truncate(0)  # Release cache

    k = cv2.waitKey(1) & 0xFF
    # 27 is the ESC key, which means that if you press the ESC key to exit
    if k == 27:
        camera.close()
        break
