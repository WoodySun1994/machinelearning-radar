#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.25
#功能：仿真航迹产生
#auther： woody sun
'''
import SimuGen

def main():
    for i in range(50):
        simulinkData = SimuGen.SimuData(autoTestEn = True)
        simulinkData.CreateSimu()
        simulinkData.SaveSimu(i)
        #simulinkData.ShowSimu()


if __name__ == "__main__":
    main()
