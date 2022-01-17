
import sys
sys.path.append(r'/home/pi/picar-x/lib')
from utils import reset_mcu
reset_mcu()

from picarx_improved import Picarx
import time


def forwardandback():
    px = Picarx()
    px.forward(30)
    time.sleep(1.5)
    px.forward(0)
    px.backward(30)
    time.sleep(1.5)
    px.backward(0)

def parallel_park_left():
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

def parallel_park_right():
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

def kturn():
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
#starting the loop
exitvar=0
#loop to choose driving
while exitvar !=1:
    choice=input("press 1 for forward and back, 2 for parallel park left, 3 for parallel park right, 4 for kturn, 5 to exit")
    if choice==1:
        forwardandback()
    elif choice==2:
        parallel_park_left()
    elif choice==3:
        parallel_park_right()
    elif choice==4:
        kturn()
    elif choice==5:
        exitvar==1

