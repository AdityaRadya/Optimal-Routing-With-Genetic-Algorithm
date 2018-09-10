import pandas as pd
import random as rn
import numpy as np

class genetic(object):
    def __init__(self,popNum, dcNum, satNum, retNum, retData, satData, dcData, distance, demand, cVehicle, cSatelite):
        self.popNum = popNum
        self.pc = 0.7
        self.pm = 0.3
        #Number of DC
        self.dcNum = dcNum
        #Number of Satelite
        self.satNum = satNum
        #Number of retails
        self.retNum = retNum
        #List of retails name
        self.oriDataRetail = retData
        #List of satelites name
        self.oriDataSat = satData
        #List of DC
        self.oriDataDc = dcData
        #Used since data set for retail start after the dc and sat data
        self.indexRet = dcNum + satNum
        #Dataset
        self.dataDistance = distance
        self.dataDemand = demand
        self.datacVehicle = cVehicle
        #Capacity of the Satelite
        self.datacSatelite = cSatelite
        self.pop = []
        self.count = 0
        self.generateSol()
        
    def generateSol(self):
        for num in range(self.popNum):
            #Asign a satelite with a dc
            s1 = [rn.randint(0,self.dcNum-1) for i in range(self.satNum)]
            #Permutation of the retails
            r1 = []
            for i in range(self.retNum):
                r1.append(self.oriDataRetail[i])
            rn.shuffle(r1)
            #Asigning the retail to a satelite
            r2 = [rn.randint(0,self.satNum-1) for i in range(self.retNum)]
            chromo = []
            chromo.append(s1)
            chromo.append(r1)
            chromo.append(r2)
            fitness = self.fitness(chromo)
            chromo.append(fitness)
            self.pop.append(chromo)
            
    def multipointCrossover(self,x,y):
        size = len(x)
        #Singlepoint Crossover when size if 2 and 1
        if size==2:
            return [x[0],y[1]],[y[0],x[1]]
        if size==1:
            return y,x
        
        index1 = rn.randint(1, size - 2)
        index2 = rn.randint(1, size - 2)
        if index1 > index2: index1, index2 = index2, index1
        return y[:index1] + x[index1:index2] + y[index2:], x[:index1] + y[index1:index2] + x[index2:]
    
    def orderCrossover(self,p1,p2):
        size = len(p1)
        #Index for ordered
        index1 = rn.randint(0, size-2)
        index2 = rn.randint(0, size-2)
        if index1 > index2: index1, index2 = index2, index1
        temp = []
        for i in range(size):
            orderCek = 0
            for j in range(index1, index2):
                #To check data within range
                if p2[i]==p1[j]: 
                    orderCek = 1
                    break
            if orderCek == 0:
                val = p2[i]
                temp.append(val)
        return temp[:index1] + p1[index1:index2] + temp[index1:]
                        
    def permutationCrossover(self,x,y):
        a = self.orderCrossover(x,y)
        b = self.orderCrossover(y,x)
        return a, b
    
    def crossover(self,x,y):
        s11,s12 = self.multipointCrossover(x[0],y[0])
        r11,r12 = self.permutationCrossover(x[1],y[1])
        r21,r22 = self.multipointCrossover(x[2],y[2])
        return [s11,r11,r21], [s12,r12,r22]
        
    def mutation(self,x):
        s1 = self.mutationS1(x[0])
        r1 = self.mutationR1(x[1])
        r2 = self.mutationR2(x[2])
        chromo = [s1,r1,r2]
        return chromo
        
    def mutationS1(self,y):
        x = y[:]
        for i in range(self.satNum):
            randomVal = rn.uniform(0, 1)
            if randomVal <= self.pm: x[i] = rn.randint(0,self.dcNum-1)
        return x    
                        
    def mutationR1(self,y):
        x = y[:]
        swapInd = 1
        tempIndex = 0
        for i in range(self.retNum):
            randomVal = rn.uniform(0, 1)
            if randomVal <= self.pm:
                #Indicate the 2nd index of swap
                swapInd = swapInd*-1
                if swapInd == -1: tempIndex = i
                if swapInd == 1: x[tempIndex], x[i] = x[i], x[tempIndex]
        return x
        
    def mutationR2(self,x):
        r2 = x[:]
        #satUsed numbers of satelite used
        for i in range(self.retNum):
            randomVal = rn.uniform(0, 1)
            if randomVal <= self.pm:
                r2[i] = rn.randint(0,self.satNum-1)
        return r2   
    
    #Group the retail with the asign satelite
    def routingRet(self, r1, r2):
        route = [[] for i in range(self.satNum)]
        for i in range(self.retNum): route[r2[i]].append(r1[i])
        return route
    
    #Distance of 2 places x and y
    def getDistance(self, x, y):
        return self.dataDistance.loc[x,y]
    
    #Get the demands of retail x
    def getDemand(self, x):
        return self.dataDemand.loc[x,self.dataDemand.columns[-1]]
    
    #Get the cost of a vehicle from the dataset
    def costVehicle(self, x):
        return self.datacVehicle.loc[self.datacVehicle.index[0],x]
    
    #Get the capacity of a vehicle from the dataset
    def capacityVehicle(self, x):
        return self.datacVehicle.loc[self.datacVehicle.index[1],x]
    
    #Get capacity of Satelite
    def capacitySatelite(self, x):
        return self.datacSatelite.loc[self.datacSatelite.index[0],x]
    
    #Get cost per vehicle
    def costPerVehicle(self, x):
        return self.datacVehicle.loc[self.datacVehicle.index[2],x]
    
    #Find route that satisfy the capacity of vehicle (Secondary)
    def routeCost(self, sPosition, route):
        sizeRoute = len(route)
        cost = 0
        capacity = 0
        prev = 0
        if not route: return 0
        for i in range(sizeRoute):
            capacity += self.getDemand(route[i])
            if capacity > self.capacityVehicle(self.datacVehicle.columns.values[1]):
                cost += self.capRoute(sPosition, route[prev:i])
                prev = i
                capacity = self.getDemand(route[i])
                #Add cost of vehicle into the cost value
                cost += self.costPerVehicle(self.datacVehicle.columns.values[1])
            if i == sizeRoute-1:
                cost += self.capRoute(sPosition, route[prev:])
                cost += self.costPerVehicle(self.datacVehicle.columns.values[1])
        return cost
            
    
    #cost with full capacity, secondary vehicle
    def capRoute(self,sPosition, route):
        sizeRoute = len(route)
        totalDist = self.getDistance(sPosition, route[0])
        totalDist += self.getDistance(sPosition, route[sizeRoute-1])
        for i in range(1,sizeRoute):
            totalDist += self.getDistance(route[i-1],route[i]) 
        cost = totalDist*self.costVehicle(self.datacVehicle.columns.values[1])
        return cost

    def fitness(self, chromo):
        cost = 0
        route = self.routingRet(chromo[1],chromo[2])
       
        #cost for route truck, dc to satelite    
        totalDistanceTruck = 0
        for i in range(self.satNum):
            if not route[i]:
                continue
            else:
                totalDistanceTruck += 2*(self.getDistance(self.dataDistance.columns.values[chromo[0][i]], self.oriDataSat[i]))
                cost += self.costPerVehicle(self.datacVehicle.columns.values[0])
        cost += totalDistanceTruck *self.costVehicle(self.datacVehicle.columns.values[0])
        
        #cost for route motor, satelite to retail
        for i in range(self.satNum):
            cost += self.routeCost(self.oriDataSat[i], route[i])
        
        #Check for contraints in the Satelite
        for sat in range(self.satNum):
            capSat = 0
            for ret in route[sat]:
                capSat += self.getDemand(ret)
            if self.capacitySatelite(self.oriDataSat[sat]) - capSat < 0:
                cost += 10000000
        
        return 1/cost
        
    def parentSelection(self):
        parArr=[]
        totalFitness = 0
        for val in self.pop:
            totalFitness += val[3]
        
        propFitness = [f[3]/totalFitness for f in self.pop]
        #Roulette Wheel, Creating Wheel
        wheel = [sum(propFitness[:i+1]) for i in range(self.popNum)]
        
        #Parent Selection
        for i in range(int(self.popNum/4)):
            selectIndex = rn.random()
            for j in range(self.popNum):
                if selectIndex <= wheel[j]: 
                    parArr.append(self.pop[j])
                    break
            for j in range(self.popNum):
                if 1-selectIndex <= wheel[j]: 
                    parArr.append(self.pop[j])
                    break
        return parArr
    
    def updatePop(self, x):
        self.pop = x
    
    def cost(self, x):
        cost = 0
        route = self.routingRet(x[1],x[2])
        #cost for route truck, dc to satelite    
        totalDistanceTruck = 0
        for i in range(self.satNum):
            if not route[i]:
                continue
            else:
                totalDistanceTruck += 2*(self.getDistance(self.dataDistance.columns.values[x[0][i]], self.oriDataSat[i]))
                cost += self.costPerVehicle(self.datacVehicle.columns.values[0])
        cost += totalDistanceTruck *self.costVehicle(self.datacVehicle.columns.values[0])
        
        #cost for route motor, satelite to retail
        for i in range(self.satNum):
            pp = 1
            cost += self.routeCost(self.oriDataSat[i], route[i])
            
        for sat in range(self.satNum):
            capSat = 0
            for ret in route[sat]:
                capSat += self.getDemand(ret)
            if self.capacitySatelite(self.oriDataSat[sat]) - capSat < 0:
                cost += 0
        return cost
    
	#Printing the results
    def translatorSol(self, chromo):        
        path = self.routingRet(chromo[1],chromo[2])
        count = 0
        for i in range(self.satNum):
            if not path[i]:
                count+=1
            else:
                print(self.oriDataDc[chromo[0][i]] ," to ",  self.oriDataSat[i])
        for i in range(self.satNum):
            self.printPath(self.oriDataSat[i], path[i])
        return
    
    def printPath(self, sPosition,route):
        sizeRoute = len(route)
        capacity = 0
        prev = 0
        if not route: return 0
        for i in range(sizeRoute):
            capacity += self.getDemand(route[i])
            capVehicle = self.capacityVehicle(self.datacVehicle.columns.values[1])
            if capacity > capVehicle:
                self.printRoute(sPosition, route[prev:i])
                prev = i
                capacity = self.getDemand(route[i])
            if i == sizeRoute-1:
                self.printRoute(sPosition, route[prev:])
        return
         
    def printRoute(self, sPosition, route):
        x = route[:]
        print(sPosition ," -> ", x," -> ", sPosition)
        return
        
