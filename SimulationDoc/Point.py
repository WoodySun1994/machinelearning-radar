#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.25
#功能：实现仿真数据点相关类
#auther： woody sun
'''

import random
import math

class Point:
    def __init__(self,x = 0, y = 0, movtype = None,speed = 0, angle = 0, accelerate = 0,frameno = 0,**kwargs):
        '''点类，输入参数包括x坐标，y坐标，运动类型，速度，角度，加速度，所处帧号'''
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.frameno = frameno
        self.accelerate = accelerate
        self.movetype = movtype

    def display(self):
        '''显示点的属性'''
        print("当前点的坐标为：("+ self.x +","+self.y+")")
        print("当前点的速度为："+self.speed)
        print("当前点的角度为："+self.angle)
        print("当前点的加速度为："+self.accelerate)
        print("当前帧号：" + self.frameno)

class RealPoint(Point):
    def __init__(self, x = 0, y = 0, speed=0, angle=0, frameno=0):
        '''真实点类，继承自点类，拥有颜色和flag属性，用于与虚假航迹进行区分'''
        super().__init__(x, y, speed, angle, frameno)
        self.color = 'red'
        self.flag = 1

class FakePoint(Point):
    def __init__(self, x=0, y=0, speed=0, angle=0, frameno=0):
        '''虚假点类'''
        super().__init__(x, y, speed, angle, frameno)
        self.color = 'gray'
        self.flag = 0

class RealPtGenerator():
    def __init__(self,x,y,movetype,speed,accelerate=0,angle =0):
        '''真实点产生器类，通过输入的点参数产生下一时刻的点迹属性'''
        self.movetype = movetype
        if self.movetype == 'UL':#匀速直线运动
            self.accelerate = 0
            self.angle = round(angle, 3)

        elif self.movetype == 'AL':#加速直线运动
            self.accelerate = round(accelerate, 2)
            self.angle = round(angle, 3)

        elif self.movetype == 'UT': #匀速转弯运动
            self.angle = round(angle + (angle/4), 3)
            if self.angle > 90:  #转弯角度不超过正负90°
                self.angle = 90

            elif self.angle < -90:
                self.angle = -90
            self.accelerate = 0

        self.speed = round(speed + self.accelerate, 2)
        speedy = self.speed * math.cos(math.radians(self.angle))  # y方向上的速度分量
        speedx = self.speed * math.sin(math.radians(self.angle))  # x方向上的速度分量
        self.y = round(y - self.speed / 36 * speedy, 2)  # speed/36 -> 将km/s改为m/s
        self.x = round(x - speed / 36 * speedx, 2)

        self.color = 'red'
        self.flag = 1
        self.size = 5

    def display(self):
        '''显示当前点信息'''
        print("(x,y): (",self.x,",",self.y,")" , "   speed:" , self.speed , "  angle:" ,self.angle,'frameno:')

class FakePtGenerator():
    def __init__(self):
        '''虚假点产生器类，用于产生随机噪声点，各属性满足均匀分布'''
        self.accelerate = round(5*random.uniform(-1,1),2)
        self.speed = round(15 * random.uniform(0, 1),2)
        self.y = round(40 * random.uniform(0, 1),2)
        self.x = round(30 * random.uniform(-1,1),2)
        self.angle = round(math.degrees(math.atan(self.x / (self.y + 0.01))), 3)
        self.color= 'gray'
        self.flag = 0
        self.size = 2

    def display(self):
        '''显示当前点信息'''
        print("(x,y): (", self.x, ",", self.y, ")", "   speed:", self.speed, "  angle:", self.angle)
