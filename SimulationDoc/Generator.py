import random
import math
import  matplotlib.pyplot as plt

class RealPtGenerator:
    def __init__(self,x,y,movetype,speed,accelerate=0,angle =0):
        self.movetype = movetype
        if self.movetype == 'UL':#匀速直线运动
            self.accelerate = 0
            self.speed = self.speed = round(speed + self.accelerate, 2)
            self.y = round(y - self.speed, 2)
            self.angle = round(angle, 3)
            self.x = round(y * math.tan(self.angle), 2)
        elif self.movetype == 'AL':#加速直线运动
            self.accelerate = round(accelerate, 2)
            self.speed = round(speed + self.accelerate, 2)
            self.y = round(y - self.speed, 2)
            self.angle = round(angle, 3)
            self.x = round(y * math.tan(self.angle), 2)
        elif self.movetype == 'UT': #匀速转弯运动
            self.angle = round(angle + angle/2, 3)
            self.accelerate = 0
            self.speed = round(speed, 2)
            self.y = round(y - self.speed, 2)
            self.x = round(y * math.tan(self.angle), 2)

        self.color = 'red'
        self.flag = 1

    def display(self):
        print("(x,y): (",self.x,",",self.y,")" , "   speed:" , self.speed , "  angle:" ,self.angle,'frameno:')

class FakePtGenerator:
    def __init__(self):
        self.accelerate = round(5*random.uniform(-1,1),2)
        self.speed = round(20 * random.uniform(0, 1),2)
        self.y = round(40 * random.uniform(0, 1),2)
        self.x = round(30 * random.uniform(-1,1),2)
        self.angle = round(math.atan(self.x / (self.y + 0.01)), 3)
        self.color= 'blue'
        self.flag = 0

    def display(self):
        print("(x,y): (", self.x, ",", self.y, ")", "   speed:", self.speed, "  angle:", self.angle)

