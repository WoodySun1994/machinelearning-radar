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

def mk_dir(path):
    '''根据path参数新建文件夹'''
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        pass

def Auto_test_data_gne(realtracknum):
    '''自动测试数据生成器，输入参数为需要产生的真实航迹数量'''
    autotestdata  = []
    for i in range(realtracknum):
        point = {}
        point["movtype"] = random.choice(['UT','AL','UL'])
        point["x"] = 30 * round(random.uniform(-1,1),2)
        point["y"] = 40 * round(random.random(),2)
        point["speed"] = 5 * round(random.uniform(0.5,1),2)
        point["angle"] = 30 * round(random.uniform(-1,1),3)
        if point["movtype"] == 'AL':
            point["accelerate"]  = round(0.5 * random.random(),2)
        else:
            point["accelerate"] = 0
        autotestdata.append(point)
    return autotestdata

AUTOTESTEN = True   #自动测试
AUTOTESTSET = {'realtracknum': 6, 'faketracknum':100, 'framenum':10}


'''
AUTOTESTDATA = [{'movtype':'UT', "x":-12.0, "y":30.0,'speed':3.5, 'angle':-10, 'accelerate':0},
            {'movtype':'UT', "x":12, "y":37.0,'speed':4.5, 'angle': 8, 'accelerate':0},
            {'movtype':'AL', "x":10.0, "y":36.0,'speed':2.5, 'angle':0, 'accelerate':0.37},
            {'movtype':'AL', "x": 20.0, "y":15.0,'speed':2, 'angle': 20, 'accelerate':0.43},
            {'movtype':'UL', "x":0.0, "y":39.0,'speed':5, 'angle': 30, 'accelerate':0},
            {'movtype':'UL', "x":18.50, "y":25.0,'speed':3.5, 'angle': -10, 'accelerate':0}
            ]
'''

class FrameInfor:
    def __init__(self,realtracknum = 5, faketracknum = 10, frameno  = 0,lastframe = None):
        self.points_list = []
        self.realtracknum = realtracknum
        self.faketracknum = faketracknum
        self.frameno = frameno

        if lastframe == None :#第一帧数据由用户给出
            for i in range(int(self.realtracknum)):
                if AUTOTESTEN == False:#非自动测试的情况下，需要用户手动输入运动参数
                    print("第", i + 1, "个航迹的运动类型(UL,AL,UT)：", end='')
                    movtype = input()
                    if movtype != 'UL' and movtype != 'AL' and movtype != 'UT':
                        raise Exception("Wrong Move Type!")

                    print("第", i + 1, "个航迹的x坐标（-30~30）：", end='')
                    x = float(input())
                    print("第", i + 1, "个航迹的y坐标（0~40）：", end='')
                    y = float(input())
                    print("第", i + 1, "个航迹的初始速度：", end='')
                    speed = float(input())
                    print("第", i + 1, "个航迹的运动角度(-0.2~0.2)：", end='')
                    angle = float(input())
                    if movtype == 'AL':
                        print("第", i + 1, "个航迹的加速度：", end='')
                        accelerate = float(input())
                    else:
                        accelerate = 0.0
                else:#自动测试时读取参数列表作为仿真数据来源
                    AutoTestData = Auto_test_data_gne(AUTOTESTSET['realtracknum'])
                    movtype = AutoTestData[i]["movtype"]
                    x = AutoTestData[i]["x"]
                    y = AutoTestData[i]["y"]
                    speed = AutoTestData[i]["speed"]
                    angle = AutoTestData[i]["angle"]
                    accelerate = AutoTestData[i]["accelerate"]

                RP = Point.RealPtGenerator(x, y, movtype, speed, accelerate, angle)
                self.points_list.append(RP)

            for i in range(int(self.faketracknum)):
                FP = Point.FakePtGenerator()
                self.points_list.append(FP)
        else:
            self.lastframe = lastframe

    def creat_frame(self):
        for point in self.lastframe.points_list:
            if point.flag == 1:  #如果当前点为真实点，则将改点传入对应的真实点产生函数中
                RP = Point.RealPtGenerator(point.x, point.y, point.movetype, point.speed,point.accelerate,point.angle)
                RP = self.add_noise(RP)
                self.points_list.append(RP)

            else:#如果当前点为虚假点，则调用虚假点产生函数
                FP = Point.FakePtGenerator()
                self.points_list.append(FP)

    def show_frame(self):
        for point in self.points_list:
            print("(x,y): (",point.x,",",point.y,")" , "   speed:" , point.speed , "  angle:" ,point.angle)
            plt.scatter(point.x, point.y, c=point.color)
        plt.xlim((-30, 30))
        plt.ylim((0, 40))
        plt.show()

    def save_frame(self,simuno = 0):
        savedata = []
        for point in self.points_list:
            '''Angle, Speed, X_position, Y_position, Target'''
            savedata.append([point.angle,point.speed,point.x, point.y,point.flag])
        savepath = "./simufile"+str(simuno)+"/frame_" + str(self.frameno) + '.txt'
        np.savetxt(savepath,savedata,fmt='%.3f')

    def add_noise(self,point):
        point.x = point.x + round(random.gauss(mu=0,sigma=0.1),2)  #位置参数误差符合mu=0,sigma=0.1的高斯分布
        point.y = point.y + round(random.gauss(mu=0, sigma=0.1),2)
        point.angle = point.angle + round(random.gauss(mu=0, sigma=0.8),3)#角度参数误差符合mu=0,sigma=0.8的高斯分布
        return point

class SimuData:
    def __init__(self,autotesten = False):
        global AutoTestEn
        AutoTestEn = autotesten
        self.frame = []
        if AutoTestEn == False:
            self.realtracknum = input("产生的真实航迹的个数：")
            self.faketracknum = input("虚假点迹数量（帧）：")
            self.framenum = input("仿真数据帧数：")
        else:
            self.realtracknum = AUTOTESTSET["realtracknum"]
            self.faketracknum = AUTOTESTSET["faketracknum"]
            self.framenum = AUTOTESTSET["framenum"]
        FI = FrameInfor(self.realtracknum,self.faketracknum)

        self.frame.append(FI)

    def create_simu(self):
        for i in range(int(self.framenum)):
            FI = FrameInfor(self.realtracknum,self.faketracknum,frameno=i+1,lastframe=self.frame[-1])
            FI.creat_frame()
            self.frame.append(FI)

    def show_simu(self):
        '''显示仿真数据'''
        # plt.ion()'''按帧显示'''
        # for frame in self.frame:
        #     for point in frame.points_list:
        #         plt.scatter(point.x, point.y, c=point.color,s =5)
        #     plt.xlim((-30, 30))
        #     plt.ylim((0, 40))
        #     plt.pause(0.001)
        #     plt.cla()  # 清屏

        for frame in self.frame:
            for point in frame.points_list:
                plt.scatter(point.x, point.y, c=point.color,s =point.size)
        plt.xlim((-30, 30))
        plt.ylim((0, 40))
        plt.show()
        plt.pause(0)

    def save_simu(self,simuno = 0):
        simupath = "./simufile" + str(simuno)
        mk_dir(simupath)
        for frm in self.frame:
            frm.save_frame(simuno)
