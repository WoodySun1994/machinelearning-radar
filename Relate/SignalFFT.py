#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.29
#功能：模拟二维FFT信号
#auther： woody sun
'''
import math
import random
import numpy as np
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as Axes3D

def Hanning(N=128):
    '''hanning窗函数'''
    window = np.array([0.5 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) for n in range(N)])
    return window

def sawtooth(x):
    '''产生周期为2pi，峰峰值为-1~1的锯齿波'''
    yout = []
    for i in x:
        y = (i%(2*math.pi) - math.pi)/(math.pi)
        yout = np.append(yout, y)
    return yout

def RandomSignalGen(dopfftLenght,rangeLenght):
    '''产生随机FFT信号'''
    randSignal = np.zeros((dopfftLenght,rangeLenght), np.float)
    for dopfftValue in range(dopfftLenght):
        for rangeValue in range(rangeLenght):
             rand = 20 * random.random()
             randSignal[dopfftValue][rangeValue] = rand
    return  randSignal


def BaseSignalGen():
    '''产生基底信号'''
    c = 3e8  # 光速
    f0 = 24e9  # 载频
    lamda = c / f0  # 波长
    d = 6e-3  # 天线间距6mm
    Fv = 7  # 产生多普勒频移 36km/h=10m/s 快速调制  只算频移不计时移
    Fv1 = 8  # 产生多普勒频移 36km/h=10m/s 快速调制  只算频移不计时移

    W1 = Hanning(128)
    W2 = Hanning(128)
    Fd = 163840  # 信号频率为1KHZ
    Fw = 7  # 6.5hz信号频率
    t = np.arange(1, 12.8, 0.0001)  # 定义信号的范围 5-40个周期 16-128周期
    y = 2 + sawtooth(2 * math.pi * Fw * t)  # 原始信号信号频率为Fw
    tt = np.arange(1, 12.8, 0.0001)  # 定义信号的范围 5-40个周期 16-128周期
    yy = 2 + sawtooth(2 * math.pi * Fw * tt + math.degrees(math.pi / 6))  # 原始信号信号频率为Fw相位45度

    N = 128 * 128
    Fs = 1280  # 采样频率 833hz  采128个值
    t1 = 1 / Fs
    t2 = t1 * np.arange(N)
    y1 = 2 + sawtooth(2 * math.pi * Fw * t2)
    data_R1 = np.array(y1)

    t3 = 1 / Fs;
    t4 = np.arange(N) * t3;
    y2 = 2 + sawtooth(2 * math.pi * Fw * t4 + math.degrees(math.pi / 6))
    data_R2 = np.array(y2)

    # 把单位矩阵变成128*128维
    s = 0
    A = np.zeros((128, 128))
    for i in range(128):
        for ii in range(128):
            A[i, ii] = data_R1[s] * 4096 / 3.3
            s = s + 1
    s = 0
    B = np.zeros((128, 128))
    for i in range(128):
        for ii in range(128):
            B[i, ii] = data_R1[s] * 4096 / 3.3
            s = s + 1

    # 读出来的数据放到数组里面
    rangefft_R1 = np.zeros((128, 128))
    rangefft_R2 = np.zeros((128, 128))

    for iii in range(128):
        rangefft_R1[iii, :] = fft(W1 * A[iii, :])
        rangefft_R2[iii, :] = fft(W2 * B[iii, :])

    F1 = abs(rangefft_R1)
    F2 = abs(rangefft_R2)

    dopfftR1 = np.zeros((128, 128))
    dopfftR2 = np.zeros((128, 128))
    for k in range(128):
        dopfftR1[:, k] = fft(rangefft_R1[:, k] * W1)  # 是一个复杂的数据
        dopfftR2[:, k] = fft(rangefft_R2[:, k] * W2)  # 是一个复杂的数据
    D1 = abs(dopfftR1[:, 0:64])
    D2 = abs(dopfftR2[:, 0:64])

    w, h = D1.shape
    baseSignal = np.zeros((w, h))
    for i in range(w):
        for j in range(h):
            baseSignal[i][j] = 20 * math.log(D1[i][j], 10)
    return baseSignal

def SignalSave2txt(signal,type = 'base'):
    '''保存二维FFT信号至txt文件'''
    signalType = ["base","random",'target']
    if signal.shape == (128,64):
        if type in signalType:
            filename = './'+type + '.txt'
            np.savetxt(filename,signal,fmt = '%.3e')
        else:
            raise ("TypeError: Wrong signal type to save!")
    else:
        raise ("DataEroor: Wrong siganl format to save!")



def FFTSignalLoad(path):
    '''二维FFT信号读取'''
    signal = np.loadtxt(path)
    return signal

def ShowFFT(signal,ax):
    '''动态显示FFT数据'''
    # plt.ion()
    # ax.set_xlabel("dopfft")
    # ax.set_ylabel("range")
    # ax.set_xlim(0, 80)
    # ax.set_ylim(0, 150)
    # ax.set_zlim(-10, 200)
    ax.plot_surface(128, 64, signal, rstride=4, cstride=4, cmap='rainbow')  #
    plt.pause(0.001)
    plt.cla()  # 清屏

def main():
    fig = plt.figure()
    ax = plt.axes(projection = '3d')
    xx = np.arange(0,64,1)
    yy = np.arange(0,128,1)
    dopfftAxis,rangeAxis = np.meshgrid(xx,yy)
    dopfftLenght,rangeLenght = dopfftAxis.shape

    # baseSignal = BaseSignalGen()
    # SignalSave2txt(baseSignal,'base')
    baseSignal = FFTSignalLoad("./base.txt")
    targetSignal = np.zeros((dopfftLenght,rangeLenght),np.float)

    plt.ion()
    ax.set_xlabel("dopfft")
    ax.set_ylabel("range")
    ax.set_xlim(0,80)
    ax.set_ylim(0,150)
    ax.set_zlim(-10,200)
#plt.show()
    while(1):
        randSignal = RandomSignalGen(dopfftLenght,rangeLenght)
        signal =  randSignal + baseSignal
        ax.plot_surface(dopfftAxis, rangeAxis, signal, rstride=4, cstride=4, cmap='rainbow')  #
        plt.pause(0.001)
        plt.cla()  # 清屏

if __name__ == '__main__':
    main()

