from readerwriterlock import rwlock
import time
try:
    from servo import Servo
    from pwm import PWM
    from pin import Pin
    from adc import ADC
    from filedb import fileDB
    #from ezblock import *
    #from ezblock import __reset_mcu__
    #__reset_mcu__()
    time.sleep(0.01)
except ImportError:
    print("This computer does not appear to be a PiCar -X system (ezblock is not present). Shadowing hardware calls with substitute functions")
    from sim_ezblock import *
import sys
sys.path.append(r'/home/pi/picar-x/lib')
import concurrent.futures
#from utils import reset_mcu
#reset_mcu()
import concurrent.futures
from picarx_improved import Picarx
import logging
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)

class Bus(object):
    def __init__(self):
        self.message=[]
        self.lock = rwlock.RWLockWriteD()
    def write(self, mes):
        #get rid of old message
        if len(self.message)>0:
            self.message=[]
        self.message.append(mes)
        with self.lock.gen_wlock():
            self.message = mes
    def read(self,readinst,readinginst):
        readinginst.message=readinst.message
        with self.lock.gen_rlock():
            message = self.message

def dataproducer(instance, timedelay):
    chn_0 = ADC("A0")
    chn_1 = ADC("A1")
    chn_2 = ADC("A2")
    adc_value_list = []
    while len(adc_value_list)<3:
        adc_value_list.append(chn_0.read())
        adc_value_list.append(chn_1.read())
        adc_value_list.append(chn_2.read())
        instance.write(adc_value_list)
        time.sleep(timedelay)
        logging.debug("data produced")

def interp_con_prod(instance, timedelay,sensitivity,polarity):
    interpbus=Bus()
    while interpbus.message is None:
        interpbus.read(instance,interpbus)
        data_list = interpbus.message
        # get the 3 values
        print(data_list)
        val1 = data_list[0]
        val2 = data_list[1]
        val3 = data_list[2]
        # if the contrast is to the left
        if val1 - sensitivity * polarity > val2:
            # turn left
            turn = 1
        # if contrast is to the right
        elif val3 - sensitivity * polarity > val2:
            # turn right
            turn = -1
        # if contrast is to both sides and not in the middle
        elif val3 - sensitivity * polarity > val2 and val1 - sensitivity * polarity > val2:
            # print that two lines were detected
            print("lines on both sides detected")
            # go straight
            turn = 0
        # if there's no appreciable contrast
        elif val2 - 25 < val3 < val2 + 25 and val2 - 25 < val1 < val2 + 25:
            # print no lines found
            print("no lines found")
            # stop moving
            turn = 2
        # if none of these conditions are met, assume that the car is on the line
        else:
            # go straight
            turn = 0
        interpbus.write(turn)
        time.sleep(timedelay)
    logging.debug("interpreted")
    return interpbus

def consumer_controller(instance,timedelay):
    #start a control bus
    controlbus=Bus()
    while len(controlbus.message) <1:
        controlbus.read(instance, controlbus)
        if controlbus.message[0]==1:
            px = Picarx()
            px.set_dir_servo_angle(-30)
            time.sleep(0.5)
            px.forward(10)
            time.sleep(.05)
        #turn right
        elif controlbus.message[0]==-1:
            px = Picarx()
            px.set_dir_servo_angle(30)
            time.sleep(0.5)
            px.forward(10)
            time.sleep(.05)
        #dont move
        elif controlbus.message[0]==2:
            px = Picarx()
            px.forward(0)
            time.sleep(1)
            print("here")
        #go straight
        else:
            px = Picarx()
            px.forward(10)
            time.sleep(.05)
    logging.debug("consumed")

#testing
databus=Bus()
#dataproducer(databus,.05)
#interpbus=interp_con_prod(databus,.05,50,1)
#consumer_controller(interpbus,.05)
sensor_delay=.05
interpreter_delay=.05
with concurrent.futures.ThreadPoolExecutor(max_workers =2) as executor:
    eSensor = executor.submit(dataproducer ,databus , sensor_delay)
    eInterpreter = executor.submit(interp_con_prod , databus ,interpreter_delay,50,1)
eSensor.result()
eInterpreter.result()