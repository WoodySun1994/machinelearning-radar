#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.10
#功能：显示选择的航迹并加入虚假点
#auther： woody sun
'''

import random
import pandas as pd
import numpy as np
import scipy.io as io
import matplotlib.pyplot as plt
import math

'''
    新建临时航迹列表
    hung   Angle  Speed  Target  X_position  Y_position
0    0.0    0.0     0.0    0.0     0.0         0.0
1    0.0    0.0     0.0    0.0     0.0         0.0
…   ……  ……    ……      ………      ………
4   0.0    0.0     0.0    0.0     0.0         0.0
'''
data = np.zeros((5,6))
listname = ['hung','Angle','Speed','Target','X_position','Y_position']
tmp_tracks_list = pd.DataFrame(data = data,columns = listname)

'''临时航迹数'''
tmp_tracks_total = 5

#产生噪声点，t为每个量测产生的虚假点
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
def FrameCreat(save_en = True,plot_en = True,fakerate = 20):
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
            frame_path = 'G:\\Graduate\\CodeForGuaduate\\pysource\\featuresfile\\frame_' + str(i) + '.txt'
            np.savetxt(frame_path, INFR, fmt='%.3f')
        if plot_en == True:
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
    return

#读取第i帧数据 return tar_infor
def frameread(iii):
    try:
        path = './featuresfile/frame_' + str(iii) + '.txt'
        names = ['Angle','Speed', 'Target', 'X_position','Y_position']
        tar_infor =  pd.read_csv(path, sep=' ', names=names)
    except:
        print('Frame Read Error!')
    return tar_infor

#最邻近算法
def NN(tmp_points, last_xpos, last_ypos):#最邻近算法

    dis = math.pow(tmp_points.iloc[0].loc['X_position'] - last_xpos, 2) + math.pow(tmp_points.iloc[0].loc['Y_position'] - last_ypos,2)
    pointno = 0
    for i in range(1, tmp_points.shape[0]):
        dis1 = math.pow(tmp_points.iloc[i].loc['X_position'] - last_xpos, 2) + math.pow(tmp_points.iloc[i].loc['Y_position'] - last_ypos, 2)
        if dis1 < dis:
            dis = dis1
            pointno = i
    return tmp_points.iloc[[pointno]]

'''临时航迹关联函数'''
# 将当前点与已经存在的临时航迹列表进行比较，返回匹配后的航迹号。若无匹配航迹则返回-1
#输入：frame_infor当前点信息   tmp_tracks_list临时航迹列表   tmp_tracks_total临时航迹数量
#输出：更新后的[frame_infor,tmp_tracks_list]
def TarckRelate(frame_infor,tmp_tracks_list, tmp_tracks_total):
    Tarck_rela = -1
    for i in range(tmp_tracks_total):                                #与临时航迹列表相继匹配
        speed = tmp_tracks_list.at[i, 'Speed']
        X_position = tmp_tracks_list.at[i, 'X_position']
        Y_position = tmp_tracks_list.at[i, 'Y_position']

        tmp = frame_infor[(frame_infor['Speed'] > speed - 3) & (frame_infor['Speed'] < speed + 3)]
        tmp = tmp[(tmp['X_position'] > X_position - 1) & (tmp['X_position'] < X_position + 1)]
        tmp = tmp[(tmp['Y_position'] > Y_position - 1) & (tmp['Y_position'] < Y_position + 1)]

        if tmp.shape[0] == 0:  #当没有匹配目标时
            continue
        elif tmp.shape[0] == 1:
            Tarck_rela = tmp_tracks_list.index[i]
        elif tmp.shape[0] >1:
            tmp = NN(tmp, tmp_tracks_list.at[i, 'X_position'], tmp_tracks_list.at[i, 'Y_position'])

        tmp_tracks_list.iloc[[Tarck_rela],0] = tmp_tracks_list.iloc[[Tarck_rela],0] + 3#更新hung值
        tmp_tracks_list.iloc[[Tarck_rela],1:] = tmp.values   #将匹配点的信息加入临时航迹列表
        frame_infor = frame_infor.drop(tmp.index)
    tmp_tracks_list['hung'] = tmp_tracks_list['hung'] - 1#所有航迹饥饿值-1
    return [frame_infor,tmp_tracks_list]



'''临时航迹新建函数'''
# 如果当前点和已存在的所有航迹都不匹配，则重新建立一条新的航迹，返回临时航迹列表
#输入：frame_infor 当前帧目标点信息，tmp_tracks_list临时航迹信息列表
#输出：更新后的[tmp_tracks_list,tmp_tracks_total]
def TrackDevelop(frame_infor,tmp_tracks_list,tmp_tracks_total):
    newname = ['hung','Angle','Speed','Target','X_position','Y_position']
    tmp_frame_infor = frame_infor.reindex(columns = newname,fill_value = 2)    #所有新建航迹的饥饿值
    new_tmp_tracks = [tmp_tracks_list,tmp_frame_infor]
    tmp_tracks_list = pd.concat(new_tmp_tracks,ignore_index = True)
    tmp_tracks_total = tmp_tracks_list.shape[0]
    return [tmp_tracks_list,tmp_tracks_total]

'''临时航迹信息删除函数'''
#当临时航迹饥饿值低于1时，则将该临时航迹信息删除
#输入：tmp_tracks_list临时航迹信息列表 track_total当前临时航迹总数
#输出：更新后的[frame_infor,track_total]
def TrackDelet(tmp_tracks_list,tmp_tracks_total):
    tmp_tracks_list = tmp_tracks_list[tmp_tracks_list['hung'] > 0]
    tmp_tracks_list.index = range(tmp_tracks_list.shape[0])
    tmp_tracks_total = tmp_tracks_list.shape[0]
    return [tmp_tracks_list,tmp_tracks_total]

'''确定航迹坐标返回函数'''
#绘制确定航迹
def TrackPlotXY(tmp_tracks_list):
    plot_point_list = tmp_tracks_list[tmp_tracks_list['hung'] > 5]#选择出饥饿值大于5的所有点
    fake_plot_list = plot_point_list[plot_point_list['Target']  == 0]
    real_plot_list = plot_point_list[plot_point_list['Target']  == 1]

    fakex = fake_plot_list.loc[:,'X_position']
    fakey = fake_plot_list.loc[:,'Y_position']
    x = real_plot_list.loc[:,'X_position']
    y = real_plot_list.loc[:,'Y_position']

    return [x,y,fakex,fakey]


'''航迹滤波函数'''
#滤波函数
def filter():
    pass
    return


#FrameCreat(save_en=True, plot_en= True, fakerate = 50)

for i in range(10):
    frame_infor = frameread(i)
    [frame_infor,tmp_tracks_list] = TarckRelate(frame_infor, tmp_tracks_list, tmp_tracks_total)
    [tmp_tracks_list, track_total] = TrackDelet(tmp_tracks_list, tmp_tracks_total)
    [tmp_tracks_list, tmp_tracks_total] = TrackDevelop(frame_infor, tmp_tracks_list, tmp_tracks_total)

    [x, y, fakex, fakey] = TrackPlotXY(tmp_tracks_list)


    plt.scatter(x, y, s=15, c='r')
    plt.scatter(fakex, fakey, s=15,c = 'gray',marker='x')
#plt.ion()
plt.xlim((-10, 10))
plt.ylim((0, 30))
#plt.pause(0.001)
#plt.cla()#清屏
plt.show()
