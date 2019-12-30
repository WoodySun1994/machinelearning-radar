#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.26
#功能：产生仿真帧数据
#auther： woody sun
'''

import Point
import  matplotlib.pyplot as plt
import numpy as np
import random
import os


AUTOTESTEN = True   #自动测试
AUTOTESTSET = {'realTrackNum': 6, 'fakeTrackNum':300, 'frameNum':10}

def MkDir(path):
    '''根据path参数新建文件夹'''
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        pass

def AutoTestDataGen(realTrackNum):
    '''自动测试数据生成器，输入参数为需要产生的真实航迹数量'''
    autoTestData  = []
    for i in range(realTrackNum):
        point = {}
        point["movType"] = random.choice(['UT','AL','UL'])
        point["x"] = 30 * round(random.uniform(-1,1),2)
        point["y"] = 40 * round(random.random(),2)
        point["speed"] = 5 * round(random.uniform(0.5,1),2)
        point["angle"] = 30 * round(random.uniform(-1,1),3)
        if point["movType"] == 'AL':
            point["accelerate"]  = round(0.5 * random.random(),2)
        else:
            point["accelerate"] = 0
        autoTestData.append(point)
    return autoTestData


'''
autoTestData = [{'movType':'UT', "x":-12.0, "y":30.0,'speed':3.5, 'angle':-10, 'accelerate':0},
            {'movType':'UT', "x":12, "y":37.0,'speed':4.5, 'angle': 8, 'accelerate':0},
            {'movType':'AL', "x":10.0, "y":36.0,'speed':2.5, 'angle':0, 'accelerate':0.37},
            {'movType':'AL', "x": 20.0, "y":15.0,'speed':2, 'angle': 20, 'accelerate':0.43},
            {'movType':'UL', "x":0.0, "y":39.0,'speed':5, 'angle': 30, 'accelerate':0},
            {'movType':'UL', "x":18.50, "y":25.0,'speed':3.5, 'angle': -10, 'accelerate':0}
            ]
'''

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

                    print("第", i + 1, "个航迹的x坐标（-30~30）：", end='')
                    x = float(input())
                    print("第", i + 1, "个航迹的y坐标（0~40）：", end='')
                    y = float(input())
                    print("第", i + 1, "个航迹的初始速度：", end='')
                    speed = float(input())
                    print("第", i + 1, "个航迹的运动角度(-0.2~0.2)：", end='')
                    angle = float(input())
                    if movType == 'AL':
                        print("第", i + 1, "个航迹的加速度：", end='')
                        accelerate = float(input())
                    else:
                        accelerate = 0.0
                else:#自动测试时读取参数列表作为仿真数据来源
                    autoTestData = AutoTestDataGen(AUTOTESTSET['realTrackNum'])
                    movType = autoTestData[i]["movType"]
                    x = autoTestData[i]["x"]
                    y = autoTestData[i]["y"]
                    speed = autoTestData[i]["speed"]
                    angle = autoTestData[i]["angle"]
                    accelerate = autoTestData[i]["accelerate"]

                RP = Point.RealPtGenerator(x, y, movType, speed, accelerate, angle)
                self.pointsList.append(RP)

            for i in range(int(self.fakeTrackNum)):
                FP = Point.FakePtGenerator()
                self.pointsList.append(FP)
        else:
            self.lastFrame = lastFrame

    def CreatFrame(self):
        for point in self.lastFrame.pointsList:
            if point.flag == 1:  #如果当前点为真实点，则将改点传入对应的真实点产生函数中
                RP = Point.RealPtGenerator(point.x, point.y, point.movetype, point.speed,point.accelerate,point.angle)
                RP = self.AddNoise(RP)
                self.pointsList.append(RP)

            else:#如果当前点为虚假点，则调用虚假点产生函数
                FP = Point.FakePtGenerator()
                self.pointsList.append(FP)

    def ShowFrame(self):
        for point in self.pointsList:
            print("(x,y): (",point.x,",",point.y,")" , "   speed:" , point.speed , "  angle:" ,point.angle)
            plt.scatter(point.x, point.y, c=point.color)
        plt.xlim((-30, 30))
        plt.ylim((0, 40))
        plt.show()

    def SaveFrame(self,simuNO = 0):
        saveData = []
        for point in self.pointsList:
            '''Angle, Speed, X_position, Y_position, Target'''
            saveData.append([point.angle,point.speed,point.x, point.y,point.flag])
        savePath = "./simufile"+str(simuNO)+"/frame_" + str(self.frameNo) + '.txt'
        np.savetxt(savePath,saveData,fmt='%.3f')

    def AddNoise(self,point):
        point.x = point.x + round(random.gauss(mu=0,sigma=0.1),2)  #位置参数误差符合mu=0,sigma=0.1的高斯分布
        point.y = point.y + round(random.gauss(mu=0, sigma=0.1),2)
        point.angle = point.angle + round(random.gauss(mu=0, sigma=0.8),3)#角度参数误差符合mu=0,sigma=0.8的高斯分布
        return point

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

    def CreateSimu(self):
        for i in range(int(self.frameNum)):
            FrameInformation = FrameInfor(self.realTrackNum,self.fakeTrackNum,frameNo=i+1,lastFrame=self.frame[-1])
            FrameInformation.CreatFrame()
            self.frame.append(FrameInformation)

    def ShowSimu(self):
        '''显示仿真数据'''
        # plt.ion()'''按帧显示'''
        # for frame in self.frame:
        #     for point in frame.pointsList:
        #         plt.scatter(point.x, point.y, c=point.color,s =5)
        #     plt.xlim((-30, 30))
        #     plt.ylim((0, 40))
        #     plt.pause(0.001)
        #     plt.cla()  # 清屏

        for frame in self.frame:
            for point in frame.pointsList:
                plt.scatter(point.x, point.y, c=point.color,s =point.size)
        plt.xlim((-30, 30))
        plt.ylim((0, 40))
        plt.show()
        plt.pause(0)

    def SaveSimu(self,simuNO = 0):
        simuPath = "./simufile" + str(simuNO)
        MkDir(simuPath)
        for frame in self.frame:
            frame.SaveFrame(simuNO)
