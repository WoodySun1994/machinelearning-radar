#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2020.2.17
#功能：仿真帧数据产生函数
#auther： woody sun
'''

import Point
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import math

AUTOTESTEN = True   #自动测试
AUTOTESTSET = {'realTrackNum': 6, 'fakeTrackNum':60, 'frameNum':4}
DefaultData = True #使用默认起始点

'''根据path参数新建文件夹'''
def MkDir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        pass

'''自动测试数据生成器，输入参数为需要产生的真实航迹数量'''
def AutoTestDataGen(DefaultData,realTrackNum):
    if DefaultData == True:
        autoTestData = [{'movType': 'UT', "x": -6.5, "y": 10.0, 'speed': 13.5/20, 'posAngle':round(math.atan(-6.5/10.0), 3), 'accelerate': 0,'movAngle':-9.8},
                        {'movType': 'UT', "x": 4.5, "y": 31.0, 'speed': 17.5/20, 'posAngle': round(math.atan(4.5/31.0), 3), 'accelerate': 0,'movAngle':8},
                        {'movType': 'AL', "x": 1.3, "y": 39.0, 'speed': 18.5/20, 'posAngle': round(math.atan(1.3/39.0), 3), 'accelerate': 0.84/20,'movAngle':2},
                        {'movType': 'AL', "x": -6.0, "y": 36.0, 'speed': 12/20, 'posAngle': round(math.atan(-6.0/36.0), 3), 'accelerate': 1.99/20,'movAngle':-7},
                        {'movType': 'UL', "x": -4.0, "y": 34.0, 'speed': 19/20, 'posAngle': round(math.atan(-4.0/34.0), 3), 'accelerate': 0,'movAngle':0},
                        {'movType': 'UL', "x": 6.5, "y": 25.0, 'speed': 19.5/20, 'posAngle': round(math.atan(6.5/25.0), 3), 'accelerate': 0,'movAngle':9.4}
                        ]
    else:
        autoTestData  = []
        for i in range(realTrackNum):
            point = {}
            if realTrackNum == 6:
                moveType = ['UT','UT','AL','AL','UL','UL']
                point["movType"] = moveType[i]
            else:
                point["movType"] = random.choice(['UT','AL','UL'])  #随机选择三种运动模型
            point["y"] = 35 * round(random.random(),2) + 5
            if point["y"] > 25:#根据目标的距离限制目标出现区域
                point["x"] = 7.5 * round(random.uniform(-1, 1), 2)
                point["movAngle"] = 10 * round(random.uniform(-1, 1), 3)  # 横坐标轴上方远处的目标运动角度满足-10-10°的均匀分布
            else:
                point["x"] = 6.5 + round(random.uniform(-0.5, 0.5), 2)
                targetPosition = random.choice(['left','right'])
                if targetPosition == 'left':
                    point["x"] *= -1
                    point["movAngle"] = 10 * round(random.uniform(-1, 0), 3)  # 纵坐标轴左边的目标运动角度满足-10-0°的均匀分布
                else:# 纵坐标轴左边的目标运动角度满足0-10°的均匀分布
                    point["movAngle"] = 10 * round(random.uniform(0, 1), 3)
            point["speed"] = 10 * round(random.uniform(1,2),2) / 20    #速度满足10-20m/s的均匀分布，雷达扫描频率T为0.05s

            if point["movType"] == 'AL':
                point["accelerate"]  = round(0.5 * random.uniform(1,4),2) / 20   #加速度满足0.5m-2m/s的均匀分布，雷达扫描频率T为0.05s
            else:
                point["accelerate"] = 0
            point["posAngle"] = round(math.atan(point["x"]/(point["y"] + 0.0001)), 3)
            autoTestData.append(point)
    return autoTestData

'''仿真数据帧类'''
class FrameInfor:
    def __init__(self,realTrackNum = 5, fakeTrackNum = 10, frameNo  = 0,lastFrame = None):
        self.pointsList = []
        self.realTrackNum = realTrackNum
        self.fakeTrackNum = fakeTrackNum
        self.frameNo = frameNo

        if lastFrame == None :#第一帧数据由用户给出
            for i in range(int(self.realTrackNum)):
                if AUTOTESTEN == False:#非自动测试的情况下，需要用户手动输入运动参数
                    print("第", i + 1, "个航迹的运动类型(UL,AL,UT)：", end='')
                    movType = input()
                    if movType != 'UL' and movType != 'AL' and movType != 'UT':
                        raise Exception("Wrong Move Type!")

                    print("第", i + 1, "个航迹的x坐标（-7.5~7.5）：", end='')
                    x = float(input())
                    print("第", i + 1, "个航迹的y坐标（0~40）：", end='')
                    y = float(input())
                    print("第", i + 1, "个航迹的初始速度：", end='')
                    speed = float(input())
                    print("第", i + 1, "个航迹的运动角度(-0.2~0.2)：", end='')
                    movAngle = float(input())
                    if movType == 'AL':
                        print("第", i + 1, "个航迹的加速度：", end='')
                        accelerate = float(input())
                    else:
                        accelerate = 0.0
                else:#自动测试时读取参数列表作为仿真数据来源
                    autoTestData = AutoTestDataGen(DefaultData,AUTOTESTSET['realTrackNum'])
                    movType = autoTestData[i]["movType"]
                    x = autoTestData[i]["x"]
                    y = autoTestData[i]["y"]
                    speed = autoTestData[i]["speed"]
                    movAngle = autoTestData[i]["movAngle"]
                    accelerate = autoTestData[i]["accelerate"]

                RP = Point.RealPtGenerator(x, y, movType, speed, accelerate, movAngle)#根据第一帧运动产生真实点迹
                self.pointsList.append(RP)

            for i in range(int(self.fakeTrackNum)):   #根据设置的每帧虚假点个数生成虚假点
                FP = Point.FakePtGenerator()
                self.pointsList.append(FP)
        else:
            self.lastFrame = lastFrame

    '''新建帧'''
    def CreatFrame(self):
        for point in self.lastFrame.pointsList:
            if point.flag == 1:  #如果当前点为真实点，则将改点传入对应的真实点产生函数中
                RP = Point.RealPtGenerator(point.x, point.y, point.moveType, point.speed,point.accelerate,point.movAngle)
                self.pointsList.append(RP)

            else:#如果当前点为虚假点，则调用虚假点产生函数
                FP = Point.FakePtGenerator()
                self.pointsList.append(FP)

    '''显示帧信息（调试用）'''
    def ShowFrame(self):
        for point in self.pointsList:
            print("(x,y): (",point.x,",",point.y,")" , "   speed:" , point.speed , "  movAngle:" ,point.movAngle)
            plt.scatter(point.x, point.y, c=point.color)

        plt.xlim((-8, 8))
        plt.ylim((0, 40))
        plt.show()

    '''将仿真帧数据保存为txt文件'''
    def SaveFrame(self,simuNO = 0):
        saveData = []
        for point in self.pointsList:
            '''Angle, Speed, X_position, Y_position, Target'''
            point = self.AddNoise(point)   #加入观测噪声
            saveData.append([point.posAngle,point.speed,point.x, point.y,point.flag])
        savePath = "./simufile"+str(simuNO)+"/frame_" + str(self.frameNo) + '.txt'
        np.savetxt(savePath,saveData,fmt='%.3f')

    '''加入距离与角度测量误差'''
    def AddNoise(self,point):
        point.x = point.x + round(random.gauss(mu=0,sigma=0.1),2)
        point.y = point.y + round(random.gauss(mu=0, sigma=0.1),2) #距离参数误差符合mu=0,sigma=0.1的高斯分布
        point.posAngle = round(math.atan(point.x / (point.y + 0.0001)), 3)
        point.posAngle = point.posAngle + round(random.gauss(mu=0, sigma=0.1),3)#角度参数误差符合mu=0,sigma=0.1的高斯分布
        return point

'''仿真文件生成类'''
class SimuData:
    def __init__(self,autoTestEn = False):
        global AUTOTESTEN
        AUTOTESTEN = autoTestEn
        self.frame = []
        if autoTestEn == False:
            self.realTrackNum = input("产生的真实航迹的个数：")
            self.fakeTrackNum = input("虚假点迹数量（帧）：")
            self.frameNum = input("仿真数据帧数：")
        else:
            self.realTrackNum = AUTOTESTSET["realTrackNum"]
            self.fakeTrackNum = AUTOTESTSET["fakeTrackNum"]
            self.frameNum = AUTOTESTSET["frameNum"]
        FrameInformation = FrameInfor(self.realTrackNum,self.fakeTrackNum)

        self.frame.append(FrameInformation)

    '''新建仿真文件'''
    def CreateSimu(self):
        for i in range(int(self.frameNum)):
            FrameInformation = FrameInfor(self.realTrackNum,self.fakeTrackNum,frameNo=i+1,lastFrame=self.frame[-1])
            FrameInformation.CreatFrame()
            self.frame.append(FrameInformation)

    '''显示仿真数据'''
    def ShowSimu(self):
        # plt.ion()'''按帧显示'''
        # for frame in self.frame:
        #     for point in frame.pointsList:
        #         plt.scatter(point.x, point.y, c=point.color,s =5)
        #     plt.xlim((-30, 30))
        #     plt.ylim((0, 40))
        #     plt.pause(0.001)
        #     plt.cla()  # 清屏
        plt.figure(figsize=(5, 40),dpi=100)

        for frame in self.frame:
            for point in frame.pointsList:
                plt.scatter(point.x, point.y, c=point.color,s =point.size, marker=point.marker)
        plt.vlines(x=[-5.5, -1.8, 1.8, 5.5], ymin=0, ymax=40, colors='yellow')#画出车道线
        plt.xlabel("X(m)")
        plt.ylabel("Y(m)")
        plt.xlim((-7, 7))
        plt.ylim((0, 40))
        plt.show()
        plt.pause(0)

    '''保存仿真文件'''
    def SaveSimu(self,simuNO = 0):
        simuPath = "./simufile" + str(simuNO)
        MkDir(simuPath)
        for frame in self.frame:
            frame.SaveFrame(simuNO)
