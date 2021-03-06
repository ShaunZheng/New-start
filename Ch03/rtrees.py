# -*-coding:utf-8-*-
from math import log
import operator

# 构造一个数据集
def createDataSet():
	dataSet = [[1,1,'yes'],[1,1,'yes'],[1,0,'no'],[0,1,'no'],[0,1,'no']]
	labels = ['no surfacing','flippers']
	return dataSet,labels
dataSet,labels = createDataSet()
'''
一、计算香农熵步骤：

设总共有n种类别

1.计算某第i类别所占全部类别数的比例（概率）： p(i)；

2.计算信息-log2(p(i));

3.求熵：即求n种类别的信息的期望。

'''
# My method
# 貌似不够健壮：
def calcShannonEnt(dataSet):
	numAll = len(dataSet)
	countY = 0
	countN = 0
	for featVec in dataSet:
		if featVec[-1] == 'yes':
			countY += 1
		else:
			countN += 1
	pY = float(countY)/numAll
	pN = float(countN)/numAll
	infoN =0
	infoY =0
	if pY == 0:
		shannonEnt = pN*infoN
	if pN == 0:
		shannonEnt = pY*infoY
	if pY != 0 and pN != 0:
		infoY = -log(pY,2)
		infoN = -log(pN,2)
		shannonEnt = pY*infoY + pN*infoN
	return shannonEnt
# print calcShannonEnt(dataSet)
'''
二、划分数据集

1.这里相当于是对树的根节点进行分叉，即对数据集dataSet按照某特征值进行划分；

2.分叉完事后，要得到新的小的数据集，同时数据集的特征减少1，并完成了一次划分；

3.注意参照图3-2理解。

4.编码需要实现：如果dataSet上的axis轴上的值等于value，那么取出该行的其它特征值存到数组

'''
def splitDataSet(dataSet,axis,value):
	numAll = len(dataSet)
	retDataSet = []
	for i in range(numAll):
		if dataSet[i][axis] == value:
			'''
			front = dataSet[i][:axis+1]
			print front
			rear = dataSet[i][axis+1:]
			print rear
			注意：这种做法是错误的，这里的extend返回值是None，改变的仅仅是front的值，
			并不会将修改后的值赋值到reduceFR。部分函数是返回None，有些则是可以返回到
			赋值的变量的，特此提醒！
			reduceFR = front.extend(rear)
			print reduceFR
			retDataSet.append(reduceFR)
			'''
			reduceFR = dataSet[i][:axis]
			rear = dataSet[i][axis+1:]
			reduceFR.extend(rear)
			retDataSet.append(reduceFR)		
	return retDataSet

'''
三、选择最好的数据集划分方式：（也就是求信息增益，同时排序，找到增益最大的）

1.根据轴axis，选择不同的划分方式；

2.在一次划分中 ，可能会将当前轴，根据值的不同，划分成多个数据集；
（相当于根据某个特征，进行树分叉，得到多个子节点）

3.对产生的每个数据集进行香农熵计算；

4.对香农熵求均值；

5.计算信息增益；

6.找到最大增益，同时得到其是那哪个轴划分的。

'''
def chooseBestFeatureToSplit(dataSet):
	numAxis = len(dataSet[0]) - 1
	# 程序的信息增益小于0时，设置bestAxis为-1，表示出错。
	bestAxis = -1
	bestInfoGain = 0.0
	
	for i in  range(numAxis):
		axisFeatures = [feature[i] for feature in dataSet]
		# print axisFeatures
		values = set(axisFeatures)
		# print values
		sumChildEnt = 0.0
		for value in values:
			childDataSet = splitDataSet(dataSet, i, value)
			# print childDataSet
			childEntropy = calcShannonEnt(childDataSet)
			# print childEntropy
			pValue = float(len(childDataSet))/len(dataSet)
			sumChildEnt += pValue*childEntropy 
		infoGain = calcShannonEnt(dataSet) - sumChildEnt
		if (infoGain > bestInfoGain):
			bestInfoGain = infoGain
			bestAxis = i
	# print bestAxis
	return bestAxis

'''
四、定义函数，求出现次数最多的分类的名称

1. 传入所有的类别列表值；

2.找出数量最多的那一类；

3.自己的代码，显然健壮性不够好：
		
def majorityCnt(classList):
	countDic = {}
	classSet = set(classList)
	for key in classSet:
		count = 0
		for i in range(len(classList)):
			if classList[i] == key:
				count =count + 1
				countDic[key] = count
	if countDic["yes"] > countDic["no"]:
		sortedClassCount = "yes"
	else:
		sortedClassCount = "no"
	return sortedClassCount
'''
# My method
# 改进版：
classList = [i[-1] for i in dataSet]
# print classList
def majorityCnt(classList):
	countDic = {}
	classSet = set(classList)
	for key in classSet:
		countDic[key] = 0
		for i in range(len(classList)):
			if classList[i] == key:
				countDic[key] += 1
	sortedClassCount = sorted(countDic.iteritems(),key=operator.itemgetter(1),reverse = True)
	return sortedClassCount[0][0]		
# 官方代码：
# def majorityCnt(classList):
# 	classCount = {}
# 	for vote in classList:
# 		if vote not in classCount.keys(): 
# 			classCount[vote]=0
# 		classCount[vote] += 1
# 	sortedClassCount = sorted(classCount.iteritems(),key = operator.itemgetter(1),reverse = True)
# 	print sortedClassCount[0][0]
# 	return sortedClassCount[0][0]


'''
五、使用递归，建立一棵树：

1.如果都是一类，那么直接返回；

2.如果用完了所有的特征，还没能分类，这时候只有多个目标变量了。那么根据目标变量的种类的数目，最多的作为类别的返回值；

3.使用字典存储树，利用递归，网字典里存，直到结束。

'''
def createTree(dataSet,labels):
	classList = [example[-1] for example in dataSet]
	if len(set(classList)) == 1:
		return classList[0]
	if len(dataSet[0]) == 1:
		return majorityCnt(classList)
	bestFeat = chooseBestFeatureToSplit(dataSet)
	# print "bestFeat===>",bestFeat
	bestFeatLabel = labels[bestFeat]
	myTree = {bestFeatLabel:{}}
	del(labels[bestFeat])
	featValues = [example[bestFeat] for example in dataSet]
	uniqueVals = set(featValues)
	for value in uniqueVals:
		subLabels = labels[:]
		myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value),subLabels)
	return myTree

# def createTree(dataSet,labels):
# 	# print labels
# 	classList = [example[-1] for example in dataSet]
# 	if classList.count(classList[0]) == len(classList):
# 		return classList[0]
# 	if len(dataSet[0]) == 1:
# 		return majorityCnt(classList)
# 	bestFeat = chooseBestFeatureToSplit(dataSet)
# 	bestFeatLabel = labels[bestFeat]
# 	# print bestFeatLabel
# 	# print type(bestFeatLabel)
# 	myTree = {bestFeatLabel : {}}
# 	del(labels[bestFeat])
# 	featValues = [example[bestFeat] for example in dataSet]
# 	uniqueVals = set(featValues)
# 	for value in uniqueVals:
# 		subLabels = labels[:]
# 		myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet,bestFeat,value),subLabels)
# 	return myTree



dataSet,labels = createDataSet()
print createTree(dataSet, labels)


# print createDataSet()
# print chooseBestFeatureToSlipt(dataSet)
# print createDataSet()
# majorityCnt(classList)
print splitDataSet(dataSet,0,0)
print splitDataSet(dataSet,0,1)
# chooseBestFeatureToSlipt(dataSet)