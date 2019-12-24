#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.24
#功能：绘制航迹并保存为GIF，输入为txt文件。内容顺序格式为：[ 'Speed', 'Angle',  'Target','X_position', 'Y_position']
#auther： woody sun
'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

fig,ax = plt.subplots()
xdata, ydata = [], []
tln,  = plt.plot([],[],'o',color = 'red', animated = True)
fln, = plt.plot([],[],'o',color = 'gray', markersize = 2,animated = True)

def init():
    '''动画对象初始化函数'''
    ax.set_xlim(-30,30)
    ax.set_ylim(0,40)
    return tln,fln,


def update(frames):
    '''动画对象更新函数'''
    framepath = './simufile/simufile_' + str(frames) + '.txt'
    names = [ 'Speed', 'Angle',  'Target','X_position', 'Y_position']
    tracks = pd.read_csv(framepath, sep=' ', names=names)
    faketracks = tracks[tracks['Target'].isin([0])]  # 选择当前航迹中所有虚假点
    xdata = faketracks['X_position']
    ydata = faketracks['Y_position']
    fln.set_data(xdata, ydata)
    truetracks = tracks[tracks['Target'].isin([1])]  # 选择当前航迹中所有真实点
    xdata = truetracks['X_position']
    ydata = truetracks['Y_position']
    tln.set_data(xdata,ydata)

    return tln,fln,


def main():
    anim = animation.FuncAnimation(fig, update, frames=range(10), interval=400, init_func=init,blit=True)
    plt.show()
    anim.save('test_animation.gif', writer='imagemagick')

if __name__ == '__main__':
    main()
