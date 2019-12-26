#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.26
#功能：对雷达数据帧进行分类的相关函数
#auther： woody sun
'''
import pandas as pd
import numpy as np
import random
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC


class radar_ml():
    def __init__(self,classifier = 'KNN'):
        self.clasname = classifier

    def Datasetproc(self,framenum = 10,simu=True, simufilenum = 30,scale_en = True,poly_en = True):
        '''数据集预处理阶段'''
        if simu == False:#利用真实航迹作为训练数据集
            AllTracks = pd.DataFrame([])
            for i in range(0, framenum):
                path = 'G:/Graduate/CodeForGuaduate/pysource/tracks/Tracks_' + str(i) + '.txt'
                names = ['Track_No', 'Point_No', 'Speed', 'X_position', 'Y_position', 'Alarm', 'Angle', 'Mat', 'Frame','Target']
                try:
                    tracks = pd.read_csv(path, sep=' ', names=names)
                except:
                    continue
                tracks = tracks[~tracks['Track_No'].isin([0])]  # 删除当前航迹中所有track_No中为0的点

                # AllTracks
                frames = [AllTracks, tracks]  # 合并点迹信息
                AllTracks = pd.concat(frames, ignore_index=True)

            # 数据集
            # 产生正样本集
            labels = ['Track_No', 'Point_No', 'Alarm', 'Mat', 'Frame']
            Pointset = AllTracks.drop(labels=labels, axis=1, inplace=False)  # 去掉部分原始数据标签
            Pointset.columns = ['data', 'data', 'data', 'data', 'Target']
            Pointset['Target'] = 1

            # 产生噪声点
            names = ['Speed', 'X_position', 'Y_position', 'Angle', 'Target']
            FakePoints = pd.DataFrame(data=None, columns=names)
            randomspeed = [random.randint(-8, 15) for i in range(3000)]
            randomypos = [round(40.0 * random.random(), 3) for i in range(3000)]
            randomangle = [round(random.uniform(-30, 70), 1) for i in range(3000)]
            randomxpos = randomypos * np.tan(np.deg2rad(randomangle))

            FakePoints['Speed'] = randomspeed
            FakePoints['X_position'] = randomxpos
            FakePoints['Y_position'] = randomypos
            FakePoints['Angle'] = randomangle
            FakePoints['Target'] = 0

            names = ['data', 'data', 'data', 'data', 'Target']
            FakePoints.columns = names
            # 合并数据点
            frames = [Pointset, FakePoints]  # 合并点迹信息
            DATASET = pd.concat(frames, ignore_index=True)
        else:#读取仿真航迹作为数据集
            DATASET = pd.DataFrame([])
            path = 'G:/Graduate/CodeForGuaduate/pysource/DATASET.txt'
            DATASET = pd.read_csv(path, sep=' ')
            DATASET.columns = ['data', 'data', 'data', 'data', 'Target']

        # 分离数据集
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(DATASET['data'], DATASET['Target'], random_state=0)
        if scale_en == True:  # 缩放数据
            scaler = MinMaxScaler()
            self.X_train = scaler.fit_transform(self.X_train)
            self.X_test = scaler.fit_transform(self.X_test)

        if poly_en == True:  # 提取多项式特征和交互特征
            poly = PolynomialFeatures(degree=3).fit(self.X_train)
            self.X_train = poly.transform(self.X_train)
            self.X_test = poly.transform(self.X_test)

    def Train(self):
        '''模型训练'''
        if self.clasname == 'KNN':
            self.classifier = KNeighborsClassifier(n_neighbors=2)
        elif self.clasname == 'DTree':
            self.classifier = DecisionTreeClassifier(random_state = 0)
        elif self.clasname == 'RForest':
            self.classifier = RandomForestClassifier(n_estimator = 100,random_state=0)
        elif self.clasname == 'SVM':
            self.classifier = SVC(kernel = 'rbf',C=10,gamma=0.1)
        else:
            raise Exception("错误的分类器类别！")

        self.classifier.fit(self.X_train, self.Y_train)
        self.trainscore = self.classifier.score(self.X_train, self.Y_train)
        self.testscore = self.classifier.score(self.X_test, self.Y_test)

    def Applicate(self,frame):
        '''模型应用于分类帧数据中的虚假点'''
        # 将特征[''Angle',Speed','Target','X_position','Y_position',]重新排序为-> [''Angle',Speed','X_position','Y_position','Target']
        #frame = frame.join(frame.pop('Angle'))
        frame = frame.join(frame.pop('Target'))
        for i in range(frame.shape[0]):
            Xdata = frame.loc[[i],'Angle':'Y_position']
            Ypred = self.classifier.predict(Xdata)  # 分类工具
            if (Ypred == 0):
                frame = frame.drop(i)
        frame.index = range(frame.shape[0])

        return frame

    def showinfr(self):
        '''打印模型相关信息'''
        print("Classifier :{}".format(self.clasname))
        print("X_train shape : {}".format(self.X_train.shape))
        print("Y_train shape : {}".format(self.Y_train.shape))
        print("X_test shape : {}".format(self.X_test.shape))
        print("Y_test shape : {}".format(self.Y_test.shape))
        print("Train data accuracy : {}".format(self.trainscore))
        print("Test data accuracy : {}".format(self.testscore))

def main():
    Simupath = './radar_infor_sim/simufile'+ str(20)+'/frame_' + str(9) + '.txt'
    names = ['Angle','Speed', 'Target', 'X_position','Y_position']
    frame_infor = pd.read_csv(Simupath, sep=' ', names=names)
    ml = radar_ml('KNN')
    ml.Datasetproc(simu=True, scale_en= False, poly_en=False)
    ml.Train()
    ml.showinfr()
    print(frame_infor)
    print("original frame size:{}".format(frame_infor.shape[0]))
    frame_infor = ml.Applicate(frame_infor)
    print(frame_infor)
    print("after frame size:{}".format(frame_infor.shape[0]))

if __name__ == '__main__':
    main()
