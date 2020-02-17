#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2020.2.17
#功能：机器学习模型训练和雷达数据帧分类函数
#auther： woody sun
'''
import pandas as pd
import numpy as np
import random
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import Normalizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import matplotlib.pyplot as plt

class RadarML():
    def __init__(self,classifier = 'KNN'):
        self.classifierName = classifier

    def DatasetProc(self,frameNum = 10,simu=True, simufilenum = 30,scale_en = True,poly_en = True):
        '''数据集预处理阶段'''
        if simu == False:#利用真实航迹作为训练数据集
            allTracks = pd.DataFrame([])
            for i in range(0, frameNum):
                path = 'G:/Graduate/CodeForGuaduate/pysource/tracks/Tracks_' + str(i) + '.txt'
                names = ['Track_No', 'Point_No', 'Speed', 'X_position', 'Y_position', 'Alarm', 'Angle', 'Mat', 'Frame','Target']
                try:
                    tracks = pd.read_csv(path, sep=' ', names=names)
                except:
                    continue
                tracks = tracks[~tracks['Track_No'].isin([0])]  # 删除当前航迹中所有track_No中为0的点

                # allTracks
                frames = [allTracks, tracks]  # 合并点迹信息
                allTracks = pd.concat(frames, ignore_index=True)

            # 数据集
            # 产生正样本集
            labels = ['Track_No', 'Point_No', 'Alarm', 'Mat', 'Frame']
            pointSet = allTracks.drop(labels=labels, axis=1, inplace=False)  # 去掉部分原始数据标签
            pointSet.columns = ['data', 'data', 'data', 'data', 'Target']
            pointSet['Target'] = 1

            # 产生噪声点
            names = ['Speed', 'X_position', 'Y_position', 'Angle', 'Target']
            fakePoints = pd.DataFrame(data=None, columns=names)
            randomSpeed = [random.randint(-8, 15) for i in range(3000)]
            randomYpos = [round(40.0 * random.random(), 3) for i in range(3000)]
            randomAngle = [round(random.uniform(-30, 70), 1) for i in range(3000)]
            randomXpos = randomYpos * np.tan(np.deg2rad(randomAngle))

            fakePoints['Speed'] = randomSpeed
            fakePoints['X_position'] = randomXpos
            fakePoints['Y_position'] = randomYpos
            fakePoints['Angle'] = randomAngle
            fakePoints['Target'] = 0

            names = ['data', 'data', 'data', 'data', 'Target']
            fakePoints.columns = names
            # 合并数据点
            frames = [pointSet, fakePoints]  # 合并点迹信息
            DATASET = pd.concat(frames, ignore_index=True)
        else:#读取仿真航迹作为数据集
            DATASET = pd.DataFrame([])
            path = 'G:/Graduate/CodeForGuaduate/pysource/DATASET.txt'
            DATASET = pd.read_csv(path, sep=' ')
            DATASET.columns = ['data', 'data', 'data', 'data', 'Target']

        # 分离数据集
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(DATASET['data'], DATASET['Target'], random_state=0)
        if scale_en == True:  # 缩放数据
            self.scaler = MinMaxScaler()
            self.scaler.fit(self.X_train)
            self.X_train = self.scaler.transform(self.X_train)
            self.X_test = self.scaler.fit_transform(self.X_test)

        if poly_en == True:  # 提取多项式特征和交互特征
            poly = PolynomialFeatures(degree=3).fit(self.X_train)
            self.X_train = poly.transform(self.X_train)
            self.X_test = poly.transform(self.X_test)

    def Train(self,KnnNeighbors = 58,DTreeMaxDepth = 5,RForestNEstimators = 13,SVC_C = 10,SVCGamma = 2):
        '''模型训练'''
        if self.classifierName == 'KNN':
            self.classifier = KNeighborsClassifier(n_neighbors=KnnNeighbors)
        elif self.classifierName == 'DTree':
            self.classifier = DecisionTreeClassifier(max_depth=DTreeMaxDepth,random_state = 0)
        elif self.classifierName == 'RForest':
            self.classifier = RandomForestClassifier(n_estimators= RForestNEstimators,random_state=0)
        elif self.classifierName == 'SVM':
            self.classifier = SVC(kernel = 'rbf',C=SVC_C,gamma=SVCGamma)
        else:
            raise Exception("错误的分类器类别！")

        self.classifier.fit(self.X_train, self.Y_train)
        self.trainScore = self.classifier.score(self.X_train, self.Y_train)
        self.testScore = self.classifier.score(self.X_test, self.Y_test)
        return self.testScore


    def Applicate(self,frame, scale_en = True,poly_en = False):
        '''将训练好的模型应用于分类帧数据中的虚假点'''
        missPoints = pd.DataFrame([],columns=['Angle','Speed','X_position','Y_position','Target'])
        for i in range(frame.shape[0]):
            featureData = frame.loc[[i],'Angle':'Y_position']
            if scale_en == True:  # 缩放数据
                featureData = self.scaler.transform(featureData)

            if poly_en == True:  # 提取多项式特征和交互特征
                poly = PolynomialFeatures(degree=3).fit(featureData)
                featureData = poly.transform(featureData)

            tagData = frame.at[i,'Target']
            tagPred = self.classifier.predict(featureData)      # 机器学习分类
            if (tagPred == 0):#如果被分类为虚假点
                if tagData == 1:#如果将真实点分类为虚假点，则将这个错误分类点加入missPoint中
                    missPoints = missPoints.append(frame.loc[[i]])
                frame = frame.drop(i)

        return frame,missPoints

    def ShowModelInfr(self):
        '''打印模型相关信息'''
        print("Classifier :{}".format(self.classifierName))
        print("X_train shape : {}".format(self.X_train.shape))
        print("Y_train shape : {}".format(self.Y_train.shape))
        print("X_test shape : {}".format(self.X_test.shape))
        print("Y_test shape : {}".format(self.Y_test.shape))
        print("Train data accuracy : {}".format(self.trainScore))
        print("Test data accuracy : {}".format(self.testScore))

def main():
    simuPath = './radar_infor_sim/simufile'+ str(0)+'/frame_' + str(3) + '.txt'
    names = ['Angle','Speed', 'X_position','Y_position', 'Target']
    frameInfor = pd.read_csv(simuPath, sep=' ', names=names)
    ml = RadarML('SVM')
    scaler = ml.DatasetProc(simu=True, scale_en= True, poly_en=False)

    # testScore = []
    # for x in np.arange(0.1, 20, 1):
    #     testScore.append(ml.Train(KnnNeighbors = x, DTreeMaxDepth = x,RForestNEstimators = x,SVC_C= x))
    # xRange = np.arange(0.1,20, 1)
    # plt.plot(xRange, testScore)
    # plt.show()
    # plt.pause(0)

    ml.Train(KnnNeighbors=58)
    ml.ShowModelInfr()
    print(frameInfor)
    print("original frame size:{}".format(frameInfor.shape[0]))
    frameInfor,missPoints = ml.Applicate(frameInfor, scale_en = True, poly_en=False)
    print(frameInfor)
    print("after frame size:{}".format(frameInfor.shape[0]))

if __name__ == '__main__':
    main()
