#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2020.2.17
#功能：仿真航迹产生主函数
#auther： woody sun
'''
import SimuGen
SimuTime = 6#设置仿真次数
def main():
    global SimuTime
    for i in range(SimuTime):
        simulinkData = SimuGen.SimuData(autoTestEn = True)
        simulinkData.CreateSimu()
        simulinkData.SaveSimu(i)
        #simulinkData.ShowSimu()


if __name__ == "__main__":
    main()
