
import sys
sys.path.append(r'/home/pi/picar-x/lib')
from utils import reset_mcu
reset_mcu()

from picarx_improved import Picarx
import time


def forwardandback:
    px = Picarx()
    px.forward(30)
    time.sleep(1.5)
    px.forward(0)
    px.backward(30)
    time.sleep(1.5)
    px.backward(0)

def parallel_park_left:
    #I cant parallel park in real life either
    px = Picarx()
    px.set_dir_servo_angle(20)
    time.sleep(0.5)
    px.backward(30)
    time.sleep(1.5)
    px.set_dir_servo_angle(-20)
    time.sleep(0.5)
    px.backward(30)
    time.sleep(1.5)
    px.backward(0)

def parallel_park_right:
    px = Picarx()
    px.set_dir_servo_angle(-20)
    time.sleep(0.5)
    px.backward(30)
    time.sleep(1.5)
    px.backward(0)
    px.set_dir_servo_angle(20)
    time.sleep(0.5)
    px.backward(30)
    time.sleep(1.5)
    px.backward(0)

def kturn:
    px = Picarx()
    px.set_dir_servo_angle(-20)
    time.sleep(0.5)
    px.backward(30)
    time.sleep(1.5)
    px.backward(0)
    px.set_dir_servo_angle(20)
    time.sleep(0.5)
    px.forward(30)
    time.sleep(1.5)
    px.forward(0)

