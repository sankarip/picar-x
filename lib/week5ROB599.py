import rossros
import time
import concurrent.futures
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
from picarx_improved import Picarx
import logging
from utils import reset_mcu
reset_mcu()
logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.WARNING)
#redoing functions from week 4 to work with rossros
def dataproducer():
    chn_0 = ADC("A0")
    chn_1 = ADC("A1")
    chn_2 = ADC("A2")
    adc_value_list = []
    adc_value_list.append(chn_0.read())
    adc_value_list.append(chn_1.read())
    adc_value_list.append(chn_2.read())
    logging.debug("data produced")
    return adc_value_list

def interp_con_prod(sensordata):
    # get the 3 values
    sensitivity=50
    polarity=1
    val1 = sensordata[0]
    val2 = sensordata[1]
    val3 = sensordata[2]
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
    logging.debug("interpreted")
    return turn

def consumer_controller(turnval):
    if turnval==1:
        px = Picarx()
        px.set_dir_servo_angle(-30)
        time.sleep(0.5)
        px.forward(5)
        time.sleep(.05)
    #turn right
    elif turnval==-1:
        px = Picarx()
        px.set_dir_servo_angle(30)
        time.sleep(0.5)
        px.forward(5)
        time.sleep(.05)
    #dont move
    elif turnval==2:
        px = Picarx()
        px.forward(0)
        time.sleep(1)
    #go straight
    else:
        px = Picarx()
        px.forward(5)
        time.sleep(.05)
    logging.debug("consumed")

class ultrasonicSensor():
    def __init__(self, timeout=0.02):
        self.trig = Pin('D2')
        self.echo = Pin('D3')
        self.timeout = timeout

    def _read(self):
        self.trig.low()
        time.sleep(0.01)
        self.trig.high()
        time.sleep(0.00001)
        self.trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        while self.echo.value()==0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value()==1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
        during = pulse_end - pulse_start
        cm = round(during * 340 / 2 * 100, 2)
        return cm

    def read(self, times=10):
        for i in range(times):
            a = self._read()
            if a != -1 or a <= 300:
                print(a)
                return a
        return -1

class ultrasonicInterp():
    def __init__(self,scale):
        self.scale=scale
    def ultrainterp(self, distance):
        if distance>1:
            speed=distance/self.scale
        else:
            speed=0
        return speed

class ultcont():
    def __init__(self):
        self.px=Picarx()
    def controlUlt(self,speed):
        self.px.forward(speed)

#create instances of functions
a=ultrasonicSensor()
b=ultrasonicInterp()
c=ultcont()
#start a bus
databus=rossros.Bus(0,"data bus")
termbus=rossros.Bus(0,"term bus")
interpbus=rossros.Bus(0,"interp bus")
timer=rossros.Timer(termbus,2,0.1, termbus, "Timer")
dataprod=rossros.Producer(dataproducer,databus,0.1,termbus,"producer")
datainterp=rossros.ConsumerProducer(interp_con_prod,databus,interpbus,0.1,termbus, "consumer producer")
control=rossros.Consumer(consumer_controller,interpbus,0.1,termbus, "consumer")
ultdatabus=rossros.Bus(0,"ult data bus")
ultinterpbus=rossros.Bus(0,"ult interp bus")
ultdataprod=rossros.Producer(ultrasonicSensor().read,ultdatabus,0.1,termbus,"ult producer")
ultdatainterp=rossros.ConsumerProducer(ultrasonicInterp(10).ultrainterp,ultdatabus,ultinterpbus,0.1,termbus, "ult consumer producer")
ultcontrol=rossros.Consumer(ultcont().controlUlt,ultinterpbus,0.1,termbus, "ult consumer")
with concurrent.futures.ThreadPoolExecutor(max_workers =7) as executor:
    #eSensor = executor.submit(dataprod)
    #eInterpreter = executor.submit(datainterp)
    #eController = executor.submit(control)
    eUltprod= executor.submit(ultdataprod)
    eUltint= executor.submit(ultdatainterp)
    eUltcons= executor.submit(ultcontrol)
    eTimer=executor.submit(timer)

#eSensor.result()
#eInterpreter.result()
#eController.result()
eUltprod.result()
eUltint.result()
eUltcons.result()
#a=ultrasonicSensor()
#a.read()


