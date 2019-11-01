import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

import sklearn 
from sklearn.model_selection import train_test_split
import random
import matplotlib.pyplot as plt

#采集航迹点
plot_en = 0  #设置是否需要画出航迹
track_total = 20  #设置需要采集的航迹数量

AllTracks = pd.DataFrame([])
for i in range(0,track_total):
    path = 'G:/Graduate/CodeForGuaduate/pysource/tracks/Tracks_'+ str(i) +'.txt'
    names = ['Track_No','Point_No','Speed','X_position','Y_position','Alarm','Angle','Mat','Frame','Target']
    try:
        tracks = pd.read_csv(path,sep = ' ',names = names)
    except:
        continue
    tracks = tracks[~tracks['Track_No'].isin([0])]#删除当前航迹中所有track_No中为0的点
    if plot_en == 1:#画出每一条轨迹
        x = tracks['X_position']
        y = tracks['Y_position']
        plt.scatter(x,y,s = 2)
        plt.xlim((-15,15))
        plt.ylim((0,30))
        plt.show()
        print("航迹号：",i,"   点迹数",)
    
    #AllTracks
    frames = [AllTracks,tracks]#合并点迹信息
    AllTracks = pd.concat(frames,ignore_index = True)
    
    #数据集
#产生正样本集
labels = ['Track_No','Point_No','Alarm','Mat','Frame']
Pointset = AllTracks.drop(labels = labels,axis = 1,inplace = False)
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


#缩放数据
from sklearn.preprocessing import RobustScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import StandardScaler

scaler = MinMaxScaler()
X_train_scale = scaler.fit_transform(X_train)
X_test_scale = scaler.fit_transform(X_test)

#提取多项式特征和交互特征
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree = 3).fit(X_train_scale)
X_train_poly = poly.transform(X_train_scale)
X_test_poly = poly.transform(X_test_scale)
print("polyXtrain.shape:{}".format(X_train_poly.shape))
print("polyXtrain names:{}".format(poly.get_feature_names()))

#绘制特征散点图
names = ['Speed','X_position','Y_position','Angle']
X_train.columns = names
grr = pd.plotting.scatter_matrix(X_train,c=Y_train, marker = 'o',figsize = (16,16),hist_kwds = {'bins':20},s=30,alpha = .8)
#plt.show()

#KNN算法-rand（0）-0.968
from sklearn.neighbors import KNeighborsClassifier
'''#观察参数设置对KNN算法精度影响
training_accuracy = []
test_accuracy = []
neighbor_setting = range(1,10)
for n_neighbors in neighbor_setting:

    knn = KNeighborsClassifier(n_neighbors = n_neighbors)
    knn.fit(X_train_scale,Y_train)
    training_accuracy.append(knn.score(X_train_scale,Y_train))
    test_accuracy.append(knn.score(X_test_scale,Y_test))
    #Y_pred = knn.predict(X_test)
    #Y_test
plt.plot(neighbor_setting,training_accuracy,label = 'training_accuracy')
plt.plot(neighbor_setting,test_accuracy,label = 'test_accuracy')
plt.ylabel('Accuracy')
plt.xlabel('n_neighbors')
plt.show()
'''
knn = KNeighborsClassifier(n_neighbors = 2)
knn.fit(X_train_scale,Y_train)
Y_pred = knn.predict(X_test_scale)
print("测试集准确度为：{}".format(knn.score(X_test_scale,Y_test)))


#将测试集dataframe的名字改回
names = ['Speed','X_position','Y_position','Angle']
X_test.columns = names


#打印出分类错误的点
t_fake = 0
t_ignor = 0
for i in range(0,len(Y_pred)):
    if Y_pred[i]==1 and Y_test.iloc[i] == 0: #虚警点
        t_fake = t_fake + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'b')
    if Y_pred[i]==0 and Y_test.iloc[i] == 1:  #漏警点
        t_ignor = t_ignor + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'r')


plt.xlim((-10,10))
plt.ylim((0,30))
plt.show()
print("漏警点数：{}".format(t_ignor))
print("虚警点数：{}".format(t_fake))

#线性回归
from sklearn.linear_model import LinearRegression
lr = LinearRegression().fit(X_train,Y_train)
print("Training set score{}".format(lr.score(X_train,Y_train)))

from sklearn.tree import DecisionTreeClassifier
'''
training_accuracy = []
test_accuracy = []
maxdep_setting = range(1,31)
for maxdep in maxdep_setting:
    tree = DecisionTreeClassifier(random_state = 0,max_depth = maxdep)
    tree.fit(X_train,Y_train)
    training_accuracy.append(tree.score(X_train,Y_train))
    test_accuracy.append(tree.score(X_test,Y_test))
plt.plot(maxdep_setting,training_accuracy,label = 'training_accuracy')
plt.plot(maxdep_setting,test_accuracy,label = 'test_accuracy')
plt.ylabel('Accuracy')
plt.xlabel('max_depth')
plt.show()
'''
tree = DecisionTreeClassifier(random_state = 0,max_depth = 10)
tree.fit(X_train_scale,Y_train)
Y_pred = tree.predict(X_test_scale)
print("Train accuracy:{}".format(tree.score(X_train_scale,Y_train)))
print("Test accuracy:{}".format(tree.score(X_test_scale,Y_test)))


#打印出分类错误的点
t_fake = 0
t_ignor = 0
for i in range(0,len(Y_pred)):
    if Y_pred[i]==1 and Y_test.iloc[i] == 0: #虚警点
        t_fake = t_fake + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'b')
    if Y_pred[i]==0 and Y_test.iloc[i] == 1:  #漏警点
        t_ignor = t_ignor + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'r')


plt.xlim((-10,10))
plt.ylim((0,30))
plt.show()
print("漏警点数：{}".format(t_ignor))
print("虚警点数：{}".format(t_fake))

#观察决策树分类图
from sklearn.tree import export_graphviz
names = ['Speed','X_position','Y_position','Angle']
export_graphviz(tree,out_file = 'tree.dot',class_names = ['Target','Fake'],feature_names = names,filled = True)
import graphviz
with open("tree.dot") as f: 
    dot_graph = f.read()
graphviz.Source(dot_graph)

print("Feature importance:\n{}".format(tree.feature_importances_))

from sklearn.svm import SVC
svm = SVC()
svm.fit(X_train_scale,Y_train)
print("Train accuracy:{}".format(svm.score(X_train_scale,Y_train)))
print("Test accuracy:{}".format(svm.score(X_test_scale,Y_test)))
Y_pred = svm.predict(X_test_scale)

#打印出分类错误的点
t_fake = 0
t_ignor = 0
for i in range(0,len(Y_pred)):
    if Y_pred[i]==1 and Y_test.iloc[i] == 0: #虚警点
        t_fake = t_fake + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'b')
    if Y_pred[i]==0 and Y_test.iloc[i] == 1:  #漏警点
        t_ignor = t_ignor + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'r')


plt.xlim((-10,10))
plt.ylim((0,30))
plt.show()
print("漏警点数：{}".format(t_ignor))
print("虚警点数：{}".format(t_fake))

plt.plot(X_train.min(axis = 0),'o',label = 'min')
plt.plot(X_train.max(axis = 0),'^',label = 'max')
plt.legend(loc = 4)
plt.xlabel("Feature index")
plt.ylabel("Feature Magnitude")
plt.yscale("log")
plt.show()


from sklearn.neural_network import MLPClassifier
#使用两个隐含层 每个隐含层包含10个隐单元
mlp = MLPClassifier(solver = 'lbfgs',random_state = 0,hidden_layer_sizes = [3,100]).fit(X_train_scale,Y_train)
print("Train accuracy:{}".format(mlp.score(X_train_scale,Y_train)))
print("Test accuracy:{}".format(mlp.score(X_test_scale,Y_test)))

Y_pred = mlp.predict(X_test_scale)

#打印出分类错误的点
t_fake = 0
t_ignor = 0
for i in range(0,len(Y_pred)):
    if Y_pred[i]==1 and Y_test.iloc[i] == 0: #虚警点
        t_fake = t_fake + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'b')
    if Y_pred[i]==0 and Y_test.iloc[i] == 1:  #漏警点
        t_ignor = t_ignor + 1
        WrongPoint = list(X_test.iloc[i,:])#错误点信息
        x = WrongPoint[1]
        y = WrongPoint[2]
        plt.scatter(x,y,s = 5,c = 'r')


plt.xlim((-10,10))
plt.ylim((0,30))
plt.show()
print("漏警点数：{}".format(t_ignor))
print("虚警点数：{}".format(t_fake))
print("Training set score{}".format(lr.score(X_test,Y_test)))

#神经网络训练的网络隐层权重，浅色代表较大的正值，深色代表负值
plt.figure(figsize = (20,5))
plt.imshow(mlp.coefs_[0],interpolation = 'none')
names = ['Speed','X_position','Y_position','Angle']
plt.yticks(range(5),names)
plt.colorbar()
plt.show()
