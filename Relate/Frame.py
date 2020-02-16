#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2020.2.16
#功能：雷达数据关联算法所需*真实数据*帧产生与读取等操作
#auther： woody sun
'''
import random
import pandas as pd
import numpy as np
import os
import glob
import matplotlib.pyplot as plt

'''删除所有已存在的framesfile文件'''
def DelFramesFiles():
    path = 'G:\\Graduate\\CodeForGuaduate\\pysource\\framesfile'
    fileNames = glob.glob(path + r'\*')
    for fileName in fileNames:
        try:
            os.remove(fileName)#删除文件
        except:
            try:
                os.rmdir(fileName)#删除空文件夹
            except:
                delfile(fileName)# 如果非空，删除路径下的所有文件
                os.rmdir(fileName)#删除空文件夹

'''#产生噪声点，t为每个量测产生的虚假点'''
def FackPointsGene(t):
    names = ['Angle','Speed','X_position','Y_position','Target']
    FakePoints = pd.DataFrame(data = None,columns = names)
    randomspeed = [random.randint(-8,15)for i in range(t)]
    randomypos = [round(40.0 * random.random(),3)for i in range(t)]
    randomangle = [round(random.uniform(-80,80),1) for i in range(t)]
    randomxpos = randomypos * np.tan(np.deg2rad(randomangle))

    FakePoints['Speed'] = randomspeed
    FakePoints['X_position'] = randomxpos
    FakePoints['Y_position'] = randomypos
    FakePoints['Angle'] =randomangle
    FakePoints['Target'] = 0

    return FakePoints    #返回每帧虚假点信息的dataframe

'''读取第i帧数据'''
# 读取第iii帧数据
#输入：iii数据帧号
#输出：tar_infor该帧数据
def FrameRead(iii):
    try:
        path = './framesfile/frame_' + str(iii) + '.txt'
        names = ['Angle','Speed', 'Target', 'X_position','Y_position']
        tar_infor =  pd.read_csv(path, sep=' ', names=names)
    except:
        print('Frame Read Error!')
    return tar_infor

'''#产生每帧的量测点'''
def FrameCreat(save_en = True,plot_en = True,fakerate = 20,sample_rate = 1):
    if save_en == True:#如果需要保存新的帧数据，则删除之前所有数据
        DelFramesFiles()
    tracks_no = [3, 12, 20]
    j = 0
    '''颜色设置'''
    # colors = "bgrcmykw"
    # color_index = 0

    for i in tracks_no:
            path = 'G:/Graduate/CodeForGuaduate/pysource/tracks/Tracks_' + str(i) + '.txt'
            names = ['Track_No', 'Point_No', 'Speed', 'X_position', 'Y_position', 'Alarm', 'Angle', 'Mat', 'Frame', 'Target']
            try:
                tracks = pd.read_csv(path, sep=' ', names=names)
            except:
                continue
            tracks = tracks[~tracks['Track_No'].isin([0])]  # 删除当前航迹中所有track_No中为0的点
            if i == 20:#调整航迹
                tracks['X_position'] = tracks['X_position'] - 5
                tracks['Angle'] = np.rad2deg(np.arctan(tracks['X_position'] /tracks['Y_position']))

            if j == 0:
                frame1 = tracks
                length1 = tracks.shape[0]
            elif j == 1:
                frame2 = tracks
                length2 = tracks.shape[0]
            elif j == 2:
                frame3 = tracks
                length3 = tracks.shape[0]
            j = j + 1

    frames = [frame1,frame2,frame3]
    TRACKS = pd.concat(frames, keys=['a','b','c'],sort = True)   #将三条航迹合并,并标号为a,b,c

    t = max(length1,length2,length3)#找到航迹中最多的点数

    x = []
    y = []
    fakex = []
    fakey = []
    mat = np.array([])
    j = 0 #frame帧号
    for i in range(t): #读取第i个时间量测的真实航迹
        if i % sample_rate == 0:   #根据设置的采样率1/n选择点迹
            try:
                x.append(TRACKS.loc['a']['X_position'].loc[i])
                y.append(TRACKS.loc['a']['Y_position'].loc[i])
            except:
                pass
            try:
                x.append(TRACKS.loc['b']['X_position'].loc[i])
                y.append(TRACKS.loc['b']['Y_position'].loc[i])
            except:
                pass
            try:
                x.append(TRACKS.loc['c']['X_position'].loc[i])
                y.append(TRACKS.loc['c']['Y_position'].loc[i])
            except:
                pass
            #产生仿真虚假航迹，默认每帧噪点数为20
            FackPoints = FackPointsGene(fakerate)
            fakex.append(FackPoints['X_position'])
            fakey.append(FackPoints['Y_position'])
            # '''保存mat文件'''
            try:
                infr1 = TRACKS.loc['a'].loc[i]
            except:
                pass

            try:
                infr2 = TRACKS.loc['b'].loc[i]
            except:
                pass
            try:
                infr3 = TRACKS.loc['c'].loc[i]
            except:
                pass

            INFR_T = pd.concat([infr1, infr2, infr3], axis = 1, sort=True)
            INFR_T = INFR_T.T   #将点集转置
            names = ['Angle','Speed', 'X_position', 'Y_position', 'Target']
            INFR_T = INFR_T[names]
            INFR_T['Target'] = 1

            infr4 = FackPoints
            INFR = pd.concat([INFR_T,infr4], axis = 0, sort=True,ignore_index= True)
            #print(INFR)
            if save_en == True:
                frame_path = 'G:\\Graduate\\CodeForGuaduate\\pysource\\framesfile\\frame_' + str(j) + '.txt'
                np.savetxt(frame_path, INFR, fmt='%.3f')
                j = j + 1
            if plot_en == True:
                plt.ion()
                plt.scatter(x, y, s=15, c='r')
                plt.scatter(fakex, fakey, s=5,c = 'gray')
                plt.xlim((-10, 10))
                plt.ylim((0, 30))
                plt.pause(0.001)
                plt.cla()#清屏
        else:
            continue

        del x[:]
        del y[:]
        del fakex[:]
        del fakey[:]
    return

'''读取仿真数据'''
def SimuFrameRead(jjj,iii):
    Simupath = './radar_infor_sim/simufile'+ str(jjj)+'/frame_' + str(iii) + '.txt'
    names = ['Angle','Speed', 'X_position','Y_position', 'Target']
    try:
        frame_infor = pd.read_csv(Simupath, sep=' ', names=names)
    except:
        print('Frame Read Error!')
    return frame_infor
