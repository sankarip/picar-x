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
    def __init__(self, sensitivity=50, polarity=1):
        self.light = light_sensor(500)
        self.turn=0
        #dark is larger numbers
    def interp(self):
        while True:
            data_list = self.light.getdata()
            val1=data_list[0]
            val2=data_list[1]
            val3=data_list[2]
            if val1-self.sensitivity>val2:
                self.turn=1
            elif val3-sensitivity>val2:
                self.turn=-1
            elif val3-sensitivity>val2 and val1-sensitivity>val2:
                print("lines on both sides detected")
            else:
                self.turn=0
            print(self.turn)
            return self.turn

if __name__ == "__main__":
    import time
    print("here")
    a=light_interpreter(5)
    a.interp()
    time.sleep(.5)




