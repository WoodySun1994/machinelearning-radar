#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.24
#功能：绘制航迹并保存为GIF，输入为txt文件。内容顺序格式为：[ 'Speed', 'Angle','X_position', 'Y_position',  'Target']
#auther： woody sun
'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

fig,ax = plt.subplots()
xData, yData = [], []
trueLine,  = plt.plot([],[],'o',color = 'red', animated = True)
fakeLine, = plt.plot([],[],'o',color = 'gray', markersize = 2,animated = True)

def Init():
    '''动画对象初始化函数'''
    ax.set_xlim(-30,30)
    ax.set_ylim(0,40)
    return trueLine,fakeLine,


def Update(frames):
    '''动画对象更新函数'''
    framePath = './simufile0/frame_' + str(frames) + '.txt'
    names = [ 'Speed', 'Angle','X_position', 'Y_position',  'Target']
    tracks = pd.read_csv(framePath, sep=' ', names=names)
    fakeTracks = tracks[tracks['Target'].isin([0])]  # 选择当前航迹中所有虚假点
    xData = fakeTracks['X_position']
    yData = fakeTracks['Y_position']
    fakeLine.set_data(xData, yData)
    trueTracks = tracks[tracks['Target'].isin([1])]  # 选择当前航迹中所有真实点
    xData = trueTracks['X_position']
    yData = trueTracks['Y_position']
    trueLine.set_data(xData,yData)

    return trueLine,fakeLine,


def main():
    anim = animation.FuncAnimation(fig, Update, frames=range(10), interval=400, init_func=Init,blit=True)
    plt.show()
    anim.save('simu0.gif', writer='imagemagick')

if __name__ == '__main__':
    main()
