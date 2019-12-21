import Generator
import  matplotlib.pyplot as plt
import numpy as np

class Point:
    def __init__(self,x = 0, y = 0, movtype = None,speed = 0, angle = 0, accelerate = 0,frameno = 0,**kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.frameno = frameno
        self.accelerate = accelerate
        self.movetype = movtype

    def display(self):
        print("当前点的坐标为：("+ self.x +","+self.y+")")
        print("当前点的速度为："+self.speed)
        print("当前点的角度为："+self.angle)
        print("当前点的加速度为："+self.accelerate)
        print("当前帧号：" + self.frameno)

class RealPoint(Point):
    def __init__(self, x = 0, y = 0, speed=0, angle=0, frameno=0):
        super().__init__(x, y, speed, angle, frameno)
        self.color = 'red'
        self.flag = 1

class FakePoint(Point):
    def __init__(self, x=0, y=0, speed=0, angle=0, frameno=0):
        super().__init__(x, y, speed, angle, frameno)
        self.color = 'blue'
        self.flag = 0

class FrameInfor:
    def __init__(self,realtracknum = 5, faketracknum = 10, frameno  = 0,lastframe = None):
        self.points_list = []
        self.realtracknum = realtracknum
        self.faketracknum = faketracknum
        self.frameno = frameno

        if lastframe == None :#第一帧数据由用户手动给出
            for i in range(int(self.realtracknum)):
                print("第", i + 1, "个航迹的运动类型(UL,AL,UT)：", end='')
                movtype = input()
                if movtype != 'UL' and movtype != 'AL' and movtype != 'UT':
                    raise Exception("Wrong Move Type!")

                print("第", i + 1, "个航迹的x坐标（-30~30）：", end='')
                x = float(input())
                print("第", i + 1, "个航迹的y坐标（0~40）：", end='')
                y = float(input())
                print("第", i + 1, "个航迹的初始速度：", end='')
                speed = float(input())
                print("第", i + 1, "个航迹的运动角度(-0.2~0.2)：", end='')
                angle = float(input())
                if movtype == 'AL':
                    print("第", i + 1, "个航迹的加速度：", end='')
                    accelerate = float(input())
                else:
                    accelerate = 0.0
                RP = Generator.RealPtGenerator(x,y,movtype,speed,accelerate,angle)
                self.points_list.append(RP)

            for i in range(int(self.faketracknum)):
                FP = Generator.FakePtGenerator()
                self.points_list.append(FP)

        else:
            self.lastframe = lastframe


    def creat_frame(self):
        for point in self.lastframe.points_list:
            if point.flag == 1:  #如果当前点为真实点，则将改点传入对应的真实点产生函数中
                RP = Generator.RealPtGenerator(point.x, point.y, point.movetype, point.speed,point.accelerate,point.angle)
                self.points_list.append(RP)

            else:#如果当前点为虚假点，则调用虚假点产生函数
                FP = Generator.FakePtGenerator()
                self.points_list.append(FP)


    def show_frame(self):
        for point in self.points_list:
            print("(x,y): (",point.x,",",point.y,")" , "   speed:" , point.speed , "  angle:" ,point.angle)
            plt.scatter(point.x, point.y, c=point.color)
        plt.xlim((-30, 30))
        plt.ylim((0, 40))
        plt.show()

    def save_frame(self):
        i = 0
        savedata = []
        for point in self.points_list:
            savedata.append([point.x, point.y, point.speed, point.angle, point.flag])
            i += 1
        savepath = "./simufile/simufile_" + str(self.frameno) + '.txt'
        np.savetxt(savepath,savedata,fmt='%.3f')

        #file_handle = open("./simfile/")

class SimuData:
    def __init__(self):
        self.frame = []

        self.realtracknum = input("产生的真实航迹的个数：")
        self.faketracknum = input("虚假点迹数量（帧）：")
        self.framenum = input("仿真数据帧数：")
        FI = FrameInfor(self.realtracknum,self.faketracknum)

        self.frame.append(FI)
    def create_simu(self):
        for i in range(int(self.framenum)):
            FI = FrameInfor(self.realtracknum,self.faketracknum,frameno=i+1,lastframe=self.frame[-1])
            FI.creat_frame()
            self.frame.append(FI)

    def show_simu(self):
        for frame in self.frame:
            for point in frame.points_list:
                plt.scatter(point.x, point.y, c=point.color)
        plt.xlim((-30, 30))
        plt.ylim((0, 40))
        plt.show()

    def save_simu(self):
        for frm in self.frame:
            frm.save_frame()


def main():
    SD = SimuData()
    SD.create_simu()
    SD.save_simu()
    SD.show_simu()


if __name__ == "__main__":
    main()
