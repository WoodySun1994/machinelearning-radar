#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2020.2.16
#功能：机器学习模型训练所需数据集获取与合并
#auther： woody sun
'''
import pandas as pd

totalSimufile = 100     #需要的仿真文件个数
totalFramesPerSimu = 4  #每个仿真文件提取的帧数

DATASET = pd.DataFrame([])
for i in range(totalSimufile):
    for j in range(totalFramesPerSimu):
        path = 'G:/Graduate/CodeForGuaduate/pysource/radar_infor_sim/simufile'+ str(i) +'/frame_' + str(j) + '.txt'
        names = ['Angle','Speed', 'X_position', 'Y_position',  'Target']
        try:
            points = pd.read_csv(path, sep=' ', names=names)
        except:
            continue
        tmp = [DATASET, points]  # 合并点迹信息
        DATASET = pd.concat(tmp, ignore_index=True)
print(DATASET)
DATASET.to_csv('DATASET.txt',sep = ' ',index=False)         #保存数据集
