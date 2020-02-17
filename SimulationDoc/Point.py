#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2020.2.17
#功能：实现仿真数据点相关类
#auther： woody sun
'''

import random
import math

class Point:
    def __init__(self,x = 0, y = 0, movType = None,speed = 0, posAngle = 0, accelerate = 0,frameNO = 0,movAngle = 0, **kwargs):
        '''点类，输入参数包括x坐标，y坐标，运动类型，速度，方位角，加速度，运动角度，所处帧号'''
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.speed = speed
        self.posAngle = posAngle
        self.frameNO = frameNO
        self.accelerate = accelerate
        self.moveType = movType
        self.moveAngle = movAngle

    def display(self):
        '''显示点的属性'''
        print("当前点的坐标为：("+ self.x +","+self.y+")")
        print("当前点的速度为："+self.speed)
        print("当前点的方位角为："+self.posAngle)
        print("当前点的加速度为："+self.accelerate)
        print("当前点的运动角度为："+self.posAngle)
        print("当前帧号：" + self.frameNO)

class RealPtGenerator():
    def __init__(self,x,y,moveType,speed,accelerate=0,movAngle = 0):
        '''真实点产生器类，通过输入的点参数产生下一时刻的点迹属性'''
        self.moveType = moveType
        self.accelerate = accelerate
        self.movAngle = movAngle

        if self.moveType == 'UL':#匀速直线运动
            self.accelerate = 0
            self.movAngle = movAngle

        elif self.moveType == 'AL':#加速直线运动
            self.accelerate = round(accelerate, 2)
            self.movAngle = round(movAngle, 3)

        elif self.moveType == 'UT': #匀速转弯运动
            self.movAngle =round(movAngle + movAngle * random.uniform(0.1,0.3), 3)#每帧增加转弯角度为本身10%-30%，满足均匀分布
            if self.movAngle > 60: #最大转角不超过60°
                self.movAngle = 60
            if self.movAngle < -60:  # 最小转角不超过-60°
                self.movAngle = -60
        self.speed = round(speed + self.accelerate, 2)
        if self.speed > 40/20:  #最大速度限制为40m/s
            self.speed = 40/20
        speedY = self.speed * math.cos(math.radians(self.movAngle))  # y方向上的速度分量
        speedX = self.speed * math.sin(math.radians(self.movAngle))  # x方向上的速度分量
        self.y = round(y - speedY, 2)
        self.x = round(x - speedX, 2)
        self.posAngle  = round(math.atan(self.x/(self.y+0.0001)), 3)

        self.color = 'red'
        self.marker = 'o'
        self.flag = 1
        self.size = 20


    # def display(self):
    #     '''显示当前点信息'''
    #     print("(x,y): (",self.x,",",self.y,")" , "   speed:" , self.speed , "  angle:" ,self.angle,'frameNO:')

class FakePtGenerator():
    def __init__(self):
        '''虚假点产生器类，用于产生随机噪声点，各属性满足均匀分布'''
        self.accelerate = round(1 / 20 *random.uniform(-0.5,2),2)
        self.speed = round(70 / 20 * random.uniform(0, 1),2)
        self.y = round(40 * random.uniform(0, 1),2)
        self.x = round(7.5 * random.uniform(-1,1),2)
        self.posAngle = round(math.degrees(math.atan(self.x / (self.y + 0.0001))), 3)
        self.color= 'gray'
        self.marker = 'x'
        self.flag = 0
        self.size = 10

    # def display(self):
    #     '''显示当前点信息'''
    #     print("(x,y): (", self.x, ",", self.y, ")", "   speed:", self.speed, "  angle:", self.angle)
