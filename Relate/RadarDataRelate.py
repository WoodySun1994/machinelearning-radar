#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2020.2.17
#功能：航迹关联算法
#auther： woody sun
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import Frame
import RadarMl

'''初始化临时航迹列表'''
def tmpTracksListInit():
    '''
        新建临时航迹列表
        hung   Angle   Speed    X_position  Y_position  Target RelateFlag
    0    0.0    0.0     0.0       0.0         0.0        0.0      0.0
    1    0.0    0.0     0.0       0.0         0.0        0.0      0.0
    …   ……  ……    ……      ………      ………
    9    0.0    0.0     0.0       0.0         0.0        0.0      0.0
    '''
    data = np.zeros((10,7))
    colName = ['hung','Angle','Speed','X_position','Y_position','Target','RelateFlag']
    tmpTracksList = pd.DataFrame(data = data,columns = colName)

    totalTmpTracks = 10 #临时航迹数
    return tmpTracksList,totalTmpTracks

'''初始化暂存点迹列表'''
#由于一些点在确定航迹建立过程中饥饿值未满足画图的需求，但是最终是需要画出来的，所以用一个列表存储这些点的信息，画完确定的点和信息后删除
def tmpStoragePointsInit():
    '''
           新建暂存点迹信息列表
           tmpTracksNo     X_position  Y_position  Target
       0    -1                 -1          -1        -1
    '''
    data = -1*np.ones((1, 4))
    colName = ['tmpTracksNo', 'X_position', 'Y_position', 'Target']
    tmpStoragePoints = pd.DataFrame(data=data, columns=colName)
    totalTmpStoragePoints = 0
    return tmpStoragePoints,totalTmpStoragePoints


'''最邻近算法'''
# 在从量测波们内选取离输入坐标点距离最近的量测
#输入：tmpRelatePoints落在量测波门内候选点迹   lastXPos，lastYPos该航迹上一量测的坐标
#输出：tmpRelatePoints.iloc[[pointNo]]  选取到的最临近点
def NN(tmpRelatePoints, lastXPos, lastYPos):
    dis = math.pow(tmpRelatePoints.iloc[0].loc['X_position'] - lastXPos, 2) + math.pow(tmpRelatePoints.iloc[0].loc['Y_position'] - lastYPos,2)
    pointNo = 0
    for i in range(1, tmpRelatePoints.shape[0]):
        dis1 = math.pow(tmpRelatePoints.iloc[i].loc['X_position'] - lastXPos, 2) + math.pow(tmpRelatePoints.iloc[i].loc['Y_position'] - lastYPos, 2)
        if dis1 < dis:
            dis = dis1
            pointNo = i
    return tmpRelatePoints.iloc[[pointNo]]

'''临时航迹关联函数（加入机器学习的逻辑法）'''
# 将当前帧落入波门中的点与已经存在的临时航迹列表进行比较，返回匹配后的航迹号，并更新临时保存点列表。若无匹配航迹则返回-1
#输入：frameInfor当前帧所有量测点信息   tmpTracksList临时航迹列表   totalTmpTracks临时航迹数量    tmpStoragePoints临时点信息列表  totalTmpStoragePoints临时点个数
#输出：更新后的[frameInfor,tmpTracksList,tmpStoragePoints,totalTmpStoragePoints]
def TrackRelate(frameInfor,tmpTracksList, totalTmpTracks, tmpStoragePoints, totalTmpStoragePoints,mlModel = None,machineLearnEnable = True):
    TrackRelaNo = -1
    tmpTracksList['RelateFlag'] = 0  #所有临时航迹关联标志位置0
    # mlMissPoints = pd.DataFrame([], columns=['Angle', 'Speed', 'X_position', 'Y_position', 'Target'])
    for tmpTrackNo in range(totalTmpTracks):                                #与临时航迹列表所有目标相继匹配
        speed = tmpTracksList.at[tmpTrackNo, 'Speed']
        X_position = tmpTracksList.at[tmpTrackNo, 'X_position']
        Y_position = tmpTracksList.at[tmpTrackNo, 'Y_position']

        #寻找当前临时航迹速度与距离波门内所有目标点
        tmp = frameInfor[(frameInfor['Speed'] > speed - 0.7) & (frameInfor['Speed'] < speed + 0.7)]#速度波门限值
        tmp = tmp[(tmp['X_position'] > X_position - 0.7) & (tmp['X_position'] < X_position + 0.7)]      #距离波门限值
        tmp = tmp[(tmp['Y_position'] > Y_position - 2) & (tmp['Y_position'] < Y_position + 0.2)]

        # if machineLearnEnable == True and tmp.shape[0] >1: #当有多个目标在波门范围内时，使用机器学习算法分类
        #      tmp, mlMissPoints = mlModel.Applicate(tmp,scale_en = True)

        if tmp.shape[0] == 0:  #当没有目标落在波门范围内时
            tmpTracksList.iloc[[tmpTrackNo], 0] = - 1   # 未匹配成功的航迹饥饿值-1

            deletTmpPoint = tmpStoragePoints[tmpStoragePoints['tmpTracksNo'] == tmpTrackNo]      #删除临时点迹列表中航迹号对应的所有临时点
            tmpStoragePoints = tmpStoragePoints.drop(deletTmpPoint.index)
            totalTmpStoragePoints = tmpStoragePoints.shape[0]
            tmpStoragePoints.index = range(totalTmpStoragePoints)                                #临时点迹列表重新排列
            continue                                                                             #继续检查临时航迹列表中下一个航迹
        elif tmp.shape[0] == 1:                    #当只有一个目标落在波门范围内时
            TrackRelaNo = tmpTracksList.index[tmpTrackNo]                                       #返回匹配上的航迹在临时列表中的航迹号
        elif tmp.shape[0] >1: #当有多个目标在波门范围内时，使用最邻近算法，选取波门内最近的目标，并返回匹配上的航迹号
            TrackRelaNo = tmpTracksList.index[tmpTrackNo]
            # tmp, mlMissPoints = mlModel.Applicate(tmp,scale_en = True)
            tmp = NN(tmp, tmpTracksList.at[tmpTrackNo, 'X_position'], tmpTracksList.at[tmpTrackNo, 'Y_position'])#最邻近算法

        tmpTracksList.iat[TrackRelaNo, 6] = 1  # 将关联成功标志位置1

        tmpTracksList.iloc[[TrackRelaNo], 0] = tmpTracksList.iloc[[TrackRelaNo], 0] + 1  # 关联成功的点hung值+1
        if tmpTracksList.iat[TrackRelaNo, 0] > 3:  # hung值最大为3
            tmpTracksList.iat[TrackRelaNo, 0] = 3
        tmpStoragePoints = tmpStoragePoints[tmpStoragePoints['tmpTracksNo'] >= 0]#删除临时点列表中航迹号不合法的点

        # 选择成功关联的点迹替换原来临时航迹中点的信息，被替换的点存入临时点列表
        data = np.zeros((1,4))   #航迹列表中被关联成功的点信息存入临时点列表
        dataFrameName = ['tmpTracksNo', 'X_position', 'Y_position', 'Target']
        newTmpPoints = pd.DataFrame(data=data, columns=dataFrameName)
        newTmpPoints['tmpTracksNo'] = TrackRelaNo
        newTmpPoints['X_position'] = tmpTracksList.at[TrackRelaNo,'X_position']
        newTmpPoints['Y_position'] = tmpTracksList.at[TrackRelaNo,'Y_position']
        newTmpPoints['Target'] = tmpTracksList.at[TrackRelaNo,'Target']
        newTmpPointsList = [tmpStoragePoints, newTmpPoints]
        tmpStoragePoints = pd.concat(newTmpPointsList,ignore_index=True)

        totalTmpStoragePoints += 1#临时点列表中个数+1

        tmpTracksList.iloc[[TrackRelaNo],1:6] = tmp.values   #将匹配点的信息加入临时航迹列表，替换原来的点信息
        frameInfor = frameInfor.drop(tmp.index)              #从帧数据中删除匹配成功的航迹点，在剩下的点中继续与其他临时航迹相匹配

    return [frameInfor,tmpTracksList, tmpStoragePoints, totalTmpStoragePoints]

'''临时航迹新建函数'''
# 如果当前帧中的量测点和已存在的所有航迹都不匹配，则重新建立一条新的航迹，返回临时航迹列表
#输入：frameInfor 当前帧目标点信息，tmpTracksList临时航迹信息列表， totalTmpTracks临时航迹个数
#输出：更新后的[tmpTracksList,totalTmpTracks]
def TrackNewDevelop(frameInfor,tmpTracksList,totalTmpTracks):
    newname = ['hung','Angle','Speed','X_position','Y_position','Target']
    frameInfor = frameInfor.reindex(columns = newname,fill_value = 1)    #设置所有新建航迹的饥饿值为1
    newname = ['hung','Angle','Speed','X_position','Y_position','Target','RelateFlag']
    tmp_frame_infor = frameInfor.reindex(columns = newname,fill_value = 0)    #设置所有新建航迹的关联标志位值为0
    new_tmp_tracks = [tmpTracksList,tmp_frame_infor]
    tmpTracksList = pd.concat(new_tmp_tracks,ignore_index = True,sort = False)  #将未成功匹配的点信息加入临时航迹列表作为新的临时航迹
    totalTmpTracks = tmpTracksList.shape[0]#更新临时航迹个数
    return [tmpTracksList,totalTmpTracks]

'''临时航迹信息删除函数'''
#当临时航迹饥饿值低于0时，则将该临时航迹信息删除并调整临时航迹号和临时点列表中所对应的临时航迹号
#输入：tmpTracksList临时航迹信息列表 totalTmpTracks当前临时航迹总数 tmpStoragePoints临时点列表  totalTmpStoragePoints临时点个数
#输出：更新后的[frameInfor,track_total, tmpStoragePoints, totalTmpStoragePoints]以及从临时航迹列表中删除的点迹delete_points信息。
# [tmpTracksList,totalTmpTracks, tmpStoragePoints, totalTmpStoragePoints,delete_points]
def TrackDelet(tmpTracksList,totalTmpTracks, tmpStoragePoints, totalTmpStoragePoints):
    tmpStoragePoints.sort_values('tmpTracksNo',inplace = True) #将临时点列表按临时航迹号重新排序
    #以下代码是根据删除无效航迹后的临时航迹的航迹号更新临时保存点迹列表
    pointsPointer = 0
    shiftValue = 0
    for tracksPointer in range(totalTmpTracks):  # 遍历临时所有临时航迹，查找饥饿值小于0既是需要被删除的航迹，根据被删除航迹个数调整临时点所对应的航迹号
        if tmpTracksList.at[tracksPointer,'hung'] >= 0 :
            if pointsPointer < totalTmpStoragePoints-1 and tmpStoragePoints.iat[pointsPointer, 0] == tmpStoragePoints.iat[pointsPointer + 1, 0]:
                tmpStoragePoints.iat[pointsPointer, 0] -= shiftValue
                pointsPointer += 1

            tmpStoragePoints.iat[pointsPointer, 0] -= shiftValue
            pointsPointer += 1
            continue
        else:
            shiftValue += 1

    tmpStoragePoints = tmpStoragePoints.head(pointsPointer)   #选取调整了航迹号的这些临时点
    totalTmpStoragePoints = tmpStoragePoints.shape[0]           #更新临时点个数

    delete_points = tmpTracksList[tmpTracksList['hung'] < 0]    #选择临时航迹中所有饥饿值小于0的点作为删除的点
    tmpTracksList = tmpTracksList[tmpTracksList['hung'] >= 0]   #剩下饥饿值大于等于0的点继续保留作为临时航迹点
    tmpTracksList.index = range(tmpTracksList.shape[0])         #更新临时航迹列表index（航迹号）
    totalTmpTracks = tmpTracksList.shape[0]

    return [tmpTracksList,totalTmpTracks, tmpStoragePoints, totalTmpStoragePoints,delete_points]

'''确定航迹点绘制函数'''
#绘制确定航迹
# 输入：frameInfor当前帧目标点信息,tmpTracksList临时航迹列表, tmpStoragePoints临时点信息列表,
# 输入：totalTmpStoragePoints临时点个数,delete_points匹配失败被删除的点,mlMissPoints被机器学习模型错误删除的真实点迹信息
# 输出：更新后的[tmpStoragePoints, totalTmpStoragePoints]
def TrackDraw(frameInfor,tmpTracksList, tmpStoragePoints, totalTmpStoragePoints,delete_points,mlMissPoints):
    scsfulOriginPoint = tmpTracksList[tmpTracksList['hung'] >= 3]#选择出饥饿值大于等于3的所有点作为成功起始点

    if scsfulOriginPoint.shape[0] != 0:   #当有新的确定航迹时，则画出其点迹
        for i in scsfulOriginPoint.index:     #遍历已成功起始的所有航迹
            tmpPointShouldDraw = tmpStoragePoints[tmpStoragePoints['tmpTracksNo']==i]     #从临时点迹列表中找出和确定航迹号匹配的点作为被绘制的点
            tmpStoragePoints = tmpStoragePoints.drop(tmpPointShouldDraw.index)            #删除临时点迹列表这些需要被画出的点
            tmpStoragePoints.index = range(tmpStoragePoints.shape[0])                     #重排临时点迹列表
            totalTmpStoragePoints = tmpStoragePoints.shape[0]                             #更新临时点数量
            if tmpPointShouldDraw.shape[0] > 1:                                           #当该航迹之前的起始点不止一个时，则需要画两条线
                tmpPointShouldDraw.index = range(tmpPointShouldDraw.shape[0])
                linex = [tmpPointShouldDraw.at[0, 'X_position'], tmpPointShouldDraw.at[1,'X_position']]
                liney = [tmpPointShouldDraw.at[0, 'Y_position'], tmpPointShouldDraw.at[1,'Y_position']]
                plt.plot(linex, liney, c='black')#前两帧点迹连线
                linex = [scsfulOriginPoint.at[i, 'X_position'], tmpPointShouldDraw.at[1, 'X_position']]
                liney = [scsfulOriginPoint.at[i, 'Y_position'], tmpPointShouldDraw.at[1, 'Y_position']]
                plt.plot(linex, liney, c='black')#上一帧与最新点的连线
            else:#当临时点保存列表仅一个点与当前确定航迹匹配时，则只需要画最新点与上一帧数据的连线
                tmpPointShouldDraw.index = range(tmpPointShouldDraw.shape[0])
                linex = [scsfulOriginPoint.at[i, 'X_position'], tmpPointShouldDraw.at[0, 'X_position']]
                liney = [scsfulOriginPoint.at[i, 'Y_position'], tmpPointShouldDraw.at[0, 'Y_position']]
                plt.plot(linex, liney, c='black')
                
            wrongPlotPoints = tmpPointShouldDraw[tmpPointShouldDraw['Target'] == 0]     # 选择需要绘制的临时点中的错误关联点
            correctPlotPoints = tmpPointShouldDraw[tmpPointShouldDraw['Target'] == 1]   # 选择需要绘制的临时点中的正确关联点
            plt.scatter(correctPlotPoints.loc[:, 'X_position'], correctPlotPoints.loc[:, 'Y_position'], s=25, c='r')#绘制正确点
            plt.scatter(wrongPlotPoints.loc[:, 'X_position'],     wrongPlotPoints.loc[:, 'Y_position'], s=25, c='gray', marker='x')#绘制错误点

    wrongPlotPoints = scsfulOriginPoint[scsfulOriginPoint['Target']  == 0]  #选择成功起始点中的错误关联点
    correctPlotPoints = scsfulOriginPoint[scsfulOriginPoint['Target']  == 1]#选择成功起始点中的正确关联点

    missPlotPoints1 = delete_points[delete_points['Target'] == 1]#选择航迹起始失败的点中的正确点
    missPlotPoints2 = frameInfor[frameInfor['Target'] == 1]      #选择其中漏警的数据点
    missPlotPoints = [missPlotPoints1,missPlotPoints2]


    missPlotPoints = pd.concat(missPlotPoints,ignore_index = True,sort = True)

    #绘制各类点
    plt.scatter(mlMissPoints.loc[:, 'X_position'], mlMissPoints.loc[:, 'Y_position'], s=25, c='blue',marker = '>')
    plt.scatter(correctPlotPoints.loc[:,'X_position'], correctPlotPoints.loc[:,'Y_position'], s=25, c='r')
    plt.scatter(wrongPlotPoints.loc[:,'X_position'], wrongPlotPoints.loc[:,'Y_position'], s=25, c='gray', marker='x')
    plt.scatter(missPlotPoints.loc[:,'X_position'], missPlotPoints.loc[:,'Y_position'], s=15, c='green', marker='<')

    return [tmpStoragePoints, totalTmpStoragePoints]

'''结合机器学习的雷达航迹关联应用函数'''
#结合机器学习的雷达航迹关联应用函数
# 输入：realData真实数据选择参数，为false时采用仿真, machineLearnEnable 是否打开机器学习分类模型,mlModelType 机器学习模型类型选择
# 输入： totalSimuFile 仿真文件数, totalFramePerSimu 仿真文件数据帧数
# 输出： 无
def RadarDataRelateBasedonMachineLearning(realData = False, machineLearnEnable = False,mlModelType = 'KNN', totalSimuFile = 30, totalFramePerSimu = 10):
    mlModel = None
    if machineLearnEnable == True:#训练机器学习模型
        mlModel = RadarMl.RadarML(mlModelType)
        mlModel.DatasetProc(simu=True,scale_en= True, poly_en=False)
        mlModel.Train()
    if realData == True:#如果利用真实航迹作为数据源，则需要将真实数据进行分帧处理
        Frame.FrameCreat(save_en=True, plot_en=True, fakerate=50, sample_rate=5)

    for simuFileNo in range(totalSimuFile):    #对每一个仿真文件进行航迹关联处理
        processOutput = sys.stdout  # 标准图像输出
        plt.figure(figsize=(5, 40), dpi=100)  # 设置输出图像画布大小
        plt.vlines(x=[-5.5, -1.8, 1.8, 5.5], ymin=0, ymax=40, colors='yellow')  # 画出车道线

        tmpTracksList, totalTmpTracks = tmpTracksListInit()               #初始化临时航迹列表
        tmpStoragePoints,totalTmpStoragePoints = tmpStoragePointsInit()   #初始化临时点迹列表

        for frameNo in range(totalFramePerSimu):   #从文件中读取每帧量测
            if realData == True:
                frameInfor = Frame.FrameRead(frameNo)
            else:
                frameInfor = Frame.SimuFrameRead(simuFileNo,frameNo)

            count = frameNo / (totalFramePerSimu - 1) * 100   #计算显示每个仿真文件的处理进程
            processOutput.write(f'\r PROCESSING percent:{count:.0f}%')

            if machineLearnEnable == True:#机器学习模型应用于雷达量测分类
                frameInfor, mlMissPoints = mlModel.Applicate(frameInfor,scale_en=True)
            else:
                mlMissPoints  = pd.DataFrame([],columns=['Angle','Speed','X_position','Y_position','Target'])
            #对雷达量测进行航迹关联
            [frameInfor, tmpTracksList, tmpStoragePoints, totalTmpStoragePoints] = TrackRelate(frameInfor, tmpTracksList, totalTmpTracks, tmpStoragePoints, totalTmpStoragePoints,mlModel,machineLearnEnable = machineLearnEnable)
            #删除关联失败的航迹信息
            [tmpTracksList, totalTmpTracks, tmpStoragePoints, totalTmpStoragePoints, delete_points] = TrackDelet(tmpTracksList, totalTmpTracks, tmpStoragePoints, totalTmpStoragePoints)
            #没有正确关联的点作为新航迹
            [tmpTracksList, totalTmpTracks] = TrackNewDevelop(frameInfor, tmpTracksList, totalTmpTracks)
            #绘制关联成功的航迹
            [tmpStoragePoints, totalTmpStoragePoints] = TrackDraw(frameInfor, tmpTracksList, tmpStoragePoints, totalTmpStoragePoints, delete_points,mlMissPoints=mlMissPoints)

        processOutput.flush
        plt.xlim((-7, 7))#坐标属性设置
        plt.ylim((0, 40))
        plt.xlabel("X(m)")
        plt.ylabel("Y(m)")
        plt.show()
        plt.pause(0)#暂停显示关联结果
    return

def main():
    RadarDataRelateBasedonMachineLearning(realData = False,machineLearnEnable = False,mlModelType = 'SVM', totalSimuFile = 6,totalFramePerSimu=4)

if __name__ == '__main__':
    main()
