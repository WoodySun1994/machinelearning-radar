#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.09
#功能：显示选择的航迹并加入虚假点
#auther： woody sun
'''

import random
import pandas as pd
import numpy as np
import scipy.io as io
import matplotlib.pyplot as plt

'''
    新建临时航迹列表
   Angle  Speed  Target  X_position  Y_position
0    0.0    0.0     0.0         0.0         0.0
1    0.0    0.0     0.0         0.0         0.0
2    0.0    0.0     0.0         0.0         0.0
…   ……  ……    ……      ………      ………
19   0.0    0.0     0.0         0.0         0.0
20   0.0    0.0     0.0         0.0         0.0
'''
data = np.zeros((20,5))
listname = ['Angle','Speed','Target','X_position','Y_position']
tmp_tracks_list = pd.DataFrame(data = data,columns = listname)

'''临时航迹数'''
tmp_tracks_total = 0

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
def FeatureCreat(save_en = True,plot_en = True):
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
        FackPoints = FackPointsGene(10)
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
        pass
    return tar_infor

'''临时航迹关联函数'''
# 将当前点与已经存在的临时航迹列表进行比较，返回匹配后的航迹号。若无匹配航迹则返回-1
#输入：frame_infor当前点信息   tmp_tracks_list临时航迹列表   tmp_tracks_total临时航迹数量
#输出：匹配的航迹号Tarck_rela，若无匹配则Tarck_rela返回-1
def TarckRelate(frame_infor,tmp_tracks_list, tmp_tracks_total):
    Tarck_rela = -1
    for i in range(tmp_tracks_total):                                #与临时航迹列表相继匹配
        speed = tmp_tracks_list.at[i, 'Speed']
        X_position = tmp_tracks_list.at[i, 'X_position']
        Y_position = tmp_tracks_list.at[i, 'Y_position']

        tmp = frame_infor[(frame_infor['Speed'] > speed - 3) & (frame_infor['Speed'] < speed + 3)]
        tmp = tmp[(tmp['X_position'] > X_position - 1) & (tmp['X_position'] < X_position + 1)]
        tmp = tmp[(tmp['Y_position'] > Y_position - 1) & (tmp['Y_position'] < Y_position + 1)]
        if tmp.shape[0] == 1:
            Tarck_rela = tmp_tracks_list.index[i]
        elif tmp.shape[0] > 1:
            pass  #当有多个匹配目标时
        else:
            pass
    return Tarck_rela

'''临时航迹新建函数'''
# 如果当前点和已存在的所有航迹都不匹配，则重新建立一条新的航迹，返回临时航迹列表
#输入：cur_tar 当前目标点信息，track_infor临时航迹信息列表，cur_tracknum当前临时列表航迹数
#输出：更新后的临时航迹列表
def TrackDevelop(cur_tar,track_infor,cur_tracknum):
    track_infor[cur_tracknum, 2: 7] = cur_tar[2: 7]#保存特征信息
    track_infor[cur_tracknum, 1] = 2#新建航迹的饥饿值为2
    track_infor[cur_tracknum, 0] = cur_tracknum#临时航号为临时航迹列表最后一个的值
    track_infor[cur_tracknum, 7] = 0#确定航迹号为0
    track_infor[cur_tracknum, 8: 10] = cur_tar[0: 2]#保存帧号信息
    return track_infor

'''临时航迹信息更新函数'''
#更新临时航迹表中对应航迹的最新点的特征，并增加对应航迹的饥饿值，返回更新后的临时航迹列表
#输入：cur_tar当前目标点信息，track_infor临时航迹列表，cur_tracknum当前临时航迹列表中航迹数量TrackRelaFlag匹配成功的临时航迹号
#输出：更新后的临时航迹表
def TrackFeed(cur_tar,track_infor,cur_tracknum,TrackRelaFlag):
    for i in range (0,cur_tracknum):
        if (i == TrackRelaFlag):    #对匹配成功的航迹
            track_infor[i, 2: 7] = cur_tar[2: 7]#更新匹配航迹信息
            track_infor[i, 8: 10] = cur_tar[0: 2]
            track_infor[i, 1] = track_infor[i, 1] + 4#饥饿值加4
            if (track_infor[i, 1] > 10):#饥饿值最多10
                track_infor[i, 1] = 10
        else:
            track_infor[i, 1] = track_infor[i, 1] - 1#饥饿值减1
    return track_infor

'''确定航迹信息保存函数'''
#当临时航迹列表中的航迹饥饿值达到10时，则认为是一条确定航迹，保存所有与此航迹匹配的航迹点的信息
#输入：save_track确定航迹列表 track_infor临时航迹列表 TRACK_NO 确定航迹号
#输出：更新后的确定航迹表
def TrackSave(save_track,track_infor,TRACK_NO):    #t->track_infor
    save_track[TRACK_NO, 0] = track_infor[5]#保存确定航迹的临时航迹号
    save_track[TRACK_NO, 2: 7] = track_infor[0: 5]#保存航迹列表对应的临时航迹信息
    save_track[TRACK_NO, 7: 9] = track_infor[6: 8]#保存航迹列表对应的临时航迹信息
    return save_track


'''临时航迹信息删除函数'''
#当临时航迹饥饿值低于1时，则讲该临时航迹信息删除
#输入：track_infor临时航迹信息列表 track_no当前需要删除的临时航迹号 track_total当前临时航迹总数 endnum已删除的确定航迹数量
#输出：track_infor更新后的临时航迹表，endnum已删除的确定航迹数量
def TrackDelet(track_infor,track_no,track_total,endnum):


    return  [track_infor,endnum]

'''确定航迹绘制函数'''
#绘制确定航迹
def TrackPlot():
    pass
    return


'''航迹滤波函数'''
#滤波函数
def filter():
    pass
    return


# FeatureCreat(save_en=True, plot_en= True)
frame_infor = frameread(0)
print(frame_infor)
# for jjj in range(0, 150):  # 读入MAT中的150个数据点,如果不够则退出当前循环
#     try:
#         cur_tar = tar_infor.loc[jjj]  # 当前处理目标点信息
#         #print(cur_tar)
#     except:
#         break
