#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.11.20
#功能：雷达数据帧进行霍夫变换相关函数
#auther： woody sun
'''

import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import SunLearn
import Frame

#霍夫直线变换
def hough_line(x_idxs, y_idxs, width=30, length=30, angle_step=4,hgplot_en = True,thres_rate = 0.8):
    # Rho and Theta ranges
    thetas = np.deg2rad(np.arange(-90.0, 90.0, angle_step))

    diag_len = int(round(math.sqrt(width * width + length * length)))
    rhos = np.linspace(-diag_len, diag_len, diag_len * 2)

    # Cache some resuable values
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    num_thetas = len(thetas)

    accumulator = np.zeros((2 * diag_len, num_thetas), dtype=np.uint8)
    # Vote in the hough accumulator
    for i in range(len(x_idxs)):
        x = x_idxs[i]
        y = y_idxs[i]

        for t_idx in range(num_thetas):
            # Calculate rho. diag_len is added for a positive index
            rho = diag_len + int(round(x * cos_t[t_idx] + y * sin_t[t_idx]))
            #            rho = int(round(x * cos_t[t_idx] + y * sin_t[t_idx]))
            accumulator[rho, t_idx] += 1
    if hgplot_en == True:
        plt.imshow(accumulator, cmap='jet', extent=[np.rad2deg(thetas[0]), np.rad2deg(thetas[-1]), rhos[0], rhos[-1]])
        plt.title('Hough transform')
        plt.xlabel('Angles (degrees)')
        plt.ylabel('Distance (pixels)')
        plt.axis('image')
        plt.show()
    #选取大于阈值的直线的theta&rho
    maxvalue = np.max(accumulator)
    thres_rate = 0.8
    threshold = int(thres_rate * maxvalue)

    rho = []
    theta = []
    print(accumulator.shape)
    for i in range(accumulator.shape[0]):
        for j in range(accumulator.shape[1]):
            if accumulator[i, j] > threshold:  # 霍夫空间满足一条直线的点数超过阈值时
                rho.append(rhos[i])
                theta.append(thetas[j])

    return theta, rho

# 融合theta差不超过20°的直线
def theta_fuse(theta, rho, fusetheta):
    fuserad = np.deg2rad(fusetheta)
    c = theta[0]
    t = 0
    tmprho = []
    tmptheta = []
    for d in range(1, len(theta)):
        if abs(c - theta[d]) > fuserad:
            if t > 0:
                #计算tmptheta的均值
                sum = 0
                for i in range(t):
                    sum +=  tmptheta[i]
                mean = sum/t
                #寻找tmptheta中最接近均值的值
                Dvalue_min = abs(tmptheta[0] - mean)
                Dvaluemin_pos = 0 #tmptheta中最接近均值的索引
                for i in range(1,t):
                    Dvalue = abs(tmptheta[i] - mean)
                    if Dvalue < Dvalue_min:
                        Dvaluemin_pos = i
                #赋值
                theta[d - t - 1] = tmptheta[Dvaluemin_pos]
                rho[d - t - 1] = tmprho[Dvaluemin_pos]

                tmprho = list([])
                tmptheta = list([])

                t = 0
            c = theta[d]
        else:
            t += 1
            tmptheta.append(theta[d])
            tmprho.append(rho[d])
            theta[d] = 0
            rho[d] = 0
    return [theta, rho]

#画出检测出的直线
def lineplot(theta,rho):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    for t in range(len(theta)):
        if sin_theta[t] > 0:
            xx = [100, (rho[t] - 100 * sin_theta[t]) / cos_theta[t]]
            yy = [(rho[t] - 100 * cos_theta[t]) / sin_theta[t], 100]
        else:
            xx = [-100, (rho[t] - 100 * sin_theta[t]) / cos_theta[t]]
            yy = [(rho[t] + 100 * cos_theta[t]) / sin_theta[t], 100]
        plt.plot(xx, yy)
    plt.xlim((-15, 15))
    plt.ylim((-0, 30))
    plt.show()
    return

#画出点迹
def Pointsplot(x,y):
    plt.scatter(x, y, s=2)
    plt.xlim((-15, 15))
    plt.ylim((0, 30))
    return

def main():
    ##########################################################
    ############     通过读取帧文件获取数据    ###############
    ##########################################################
    hough_frame = pd.DataFrame([])
    #读取数据
    for i in range(5):
        frame_infor = Frame.frameread(i)
        infor = [hough_frame,frame_infor]
        hough_frame = pd.concat(infor,ignore_index = True)


    hough_frame = SunLearn.MyClassify(hough_frame)#利用机器学习算法对点迹进行分类
    x_idxs = hough_frame['X_position']
    y_idxs = hough_frame['Y_position']
    x_idxs.index = range(len(x_idxs))
    y_idxs.index = range(len(y_idxs))

    ##########################################################


    ##########################################################
    ################通过自定义点获取数据######################
    ##########################################################
    # x1 = [0, 1, 2, 3, 4, -10]
    # y1 = [10, 10, 10, 10, 10, 10]
    #
    # x2 = [0, 1, 2, 3, 4, 5, 6]
    # y2 = [7, 8, 9, 10, 11, 12, 13]
    #
    # x3 = [5, 5, 5, 5, 5, 5]
    # y3 = [23, 24, 25, 26, 27, 28]
    #
    # x4 = [-8, -7, -6, -5, -4, -3, -2, -1, 0]
    # y4 = [22, 21, 20, 19, 18, 17, 16, 15, 14]
    #
    # x_idxs = x4 + x3 + x2 + x1
    # y_idxs = y4 + y3 + y2 + y1
    ##########################################################
    [theta, rho] = hough_line(x_idxs, y_idxs, angle_step=1)#霍夫直线检测
    theta, rho = theta_fuse(theta, rho, 30)#角度融合
    Pointsplot(x_idxs, y_idxs)  # 画出需要检测直线的点
    lineplot(theta,rho)  #根据参数画出直线
    return

if __name__ == '__main__':
    main()
