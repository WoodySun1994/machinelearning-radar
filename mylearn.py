import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import sklearn
from sklearn.model_selection import train_test_split
import random
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.neighbors import KNeighborsClassifier

#数据集处理函数
def DataSetProc(track_total = 35,scale_en = True,poly_en = True):
    # 采集航迹点
    track_total = 35  # 设置需要采集的航迹数量

    AllTracks = pd.DataFrame([])
    for i in range(0, track_total):
        path = 'G:/Graduate/CodeForGuaduate/pysource/tracks/Tracks_' + str(i) + '.txt'
        names = ['Track_No', 'Point_No', 'Speed', 'X_position', 'Y_position', 'Alarm', 'Angle', 'Mat', 'Frame', 'Target']
        try:
            tracks = pd.read_csv(path, sep=' ', names=names)
        except:
            continue
        tracks = tracks[~tracks['Track_No'].isin([0])]  # 删除当前航迹中所有track_No中为0的点

        # AllTracks
        frames = [AllTracks, tracks]  # 合并点迹信息
        AllTracks = pd.concat(frames, ignore_index=True)

    #数据集
    #产生正样本集
    labels = ['Track_No','Point_No','Alarm','Mat','Frame']
    Pointset = AllTracks.drop(labels = labels,axis = 1,inplace = False)#去掉原始数据标签
    Pointset.columns = ['data','data','data','data','Target']
    Pointset['Target'] = 1
    #Pointset       #正样本集

    #产生噪声点
    names = ['Speed','X_position','Y_position','Angle','Target']
    FakePoints = pd.DataFrame(data = None,columns = names)
    randomspeed = [random.randint(-8,15)for i in range(3000)]
    randomxpos = [round(10.0 * random.uniform(-1,1),3)for i in range(3000)]
    randomypos = [round(40.0 * random.random(),3)for i in range(3000)]
    randomangle = [round(random.uniform(-30,70),1) for i in range(3000)]

    FakePoints['Speed'] = randomspeed
    FakePoints['X_position'] = randomxpos
    FakePoints['Y_position'] = randomypos
    FakePoints['Angle'] =randomangle
    FakePoints['Target'] = 0

    names = ['data','data','data','data','Target']
    FakePoints.columns = names
    #FakePoints    #负样本集
    #合并数据点
    frames = [Pointset,FakePoints]#合并点迹信息
    DATASET = pd.concat(frames,ignore_index = True)
    #DATASET    #数据集
    #分离数据集
    X_train,X_test,Y_train,Y_test = train_test_split(DATASET['data'],DATASET['Target'],random_state = 0)
    print("X_train shape : {}".format(X_train.shape))
    print("Y_train shape : {}".format(Y_train.shape))
    print("X_test shape : {}".format(X_test.shape))
    print("Y_test shape : {}".format(Y_test.shape))

    if scale_en == True:#缩放数据
        scaler = MinMaxScaler()
        X_train_scale = scaler.fit_transform(X_train)
        X_test_scale = scaler.fit_transform(X_test)

    if poly_en == True:#提取多项式特征和交互特征
        poly = PolynomialFeatures(degree = 3).fit(X_train_scale)
        X_train_poly = poly.transform(X_train_scale)
        X_test_poly = poly.transform(X_test_scale)
        print("polyXtrain.shape:{}".format(X_train.shape))
        print("polyXtrain names:{}".format(poly.get_feature_names()))
        return [X_train_poly,X_test_poly,Y_train,Y_test]
    return [X_train,X_test,Y_train,Y_test]

#利用机器学习分类算法去除不是目标的虚假点
def MyClassify(framedata):
    #预处理数据集，训练分类器
    X_train, X_test, Y_train, Y_test = DataSetProc(poly_en=False)
    knn = KNeighborsClassifier(n_neighbors=2)
    knn.fit(X_train, Y_train)
    #将特征['Speed','Angle','Target','X_position','Y_position',]重新排序为-> ['Speed','X_position','Y_position','Angle','Target']
    framedata = framedata.join(framedata.pop('Angle'))
    framedata = framedata.join(framedata.pop('Target'))
    # 遍历每帧数据中的每个点，进行分类
    for i in range(framedata.shape[0]):
        Xdata = framedata.loc[[i],'Speed':'Angle']
        Ypred = knn.predict(Xdata)#分类工具
        if(Ypred == 0):
            framedata = framedata.drop(i)
    return framedata





