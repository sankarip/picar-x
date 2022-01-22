import time
from adc import ADC
import sys
sys.path.append(r'/home/pi/picar-x/lib')
from utils import reset_mcu
reset_mcu()
from picarx_improved import Picarx
#class to get ADC values from sensor
#code is from grayscale_module.py
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
#class to interpret sensor data
class light_interpreter(object):
    def __init__(self,sens, pol):
        self.light = light_sensor(500)
        #starting the turning value at going straight
        self.turn=0
        self.sensitivity=sens
        #use -1 to find lighter lines and 1 to find lighter lines
        self.polarity=pol
        #dark is larger numbers
    def interp(self):
        while True:
            #get data
            data_list = self.light.getdata()
            #get the 3 values
            val1=data_list[0]
            val2=data_list[1]
            val3=data_list[2]
            #if the contrast is to the left
            if val1-self.sensitivity*self.polarity>val2:
                #turn left
                self.turn=1
            #if contrast is to the right
            elif val3-self.sensitivity*self.polarity>val2:
                #turn right
                self.turn=-1
            #if contrast is to both sides and not in the middle
            elif val3-self.sensitivity*self.polarity>val2 and val1-self.sensitivity*self.polarity>val2:
                #print that two lines were detected
                print("lines on both sides detected")
                #go straight
                self.turn = 0
            #if there's no appreciable contrast
            elif val2-25<val3<val2+25 and val2-25<val1<val2+25:
                #print no lines found
                print("no lines found")
                #stop moving
                self.turn=2
            #if none of these conditions are met, assume that the car is on the line
            else:
                #go straight
                self.turn=0
            #print the turning value for debugging
            print(self.turn)
            #return the turning value
            return self.turn
class light_controller(object):
    def __init__(self):
        #use a sensitivity of 50 (worked for me) and a polarity of (find dark lines)
        car = light_interpreter(50, 1)
        #run the interp code from above
        self.control=car.interp()
    #function to steer the car based on the interpretation of sensor readings
    def light_steer(self):
        #turn left
        if self.control==1:
            px = Picarx()
            px.set_dir_servo_angle(-30)
            time.sleep(0.5)
            px.forward(10)
            time.sleep(.05)
        #turn right
        elif self.control==-1:
            px = Picarx()
            px.set_dir_servo_angle(30)
            time.sleep(0.5)
            px.forward(10)
            time.sleep(.05)
        #dont move
        elif self.control==2:
            px = Picarx()
            px.forward(0)
            time.sleep(1)
        #go straight
        else:
            px = Picarx()
            px.forward(10)
            time.sleep(.05)
if __name__ == "__main__":
    import time
    #run for 20 seconds to prevent crashing and safely end the code
    t_end = time.time() +20
    while time.time() < t_end:
        a=light_controller()
        a.light_steer()




