#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.08
#功能：主程序
#auther： woody sun
'''

import pandas as pd
import matplotlib.pyplot as plt
plt.ion()


# 采集航迹点
plot_en = 1  # 设置是否需要画出航迹
track_total = 35  # 设置需要采集的航迹数量

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
for i in range(t):#输出所有序列

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
    plt.scatter(x, y, s=5,c = 'b')
    plt.xlim((-10, 10))
    plt.ylim((0, 30))
    plt.pause(0.001)


