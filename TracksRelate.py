#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.20
#功能：显示选择的航迹并加入虚假点
#auther： woody sun
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import Frame

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

'''最邻近算法'''
# 在从量测波们内选取离输入坐标点距离最近的量测
#输入：tmp_points量测波门内候选点迹   last_xpos，last_ypos该航迹上一量测的坐标
#输出：tmp_points.iloc[[pointno]]  选取到的最临近点
def NN(tmp_points, last_xpos, last_ypos):
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
    Track_rela = -1
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
            Track_rela = tmp_tracks_list.index[i]
        elif tmp.shape[0] >1:
            Track_rela = tmp_tracks_list.index[i]
            tmp = NN(tmp, tmp_tracks_list.at[i, 'X_position'], tmp_tracks_list.at[i, 'Y_position'])

        tmp_tracks_list.iloc[[Track_rela],0] = tmp_tracks_list.iloc[[Track_rela],0] + 3#更新hung值
        if tmp_tracks_list.iat[Track_rela,0] > 7:  #hung值最大为7
             tmp_tracks_list.iat[Track_rela,0] = 7
        tmp_tracks_list.iloc[[Track_rela],1:] = tmp.values   #将匹配点的信息加入临时航迹列表
        frame_infor = frame_infor.drop(tmp.index)            #从帧数据中删除匹配成功的航迹点
    tmp_tracks_list['hung'] = tmp_tracks_list['hung'] - 1#所有航迹饥饿值-1
    return [frame_infor,tmp_tracks_list]

'''临时航迹新建函数'''
# 如果当前点和已存在的所有航迹都不匹配，则重新建立一条新的航迹，返回临时航迹列表
#输入：frame_infor 当前帧目标点信息，tmp_tracks_list临时航迹信息列表
#输出：更新后的[tmp_tracks_list,tmp_tracks_total]
def TrackDevelop(frame_infor,tmp_tracks_list,tmp_tracks_total):
    newname = ['hung','Angle','Speed','Target','X_position','Y_position']
    tmp_frame_infor = frame_infor.reindex(columns = newname,fill_value = 2)    #设置所有新建航迹的饥饿值为2
    new_tmp_tracks = [tmp_tracks_list,tmp_frame_infor]
    tmp_tracks_list = pd.concat(new_tmp_tracks,ignore_index = True)             #将新建航迹加入临时航迹列表
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
# frame_infor 当前帧目标点信息
def TrackPlotXY(frame_infor,tmp_tracks_list):
    plot_point_list = tmp_tracks_list[tmp_tracks_list['hung'] > 5]#选择出饥饿值大于5的所有点
    fake_plot_list = plot_point_list[plot_point_list['Target']  == 0]#选择其中的错误关联点
    real_plot_list = plot_point_list[plot_point_list['Target']  == 1]#选择其中的正确关联点

    miss_plot_list = frame_infor[frame_infor['Target'] == 1]   #选择其中漏警的数据点

    missx = miss_plot_list.loc[:,'X_position']
    missy = miss_plot_list.loc[:,'Y_position']
    fakex = fake_plot_list.loc[:,'X_position']
    fakey = fake_plot_list.loc[:,'Y_position']
    x = real_plot_list.loc[:,'X_position']
    y = real_plot_list.loc[:,'Y_position']

    return [x,y,fakex,fakey,missx,missy]

'''航迹滤波函数'''
#滤波函数
def filter():
    pass
    return


Frame.FrameCreat(save_en=True, plot_en= True, fakerate = 50, sample_rate = 5)

total_frame = 55
process_output = sys.stdout
for i in range(total_frame):
    frame_infor = Frame.FrameRead(i)
    count = i/(total_frame-1)*100
    process_output.write(f'\r PROCESSING percent:{count:.0f}%')
    [frame_infor,tmp_tracks_list] = TarckRelate(frame_infor, tmp_tracks_list, tmp_tracks_total)
    [tmp_tracks_list, track_total] = TrackDelet(tmp_tracks_list, tmp_tracks_total)
    [tmp_tracks_list, tmp_tracks_total] = TrackDevelop(frame_infor, tmp_tracks_list, tmp_tracks_total)

    [x, y, fakex, fakey,missx,missy] = TrackPlotXY(frame_infor,tmp_tracks_list)

    plt.scatter(x, y, s=15, c='r')
    plt.scatter(fakex, fakey, s=15,c = 'gray',marker='x')
    plt.scatter(missx, missy, s=15,c = 'g',marker='x')
#plt.ion()
process_output.flush
plt.xlim((-10, 10))
plt.ylim((0, 30))

#plt.cla()#清屏
plt.show()
plt.pause(0)