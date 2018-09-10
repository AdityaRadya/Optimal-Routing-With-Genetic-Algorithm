import pandas as pd
import random as rn
import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from GA import genetic
from loading import printProgressBar

popNum = 500
generationNum = 100

data = input("Input File name : ")
data.replace(" ", "")

distance = pd.read_excel('Data/'+data+'.xlsx', sheet_name="distance", index_col=0)
demand = pd.read_excel('Data/'+data+'.xlsx', sheet_name="demand", index_col=0)
costVehicle = pd.read_excel('Data/'+data+'.xlsx', sheet_name="vehicle", index_col=0)
capSatelite = pd.read_excel('Data/'+data+'.xlsx', sheet_name="satelite", index_col=0)

#Value to determine the percentage of best chromo for next gen
satNum = capSatelite.shape[1]
retNum = demand.shape[0]
dcNum = distance.shape[1] - satNum - retNum
retData1 = demand.index[:]
satData = distance.index[dcNum:satNum+dcNum]
dcData = distance.index[:dcNum]
retData = []

#Convert pandas into normal array
for i in range(retNum):
    retData.append(retData1[i])
	
settings = input("Change Setting [Y/N] : ")
if settings == "Y" or settings == "y" or settings == "yes" or settings == "Yes":
	popNum = int(input("Population Number (500) : "))
	generationNum = int(input("Total Generation (100) : "))

ga = genetic(popNum, dcNum, satNum, retNum, retData, satData, dcData, distance, demand, costVehicle, capSatelite)

if settings == "Y" or settings == "y" or settings == "yes" or settings == "Yes":
	ga.pm = float(input("Input Probability Mutation (0.3) : "))
	ga.pc = float(input("Input Probability Crossover (0.7) : "))

printProgressBar(1, generationNum, prefix = 'Progress:', suffix = 'Complete', length = 50)
fitness = []
start = timer()
for generation in range(generationNum):
	rn.shuffle(ga.pop)
	parents = ga.parentSelection()
    #Randomize parents array
	newPop = ga.pop
    
	for parentIndex in range(1,int(popNum/2)):
		randomVal = rn.random()
		if randomVal < ga.pc:
			child1, child2 = ga.crossover(parents[parentIndex-1], parents[parentIndex])
			child1, child2 = ga.mutation(child1), ga.mutation(child2)
			child1.append(ga.fitness(child1))
			child2.append(ga.fitness(child2))
			newPop.append(child1)
			newPop.append(child2)
	newPop = sorted(newPop,key=lambda l:l[3],reverse=True)
	nextPop = newPop[:popNum]
	ga.updatePop(nextPop)
	fitness.append(ga.cost(ga.pop[0]))
	printProgressBar(generation+1, generationNum, prefix = 'Progress:', suffix = 'Complete', length = 50)
 
ga.translatorSol(ga.pop[0])
print("Cost : ",ga.cost(ga.pop[0]))
end = timer()
print ("Time : ",end - start)

import matplotlib.pyplot as plt
index = [i for i in range(generationNum)]
plt.plot(index, fitness)
plt.xlabel('Epoch')
plt.ylabel('Cost')
plt.title('Result')
plt.show()
