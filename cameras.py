import random
import collections

print('this is the random number before seeding cameras')
print(random.random())
random.seed(7)

print('this is the random number after seeing cameras')
print(random.random())

import shortestpath
from scipy import misc
import numpy as np
import pandas as pd
import time 



#%%

## class to set up the filereader - reads files in and out
## reads Paint map in, reads origin-destination matrix in, saves simulated
## camera counts... ultimately needs to read simulated camera counts in and
## write optimised origin-destination matrix out


class IO:
    
    def readMap(self):    
        arr = misc.imread('mapofleeds.png')

        data =[[arr[j, i, 0] for i in range(arr.shape[1])] for j in range(arr.shape[0])]

        #print(np.unique(data))

        for i in range(len(data)):
            for j in range(len(data[0])):
                if data[i][j] == 255:
                    data[i][j] = 'B'  # B for buildings
                if data[i][j] == 0:
                    data[i][j] = 'C'  # C for camera potential spots
                if data[i][j] == 195:
                    data[i][j] = 'R' # R for roads (pavements etc.)
                if data[i][j] == 237:
                    data[i][j] = 'E' # E for entrance/exits
                    
        return data

    
    def readMatrix(self):

        df = pd.read_csv('matrix.csv', index_col=['Area'])
        matrix = df.as_matrix()
        
        return matrix

    def readCounts(self):
        pass

    def writeCounts(self, dataIn, columnsIn):
        datatranspose = list(map(list, zip(*dataIn)))
        df = pd.DataFrame(data = datatranspose, columns = columnsIn)
        df.to_csv('out.csv')
        

    def writeMatrix(self, dataIn):
        
        thelist = dataIn

        outfilename = ('out.txt')

        with open(outfilename, 'w') as f:
            for item in thelist:
                f.write(",".join(map(str, item)) + "\n")
        f.close()

        
        return



#%%

## base class Agent

class Agent(object):

    def run(self):
        pass

#%%

## Person inherits Agent

class Person(Agent):
    
    def __init__(self, worldIn, agentsIn):
        self.x = 50
        self.y = 150
        self.world = worldIn
        self.agents = agentsIn
        
    def run(self):
        pass
        
    
#%%
    
## Worker inherits Person    
##
## Each worker has (by default) a random home and random work location.
## However, adjustTimes can be called in the main program to match the number
## of workers going to and from each point to an origin-destination matrix.
## They have a corresponding 'home->work' journey that is calculated
## using the shortestpath.shortestjourney method (which currently
## minimises distances while avoiding any boxes not marked with 'R' for road).
## Each iteration the time is assessed and based on how long their journey
## is the workers will set off at the right time to arrive for 9am.
## Workers all leave home at 5pm, arriving back home at a time dependent
## on their journey time.
## Their individual 'journey counters' keep track of how far along their
## commute they are, resetting to 1 when they arrive at their destination.
##    
## Workers have four states: at home, at work, journeying to work and 
## journeying home.

class Worker(Person):
  
    
    def __init__(self, worldIn, agentsIn):
        
        self.type = 'Worker'
        self.world = worldIn   
        self.agents = agentsIn
        self.walkingspeed = int(random.random()*3) # so far unused
                
        random.seed(86)
        
        ## calls world.getSpawns() to feed in a list of spawn points, 
        ## then assigns a 'home' and 'work' spawn randomly (making sure they're
        ## different)
        spawns = self.world.getSpawns()
        #print(spawns)
        self.entrancespawn = random.choice(spawns)
        while True:
            self.exitspawn = random.choice(spawns)
            if self.exitspawn != self.entrancespawn:
                break
        #print(self.entrancespawn)
        #print(self.exitspawn)
        
        # sets their initial position to their home, and the journey counter
        # to 0
        self.x = self.entrancespawn[0]
        self.y = self.entrancespawn[1]
        self.journeycounter = 0
        self.state = 'Home'
        
        # code to calculate their commute journey, and from that the 'setofftime'
        # that they need to leave work at
        # first the journey length:
        #self.journeytowork = shortestpath.shortestjourney([self.entrancespawn[0], self.entrancespawn[1]], [self.exitspawn[0], self.exitspawn[1]], self.world.data)
        #self.journeyhome = shortestpath.shortestjourney([self.exitspawn[0], self.exitspawn[1]], [self.entrancespawn[0], self.entrancespawn[1]], self.world.data)
        #print(self.journeytowork)
        #print(self.journeyhome)
        #self.journeylength = len(self.journeytowork) - 1
        # and then the journey time, and the appropriate set off time:
        # (journey time is counted as the number of points in their journey
        # divided by 4, with any remainder adding '1' to the journey time - 
        # this is so that each 'hour' the worker moves 4 squares)
        #self.starttime = 9*ticksToAnHour
        #self.endtime = 17*ticksToAnHour
        #self.setofftime = (self.starttime - self.journeylength)
        #self.journeytime = self.journeylength
        #print(self.setofftime)
        #print(self.journeytime)
        
        
    def adjustLocations(self, entryIn, exitIn, journeyWork, journeyHome):
        
        ## function used to adjust times to fit an origin-destination matrix
        ## decides new journey, and corresponding journey length, set off time,
        ## etc.
        
        self.entrancespawn = entryIn
        self.exitspawn = exitIn
        self.journeytowork = journeyWork
        self.journeyhome = journeyHome
        self.journeylength = len(self.journeytowork) - 1
        self.starttime = 9*ticksToAnHour
        self.endtime = 17*ticksToAnHour
        self.setofftime = (self.starttime - self.journeylength)
        self.journeytime = self.journeylength
        #print(self.setofftime)
        #print(self.journeytime)
        
        self.x = self.entrancespawn[0]
        self.y = self.entrancespawn[1]

        

        
    ## each workers' run function evaluates first the time input: if it's 
    ## their set off time they begin their commute to work, and if it's 5pm
    ## they begin their journey home
    ## if it's neither of those times their state is evaluated: at home remains
    ## at home, at work remains at work, whereas each time step they are 
    ## 'Journeying' they move another point along their journey and their journey
    ## counter is updated to keep track of their progress
    ## if their journey counter hits their journey time they arrive at their
    ## destination (this isn't necessary with 1 move per time step, but is
    ## necessary for e.g 4 moves per time step)

    def run(self, hourIn):


        if hourIn == self.setofftime:
            self.journeycounter = 0
            self.goToWork(self.journeycounter)
            self.journeycounter = self.journeycounter + 1
        elif hourIn == self.endtime:
            self.journeycounter = 0
            self.goHome(self.journeycounter)
            self.journeycounter = self.journeycounter + 1
        elif self.state == 'Journeying home':
            self.goHome(self.journeycounter)
            self.journeycounter = self.journeycounter + 1
        elif self.state == 'Journeying to work':
            self.goToWork(self.journeycounter)
            self.journeycounter = self.journeycounter + 1

            
    ## the goToWork function monitors the progress of the commute, 
    ## and updates the position of the worker along their journey            
    def goToWork(self, counterIn):
        if counterIn < self.journeytime:
            #print(counterIn)
            self.x = self.journeytowork[(counterIn)][0]
            self.y = self.journeytowork[(counterIn)][1]         
            self.state = 'Journeying to work'
        if counterIn == self.journeytime:
            self.x = self.exitspawn[0]
            self.y = self.exitspawn[1]
            self.state = 'At work'
    
    ## likewise the goHome function monitors the journey home,
    ## updating the position of the worker correspondingly
    def goHome(self, counterIn):
        
        if counterIn < self.journeytime:
            #print(counterIn)
            self.x = self.journeyhome[counterIn][0]
            self.y = self.journeyhome[counterIn][1]         
            self.state = 'Journeying home'
        if counterIn == self.journeytime:
            self.x = self.entrancespawn[0]
            self.y = self.entrancespawn[1]
            self.state = 'At home'


#%%

class Camera(object):
    
    ## each camera has a random location (only allowed on the building walls against
    ## the road) and a line of sight (one square of road in whatever direction
    ## the map dictates - if there's a choice of more than one square one is
    ## randomly selected)
    ## the cameras also all have a list of all the agents in the system, and
    ## they keep track of which of those agents is in their line of sight
    ## ('agentsenclosed')
    ## if an agent which was in 'agentenclosed' LAST time step is now no longer
    ## in the lineofsight THIS time step, then the counter is increased by 1
    ## every hour the counter is stored in hourlycount, and reset to 0
    
 
    def __init__(self, agentsIn, worldIn):
        
        self.world = worldIn
    
        self.agents = agentsIn
        self.agentsenclosed = []
        self.countsum = 0
        self.hourlycount = []
        
        locations = self.world.getCameraSpots()
        #print(locations)
        self.location = random.choice(locations)
        print(self.location)
        self.lineofsight = self.findLineOfSight()
        print(self.lineofsight)
    

    def setLocation(self, locationIn):
        
        self.location = locationIn
        self.lineofsight = self.findLineOfSight()    
    
    ## searches adjacent points for a road spot, adds it to the line of sight
    ## try-except blocks catch the out-of-index points (happens when cameras
    ## are placed right at the edge of the map)
    
    def findLineOfSight(self):
        
        lineofsight = []
        try:        
            adj1 = self.world.data[self.location[0]+1][self.location[1]]
            if adj1 == 'R':
                lineofsight.append([(self.location[0])+1, self.location[1]])
        except IndexError:
            pass
        try:
            adj2 = self.world.data[(self.location[0])-1][self.location[1]]
            if adj2 == 'R':
                lineofsight.append([(self.location[0])-1, self.location[1]])
        except IndexError:
            pass
        try:        
            adj3 = self.world.data[self.location[0]][(self.location[1])+1]
            if adj3 == 'R':
                lineofsight.append([self.location[0], (self.location[1])+1])
        except IndexError:
            pass
        try:
            adj4 = self.world.data[self.location[0]][(self.location[1])-1]
            if adj4 == 'R':
                lineofsight.append([self.location[0], (self.location[1])-1])
        except IndexError:
            pass
        
        ## this try-except block checks to see if the array lineofsight contains
        ## more than one point
        ## if there is, it chooses one of these points at random as the lineofsight
        ## if not (TypeError), it simply continues to return the single point 
        ## if there isn't even a single lineofsight point (IndexError), the camera
        ##         
        try: 
            len(lineofsight[0])
            lineofsight = lineofsight[0]
        except TypeError:
            pass
        except IndexError:
            pass
        
        return [lineofsight]
        

    ## checks for agents in line of sight, adds them to agentsenclosed  
    def updateAgentsEnclosed(self):
        for agent in self.agents:
            if [agent.x, agent.y] in self.lineofsight:
                #print("An agent is in sight!")
                self.agentsenclosed.append(agent)
                
    ## checks to see if any of the agents that were in the line of sight last
    ## time tick are now not there
    ## i.e goes through agents in agentsenclosed, checks to see if their x and
    ## y are still contained in line of sight, and if not it removes them from
    ## the agentsenclosed list and adds one to the counter
    def countAgentsLeft(self):
        for i in reversed(range(len(self.agentsenclosed))):
            if [self.agentsenclosed[i].x, self.agentsenclosed[i].y] not in self.lineofsight:
                #print("An agent has left the line of sight!")
                self.countsum = self.countsum + 1
                self.agentsenclosed.pop(i)
            
    ## stores counter in hourlycounts every hour
    def run(self, timeIn):
        self.updateAgentsEnclosed()
        self.countAgentsLeft()
        if timeIn%ticksToAnHour == 0:
            self.hourlycount.append(self.countsum)
            self.countsum = 0
            

        
#%%

## Environment class
## initially a map filled with R for road
## but using setMap in the main program we can adjust it to match that of a 
## map picture (R still represents road, E for spawn points, B for buildings
## and C for building 'walls', i.e potential camera spots - see IO class for
## details)

class Environment(object):
    
    # sets up a world with a given height and width
    # initially all points of the world are 'N', null
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.data =[['R' for i in range(self.width)] for j in range(self.height)]
        self.shopLocations = []

    
    def setMap(self, mapIn):
        self.data = mapIn
        self.height = len(mapIn)
        self.width = len(mapIn[0])
    
    
    ## returns locations of spawn points
    def getSpawns(self):

        indices = []
        for k in range(len(self.data)):
    
           for i, j in enumerate(self.data[k]):
               if j == 'E':
                   indices.append([k, i])
        #print(indices)
        return indices
     
    ## returns locations of potential camera spots
    def getCameraSpots(self):
        
        indices = []
        for k in range(len(self.data)):
    
           for i, j in enumerate(self.data[k]):
               if j == 'C':
                   indices.append([k, i])
        return indices
        
        
#%%
    
## set defaults
numberOfAgents = 100 # overwritten in the case that origin-destination matrix is used
numberOfCameras = 8

## sets up values to use so that the timescale can be adjusted
## ticksToAnHour sets base time (i.e 60 -> one time tick is one minute)
## numberOfIterations is then 'numberofhours' * ticksToAnHour 
ticksToAnHour = 60
numberOfIterations = 48*ticksToAnHour


## prepares IO for file reading/writing
io = IO()

## sets up the world, reading in the paint map file
world = Environment(10, 10)
mapIn = io.readMap()
world.setMap(mapIn)


## code to set up an array of agents
agents = []

## the origin-destination matrix is read in, and used to determine how many
## agents to build with each origin as their home spawn and which destination
## as their work spawn

matrix = io.readMatrix()
reshaped = list(matrix.flatten())    


length = len(matrix)
width = len(matrix[0])
spawns = world.getSpawns()

print('this is the random number before journeys')
print(random.random())

journeysarray = [shortestpath.shortestjourney([spawns1[0], spawns1[1]], [spawns2[0], spawns2[1]], world.data)\
 for spawns1 in spawns for spawns2 in spawns]

print('this is the random number after journeys')
print(random.random())

## written using a flexible input dataframe (used below with df = io.readMatrix)
def buildAgents(listIn, length, width):
    
    random.seed(73)
    #population = [int(round(item*numberOfAgents)) for item in listIn]
    population= listIn
        
    for i in range(length):
        for j in range(width):
            for k in range(population[(i*length + j)]):
                agents.append(Worker(world,agents))    
                agents[-1].adjustLocations(spawns[i], spawns[j], journeysarray[(i*(length)+j)], journeysarray[(j*(length)+i)])
    
   # for i in range(len(matrixIn)):
    #    for j in range(len(matrixIn[0])):
     #       for k in range(matrixIn[i][j]):
      #          agents.append(Worker(world, agents))
       #         agents[-1].adjustTimes(spawns[i], spawns[j])
                
    for i in range(len(agents)):
        print("Worker " + repr(i) + " works at " + repr(agents[i].exitspawn[0]) + " " + repr(agents[i].exitspawn[1]))
        print("Worker " + repr(i) + " lives at " + repr(agents[i].entrancespawn[0]) + " " + repr(agents[i].entrancespawn[1]))


def genericAgents():
    
    for i in range(numberOfAgents):
        agents.append(Worker(world, agents))        


## code to set up an array of cameras
cameras = []

mapcameralocations = [[41,41], [8,43], [4,17], [2,16], [29,9], [31,9], [31,20], [31,25]]
    
    
def buildCameras():
    for i in range(numberOfCameras):
        print('building a camera')
        cameras.append(Camera(agents, world))
        cameras[i].setLocation(mapcameralocations[i])
## code to loop through iterations and agents    
## each agent runs, and then each camera updates its counts       

def runAgents():

    for i in range(numberOfIterations):
        clock = i%(24*ticksToAnHour)
      #  random.shuffle(agents)
        
        for j in range(len(agents)):
            agents[j].run(clock)
            #if clock%ticksToAnHour == 0:    
                #print("At time " + repr(clock) + agents[j].type + " " + repr(j) + " is at " + repr(agents[j].y) + " " + repr(agents[j].x) + " and is " + agents[j].state)
            
        for k in range(numberOfCameras):
            cameras[k].run(clock)
            #print(cameras[k].countsum)
#        if stoppingCriteriaMet() == True:
          #  break


## function to build program in its most basic

def runProgram(listIn, lengthIn, widthIn):
    
    random.seed(100)    
    print('after seed')
    print(random.random())
    t0 = time.time()

    print('after time')
    print(random.random())    
    buildAgents(listIn, lengthIn, widthIn)
    print('after building agents')
    print(random.random())
    buildCameras()
    print('after building cameras')
    print(random.random())
    runAgents()
    print('after running agents')
    print(random.random())
    counts = saveCameraCounts()
    print('after saving cameras')
    print(random.random())
    t1 = time.time()
    total = t1 - t0
    print(total)

    #for agent in agents:
     #   print('journey to work')
      #  print(agent.journeytowork)
       # print('journey home')
        #print(agent.journeyhome)

    global agents
    agents = []
    
    global cameras
    print('HERE ARE THE LOCATIONS')

    cameras = []   
        
    return counts
    
    
## prints the camera counts
def printCameraCounts():
    data = []
    for camera in cameras:
        print(camera.hourlycount)
        data.append(camera.hourlycount)
    
## as printCameraCounts, but also saves them using the io
def saveCameraCounts():        
    data = []
    columnheadings = []
    for camera in cameras:
        print(camera.hourlycount)
        data.append(camera.hourlycount)
        columnheadings.append(str(camera.lineofsight))
    io.writeCounts(data, columnheadings)
    print('done')
    return data
    
    


#%%

#day/night
#'home'

#%%
## genetic algorithm section, work in progress! separate file?
#minimum = 0
#maximum = 4
#dfrand = pd.DataFrame(np.random.randint(minimum, maximum, size = (10,10)))


