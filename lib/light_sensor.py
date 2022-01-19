import time
#try:
 #   from servo import Servo
  #  from pwm import PWM
   # from pin import Pin
   # from adc import ADC
    #from filedb import fileDB
    #from ezblock import *
    #from ezblock import __reset_mcu__
    #__reset_mcu__()
    #time.sleep(0.01)
#except ImportError:
 #   print("This computer does not appear to be a PiCar -X system (ezblock is not present). Shadowing hardware calls with substitute functions")
  #  from sim_ezblock import *
from adc import ADC
import sys
sys.path.append(r'/home/pi/picar-x/lib')
from utils import reset_mcu
reset_mcu()
from picarx_improved import Picarx

class light_sensor(object):
    def __init__(self,ref = 1000):
        self.chn_0 = ADC("A0")
        self.chn_1 = ADC("A1")
        self.chn_2 = ADC("A2")
        self.ref = ref

    def getdata(self):
        adc_value_list = []
        adc_value_list.append(self.chn_0.read())
        adc_value_list.append(self.chn_1.read())
        adc_value_list.append(self.chn_2.read())
        return adc_value_list

class light_interpreter(object):
    def __init__(self,sens, pol):
        self.light = light_sensor(500)
        self.turn=0
        self.sensitivity=sens
        #use -1 to find lighter lines and 1 to find lighter lines
        self.polarity=pol
        #dark is larger numbers
    def interp(self):
        while True:
            data_list = self.light.getdata()
            val1=data_list[0]
            val2=data_list[1]
            val3=data_list[2]
            if val1-self.sensitivity*self.polarity>val2:
                self.turn=1
            elif val3-self.sensitivity*self.polarity>val2:
                self.turn=-1
            elif val3-self.sensitivity*self.polarity>val2 and val1-self.sensitivity*self.polarity>val2:
                print("lines on both sides detected")
            elif val2-25<val3<val2+25 and val2-25<val1<val2+25:
                print("no lines found")
                self.turn=2
            else:
                self.turn=0
            print(self.turn)
            return self.turn

class light_controller(object):
    def __init__(self):
        car = light_interpreter(50, 1)
        self.control=car.interp()
    def light_steer(self):
        if self.control==1:
            px = Picarx()
            px.set_dir_servo_angle(-30)
            time.sleep(0.5)
            px.forward(10)
            time.sleep(.05)
        elif self.control==-1:
            px = Picarx()
            px.set_dir_servo_angle(30)
            time.sleep(0.5)
            px.forward(10)
            time.sleep(.05)
        elif self.control==2:
            px = Picarx()
            px.forward(0)
            time.sleep(1)
        else:
            px = Picarx()
            px.forward(10)
            time.sleep(.05)


if __name__ == "__main__":
    import time
    #run for 20 seconds
    t_end = time.time() +20
    while time.time() < t_end:
        a=light_controller()
        a.light_steer()




