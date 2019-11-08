#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.08
#功能：仿真产生量测数据，并按帧保存为mat文件
#auther： woody sun
'''

import random
import pandas as pd
import numpy as np
import scipy.io as io
import matplotlib.pyplot as plt

#产生噪声点，t为每个量测产生的虚假点数
def FackPointsGene(t):
    names = ['Angle','Speed','X_position','Y_position','Target']
    FakePoints = pd.DataFrame(data = None,columns = names)
    randomspeed = [random.randint(-8,15)for i in range(t)]
    randomxpos = [round(10.0 * random.uniform(-1,1),3)for i in range(t)]
    randomypos = [round(40.0 * random.random(),3)for i in range(t)]
    randomangle = [round(random.uniform(-30,30),1) for i in range(t)]

    FakePoints['Speed'] = randomspeed
    FakePoints['X_position'] = randomxpos
    FakePoints['Y_position'] = randomypos
    FakePoints['Angle'] =randomangle
    FakePoints['Target'] = 0

    return FakePoints    #返回虚假点

#产生每帧的量测点
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
for i in range(t):
    #读取第i个时间量测的真实航迹
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
    #产生仿真虚假航迹，每帧噪点数为10
    FackPoints = FackPointsGene(100)
    fakex.append(FackPoints['X_position'])
    fakey.append(FackPoints['Y_position'])
    # '''保存mat文件'''
    try:
        mat1 = TRACKS.loc['a'].loc[i]
    except:
        pass

    try:
        mat2 = TRACKS.loc['b'].loc[i]
    except:
        pass
    try:
        mat3 = TRACKS.loc['c'].loc[i]
    except:
        pass
    MATS_T = pd.concat([mat1, mat2, mat3], axis = 1, sort=True)
    MATS_T = MATS_T.T   #将点集转置
    names = ['Angle','Speed', 'X_position', 'Y_position', 'Target']
    MATS_T = MATS_T[names]
    MATS_T['Target'] = 1

    mat4 = FackPoints
    MAT = pd.concat([MATS_T,mat4], axis = 0, sort=True,ignore_index= True)

    plt.ion()
    plt.scatter(x, y, s=15, c='r')
    plt.scatter(fakex, fakey, s=5,c = 'gray')
    plt.xlim((-10, 10))
    plt.ylim((0, 30))
    plt.pause(0.001)
    plt.cla()#清屏

    del x[:]
    del y[:]
    del fakex[:]
    del fakey[:]

    mat_path = 'G:\\Graduate\\CodeForGuaduate\\pysource\\featuresfile\\frame_' + str(i) + '.mat'
    io.savemat(mat_path, {'featuer_save': MAT})

