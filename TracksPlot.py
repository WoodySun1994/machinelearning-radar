#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.06
#功能：显示选择的航迹并加入虚假点
#auther： woody sun
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import random
import pandas as pd
import matplotlib.pyplot as plt

#产生噪声点，t为产生的虚假点数
def FackPointsGene(t):
    names = ['Speed','X_position','Y_position','Angle','Target']
    FakePoints = pd.DataFrame(data = None,columns = names)
    randomspeed = [random.randint(-8,15)for i in range(t)]
    randomxpos = [round(10.0 * random.uniform(-1,1),3)for i in range(t)]
    randomypos = [round(40.0 * random.random(),3)for i in range(t)]
    randomangle = [round(random.uniform(-30,70),1) for i in range(t)]

    FakePoints['Speed'] = randomspeed
    FakePoints['X_position'] = randomxpos
    FakePoints['Y_position'] = randomypos
    FakePoints['Angle'] =randomangle
    FakePoints['Target'] = 0

    return FakePoints    #返回虚假点


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
TRACKS = pd.concat(frames, keys=['a','b','c'],sort = True)   #将三条航迹合并

t = max(length1,length2,length3)

x = []
y = []
fakex = []
fakey = []
for i in range(t):
    #读取第i个时间量测的真实航迹
    try:
        x.append(TRACKS.loc['a']['X_position'].iloc[i])
        y.append(TRACKS.loc['a']['Y_position'].iloc[i])
    except:
        pass
    try:
        x.append(TRACKS.loc['b']['X_position'].iloc[i])
        y.append(TRACKS.loc['b']['Y_position'].iloc[i])
    except:
        pass
    try:
        x.append(TRACKS.loc['c']['X_position'].iloc[i])
        y.append(TRACKS.loc['c']['Y_position'].iloc[i])
    except:
        pass
    #产生仿真虚假航迹，每帧噪点数为100
    FackPoints = FackPointsGene(100)
    fakex.append(FackPoints['X_position'])
    fakey.append(FackPoints['Y_position'])
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

