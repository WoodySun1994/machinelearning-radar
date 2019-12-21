import random
import math

class Point:
    def __init__(self,x = 0, y = 0, movtype = None,speed = 0, angle = 0, accelerate = 0,frameno = 0,**kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.frameno = frameno
        self.accelerate = accelerate
        self.movetype = movtype

    def display(self):
        print("当前点的坐标为：("+ self.x +","+self.y+")")
        print("当前点的速度为："+self.speed)
        print("当前点的角度为："+self.angle)
        print("当前点的加速度为："+self.accelerate)
        print("当前帧号：" + self.frameno)

class RealPoint(Point):
    def __init__(self, x = 0, y = 0, speed=0, angle=0, frameno=0):
        super().__init__(x, y, speed, angle, frameno)
        self.color = 'red'
        self.flag = 1

class FakePoint(Point):
    def __init__(self, x=0, y=0, speed=0, angle=0, frameno=0):
        super().__init__(x, y, speed, angle, frameno)
        self.color = 'blue'
        self.flag = 0


class RealPtGenerator(RealPoint):
    def __init__(self,x,y,movetype,speed,accelerate=0,angle =0):
        self.movetype = movetype
        if self.movetype == 'UL':#匀速直线运动
            self.accelerate = 0
            self.speed = self.speed = round(speed + self.accelerate, 2)
            self.y = round(y - self.speed, 2)
            self.angle = round(angle, 3)
            self.x = round(x - speed * math.tan(self.angle), 2)
        elif self.movetype == 'AL':#加速直线运动
            self.accelerate = round(accelerate, 2)
            self.speed = round(speed + self.accelerate, 2)
            self.y = round(y - self.speed, 2)
            self.angle = round(angle, 3)
            self.x = round(x - speed * math.tan(self.angle), 2)
        elif self.movetype == 'UT': #匀速转弯运动
            self.angle = round(angle + (angle/4), 3)
            if self.angle > 1.22:  #转弯角度不超过正负70°
                self.angle = 1.22

            elif self.angle < -1.22:
                self.angle = -1.22
            self.accelerate = 0
            self.speed = round(speed + self.accelerate, 2)
            self.y = round(y - self.speed, 2)

            self.x = round(x - speed * math.tan(self.angle), 2)

        self.color = 'red'
        self.flag = 1

    def display(self):
        print("(x,y): (",self.x,",",self.y,")" , "   speed:" , self.speed , "  angle:" ,self.angle,'frameno:')

class FakePtGenerator(FakePoint):
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
