#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
更新：“2019.12.25
#功能：仿真航迹产生
#auther： woody sun
'''
import SimuGen

def main():
    for i in range(30):
        SD = SimuGen.SimuData(autotesten = True)
        SD.create_simu()
        SD.save_simu(i)
        # SD.show_simu()


if __name__ == "__main__":
    main()
