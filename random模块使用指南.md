# random模块使用指南

用于产生伪随机数，源码位置Lib/random.py<br>
由于计算机伪随机数是通过随机种子和一定的计算方法得到的，所以随机种子和计算方法确定之后，则伪随机数是可以直接计算得到的，所以不能用于密码设置。<br>

## 基本方法
random.seed(a = None, version = 2)<br>
初始化伪随机数生成器。a为种子设置参数，默认为系统时钟。

random.seed(10)
random.randint(0,10)
random.randint(0,10)
每次产生相同的随机数

random.getstate()<br>
返回当前生成器的内部状态对象

random.setstate(state)<br>
传入先前利用getstate获得的状态对象，使生成器恢复到这个状态。可以使每一次random产生相同的数值。保证多次运行获得相同输出。

## 产生随机整数
random.randrange([start,]stop[,step])<br>
产生一定范围内的随机整数

random.randint(a,b)<br>
产生一个a <= N <= b的随机整数N。等同于random.randrange(a,b+1)

## 设定浮点数与特定分布
random.random()<br>
返回一个介于[0.0,1.0)区间的浮点数<br>
random.uniform(a,b)<br>
返回一个[a,b]之间的一个浮点数<br>
random.triangular(low,high,mode)<br>
返回一个low<=N<=high的三角形分布的随机数，参数mode指明众数出现的位置<br>
random.betavariate(alpha,beta)<br>
返回一个beta分布的数，返回结果在0~1之间<br>
random.expovariate(lambd)<br>
指数分布<br>
random.gammavariate(alpha,beta)<br>
伽马分布<br>
random.gauss(mu,sigma)<br>
高斯分布<br>
random.lognormvariate(mu,sigma)<br>
对数正态分布<br>
random.normalvariate(mu,sigma)<br>
正态分布<br>

## 序列类随机取值
random.choice(seq)<br>
从非空序列seq中随机选取一个元素。如果seq为空则弹出IndexError异常<br>
random.choices(population,weights = None, *,cum_weights = None, k = 1)<br>
3.6版本新增。从population集群中随机抽取K个元素。weights是相对权重列表，cum_weights是累计权重，两个参数不能同时存在。<br>
random.shuffle(x[,random])<br>
随机打乱序列x内元素的排列顺序。只能针对可变的序列，对于不可变序列，请使用下面的sample()方法。<br>
random.sample(population,k)<br>
从population样本或集合中随机抽取K个不重复的元素形成新的序列。常用于不重复的随机抽样。返回的是一个新的序列，不会破坏原有序列。要从一个整数区间随机抽取一定数量的整数，请使用sample(range(10000000), k=60)类似的方法，这非常有效和节省空间。如果k大于population的长度，则弹出ValueError异常。<br>





