#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.5
#功能：雷达获取的mat数据对航迹进行提取保存
#auther： woody sun
'''


import numpy as np
from scipy.io import loadmat
import os
import glob

'''临时航迹关联函数'''
# 将当前点与已经存在的临时航迹列表进行比较，返回匹配后的航迹号。若无匹配航迹则返回-1
#输入：cur_tar当前点   track_infor临时航迹列表
#输出：匹配的航迹号，若无匹配则返回-1
def TarckRelate(cur_tar,track_infor):
    TarckRelaFlag = 0
    for i in range(0,7):                                #与8条临时航迹列表相继匹配
        #print(abs(cur_tar[2] - track_infor[i, 2]))
        #print(cur_tar[4] - track_infor[i, 4])
        if (10 >= abs(cur_tar[2] - track_infor[i, 2])):  #判断速度差距是否在3以内
            if (10 >= cur_tar[4] - track_infor[i, 4]): #同时判断纵向距离差距是否在0.5以内
                if (2 >= cur_tar[3] - track_infor[i, 3]):  # 同时判断横向距离差距是否在3以内
                    TarckRelaFlag = i                       #满足以上两个条件则认为航迹相互关联
                    return TarckRelaFlag
    return -1

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
    if (track_infor[track_no,7] != 0):  #如果当前删除航迹是确定航迹
        endnum  = endnum + 1              #确定删除航迹计数加1
    for i in range(track_no,track_total):      #当前航迹往后的所有航迹前移
        track_infor[i,1:10] = track_infor[i+1,1:10]
    track_infor[track_total,1:10] = np.zeros((1,9))
    return  [track_infor,endnum]

'''确定航迹绘制函数'''
#绘制确定航迹
def TrackPlot():
    pass
    return

'''删除所有Tracks文件'''
# folders location

def DelTracksFiles():
    #   read all the files under the folder
    path = 'G:\\Graduate\\CodeForGuaduate\\pysource\\tracks'
    fileNames = glob.glob(path + r'\*')

    for fileName in fileNames:
        try:
            #           delete file
            os.remove(fileName)
        except:
            try:
                #               delete empty folders
                os.rmdir(fileName)
            except:
                #               Not empty, delete files under folders
                delfile(fileName)
                #               now, folders are empty, delete it
                os.rmdir(fileName)

'''main函数'''
def main():
    DelTracksFiles()  #删除所有Tracks文件
    cur_tar = []         #当前处理点迹信息
    tmp_track_total = 0  # 当前临时航迹数量，临时航迹最多维持8条
    # 临时航迹信息:1临时航迹号 2饥饿时间  3目标速度 4目标横坐标 5目标纵坐标 6是否位于危险区域 7目标角度 8确定航迹编号 9、10mat文件中的编号
    tmp_track_list = np.zeros((8, 10))

    TrackRelaFlag = 0  # 航迹关联成功标志，成功时等于关联的临时航迹号,不成功则为-1

    TRACK_NO = 0  # 确定航迹号
    POINT_NO = 0  # 确定航迹中记录的点迹号
    endnum = 0  # 记录删除的已关联成功航迹数
    savetracknum = 27  # 需要保存的确定航迹数量

    # 保存的所有关联成功的点迹信息： 1确定航迹号 2点迹号 3目标速度 4目标横坐标 5目标纵坐标 6是否位于危险区域 7目标角度
    save_point_list = np.zeros((10000,10))
    save_track_tmp = np.zeros((30,1000,10))   #临时保存矩阵
    SaveData = np.zeros((1000,10))   #保存数据矩阵

    for iii in range(1,153):   #读取mat文件
        path = './matfile/11_1/features_' + str(iii) + '.mat'
        tar_infor = loadmat(path)
        for jjj in range(0,50): #读入MAT中的50个数据点
            cur_tar = tar_infor['featuer_save'][jjj]         #当前处理目标点信息
            #print(cur_tar)

            TrackRelaFlag = TarckRelate(cur_tar, tmp_track_list) #当前点迹与之前所有航迹进行匹配。匹配成功返回临时航迹号，失败则返回0
            if  -1 == TrackRelaFlag:   #没有匹配成功的航迹
                if tmp_track_total < 8:   #最多维持8条临时航迹
                    tmp_track_list = TrackDevelop(cur_tar, tmp_track_list, tmp_track_total)  #新建一条临时航迹，更新临时航迹表
                    tmp_track_total = tmp_track_total + 1  # 正在维持的航迹数 + 1

            else:    #匹配成功
                tmp_track_list = TrackFeed(cur_tar, tmp_track_list, tmp_track_total, TrackRelaFlag)  #更新临时航迹最新点的特征值，并更新各个航迹的饥饿值
                if  tmp_track_list[TrackRelaFlag, 1] >= 9: #判断当前匹配的航迹是否满足稳定航迹条件
                    if (tmp_track_list[TrackRelaFlag, 7] == 0): #确定航迹编号为0 意味着是第一次建立确定航迹
                        TRACK_NO = TRACK_NO + 1  # 确定航迹号加1
                        tmp_track_list[TrackRelaFlag, 7] = TRACK_NO  # 给确定航迹赋值确定航迹号

                    t = tmp_track_list[TrackRelaFlag, 2:10] #临时航迹对应特征信息
                    save_point_list = TrackSave(save_point_list, t, POINT_NO)  #更新确定航迹点迹列表。保存当前航迹点的信息：特征和航迹号
                    POINT_NO = POINT_NO + 1  # 确定点迹号加1
                    #TRACK_NO = TRACK_NO + 1  # 确定航迹号加1

            #遍历临时航迹，删除饥饿值过低的临时航迹
            tmp = tmp_track_total
            for i in range(0,tmp):   #遍历当前所有临时航迹
                if (tmp_track_list[i, 1] < 1 and tmp_track_list[i, 8]): #当临时航迹的饥饿值小于1时，则删除对应的临时航迹
                    [tmp_track_list,endnum] = TrackDelet(tmp_track_list, i, tmp,endnum)#删除临时航迹，并返回已结束的确定航迹数
                    if tmp_track_total > 1:
                        tmp_track_total = tmp_track_total - 1#当前临时航迹数量减1
            #if endnum != 0:
            #    pass
    #if (endnum >= savetracknum):#结束的稳定航迹数达到设定条数，则调整保存当前航迹信息
     #   endnum = 0
        #保存航迹
    for j in range(0,endnum):#保存savetracknum条航迹
        i = 0
        n = 0
        while (save_point_list[i, 0] != 0):#遍历确定航迹列表中每一个点
            if (j == save_point_list[i, 0] - 1): #保存第j条航迹的点迹信息
                save_track_tmp[j, n,:] = save_point_list[i,:]
                n = n + 1
            i = i + 1#读取下一个目标点的值


        #将航迹点按航迹保存
        for j in range(0,endnum):
            i = 0
            while (save_track_tmp[j, i, 0] != 0 ): #直到保存完当前航迹的最后一个点迹
                SaveData[i,:] = save_track_tmp[j, i,:]
                i = i + 1
            if (i > 100):#如果该航迹的点迹数超过20，则保存航迹信息
                savepath = './tracks/'+'Tracks_'+ str(j) + '.txt'
                np.savetxt(savepath,SaveData,fmt='%.3f')
                SaveData = np.zeros((1000,10))#清空保存数据
    pass


if __name__ == '__main__':
    main()
