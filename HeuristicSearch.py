# INFORMATION
# ---------------------------------------------
# Practica 2 Heuristica: CSP y Busquedas
# A* Implementation: this is a programm which emulates the A* search algorithm to find a solution for the observation-satelites problem
# Daniel Cano Robledo
# Raul Gimenez de Dios

# IMPORTS
# ---------------------------------------------
# Argument treatment import
import sys
# Time measumeremtn import
import time
# Object copying import
import copy
# Mathematical operations import
import math

# PROBLEM MODELING
# ---------------------------------------------
# Satelite class:
# 
# Stores information about a satelite element, checks if it can perform operators on a given state and gives the possibility to both print it and compare
# itself to another satelite
class satelite:
    # Constructor, creates a new satelite
    #
    # @param id: Identificator (possible values = {1, 2})
    # @param viewZone: Array indicating the actual viewZone of the satelite
    # @param hour: Hour that the satelite is currently at
    # @param battery: Current battery of the satelite
    # @param maxBattery: Maximum battery of the satelite
    # @param chargingUnit: Number of units that a satelite charges when performing the charge operator
    # @param costs: Dictionary containing all of the costs (observe, transmit and rotate)
    # #return a new instantiation of the class satelite 
    def __init__(self, id, viewZone, hour, battery, maxBattery, chargingUnit, costs):
        self.id = id                         
        self.viewZone = viewZone             
        self.hour = hour                     
        self.battery = battery               
        self.maxBattery = maxBattery         
        self.chargingUnit = chargingUnit     
        self.costs = costs                   
    
    # Checks if the observe operator is available for this satelite and a given observation
    #
    # @param observation: observation to check the operator with
    # @return True if the operator can be performed and False if it can not
    def canObserve(self, observation):
        inSunTimeZone = self.hour >= 0 and self.hour <= 11
        sameHour = self.hour == observation.hour
        withinViewZone = (observation.viewZone == self.viewZone[0]) or (observation.viewZone == self.viewZone[1])
        batteryEnough = self.battery >= self.costs.get("observeCost")
        observationNotObserved = observation.state == "waiting"
        return inSunTimeZone and sameHour and withinViewZone and batteryEnough and observationNotObserved
    
    # Checks if the transmit operator is available for this satelite and a given observation
    #
    # @param observation: observation to check the operator with
    # @return True if the operator can be performed and False if it can not
    def canTransmit(self, observation):
        inSunTimeZone = self.hour >= 0 and self.hour <= 11
        batteryEnough = self.battery >= self.costs.get("transmitCost")
        observationNotTransmited = observation.state == "observed"
        observerCoincidence = self.id == observation.observerId
        return inSunTimeZone and batteryEnough and observationNotTransmited and observerCoincidence
        
    # Checks if the charge operator is available for this satelite
    #
    # @return True if the operator can be performed and False if it can not
    def canCharge(self):
        inSunTimeZone = self.hour >= 0 and self.hour <= 11
        notMaxBattery = not(self.battery == self.maxBattery)
        return inSunTimeZone and notMaxBattery
    
    # Checks if the rotateUp operator is available for this satelite
    #
    # @return True if the operator can be performed and False if it can not    
    def canRotateUp(self):
        notInUpperBound = not(self.viewZone == [0, 1])
        if self.id == 2:
            notInUpperBound = not(self.viewZone == [1, 2])
        
        batteryEnough = self.battery >= self.costs.get("rotateCost")
        return notInUpperBound and batteryEnough
    
    # Checks if the rotateDown operator is available for this satelite
    #
    # @return True if the operator can be performed and False if it can not       
    def canRotateDown(self):
        notInBottomBound = not(self.viewZone == [1, 2])
        if self.id == 2:
            notInBottomBound = not(self.viewZone == [2, 3])
        
        batteryEnough = self.battery >= self.costs.get("rotateCost")
        return notInBottomBound and batteryEnough
    
    # This function prints all of the information of the satelite
    #
    # @return void   
    def print(self):
        print("Sat" + str(self.id) + " =  {id: " + str(self.id) + ", viewZone: (" + str(self.viewZone[0]) + ", " + str(self.viewZone[1]) + "), hour: " + str(self.hour) +
              ", battery: " + str(self.battery) + ", maxBattery: " + str(self.maxBattery) + ", chargingUnit: " + str(self.chargingUnit) +
              ", observeCost: " + str(self.costs.get("observeCost")) + ", transmitCost: " + str(self.costs.get("transmitCost")) + ", rotateCost: " + str(self.costs.get("rotateCost")) +
              "}", end="\n")
    
    # This function compares this satelite with another one
    #
    # @return True if both satelites are equal and False if they are not 
    def equals(self, sat):
        sameViewZone = self.viewZone[0] == sat.viewZone[0] and self.viewZone[1] == sat.viewZone[1]
        sameCosts = self.costs.get("observeCost") == sat.costs.get("observeCost") and self.costs.get("transmitCost") == sat.costs.get("transmitCost") and self.costs.get("rotateCost") == sat.costs.get("rotateCost")
        return self.id == sat.id and sameViewZone and self.hour == sat.hour and self.battery == sat.battery and self.maxBattery == sat.maxBattery and self.chargingUnit == sat.chargingUnit and sameCosts     

# Observation class:
# 
# Stores information about the observation gives the possibility to both print it and compare itself to another observation
class observation:
    # Constructor, creates a new observation
    #
    # @param id: Identificator
    # @param state: State of the observation (possible values={waiting, observed and transmited})
    # @param viewZone: Viewzone that the observation is at (Y-Coordinate)
    # @param hour: Hour that the observation is at (X-Coordinate)
    # @param observerId: Id of the satelite which observed the observation
    # @return a new instantiation of the class observation
    def __init__(self, id, state, viewZone, hour, observerId = 1):
        self.id = id                    
        self.state = state               
        self.viewZone = viewZone         
        self.hour = hour                 
        self.observerId = observerId     
    
    # This function prints all of the information of the observation
    #
    # @return void   
    def print(self):
        print("Observation" + str(self.id) + " =  {id: " + str(self.id) + ", state: " + self.state + ", viewZone: "+ str(self.viewZone) + ", hour: " + str(self.hour) + "}", end="\n")
    
    # This function compares this observation with another one
    #
    # @return True if both observations are equal and False if they are not   
    def equals(self, observation):
        return self.id == observation.id and self.state == observation.state and self.viewZone == observation.viewZone and self.hour == observation.hour and self.observerId == observation.observerId       

# Move class:
# 
# Stores information about a move and the elements that are affected by it
class move:
    # Constructor, creates a new move
    #
    # @param name: name of the move (possible values = {start, idle, observe, transmit, charge, rotateUp and rotateDown})
    # @param cost: battery cost of the move
    # @param sat: the satelite object which is performing the move
    # @param observation: the observation involucred in the move, it could be None
    # @return a new instantiation of the class move
    def __init__(self, name, cost, sat, observation = None):
        self.name = name
        self.cost = cost
        self.sat = sat
        self.observation = observation
    
    # This function compares this move with another one
    #
    # @return True if both observations are equal and False if they are not     
    def print(self):
        if(self.observation == None):
            print("SAT " + str(self.sat.id) + " - Observation NONE - " + self.name + " - " + str(self.cost) +" batteryCost")
        else:
            print("SAT " + str(self.sat.id) + " - Observation " + str(self.observation.id) + " - " + self.name + " - "  + str(self.cost) +" batteryCost")
        
# State class:
# 
# Represent a state within the search problem
class state:
    # Constructor, creates a new state
    #
    # @param sat1: sat object representing the first satelite of the problem
    # @param sat2: sat object representing the second satelite of the problem
    # @param observations: array containing all of the problem's observations
    # @param shouldGoSat1: boolean variable controlling whether or not the next action should affect the first satelite
    # @return a new instantiation of the class state
    def __init__(self, sat1, sat2, observations, shouldGoSat1 = True):
        self.sat1 = sat1
        self.sat2 = sat2
        self.observations = observations
        self.shouldGoSat1 = shouldGoSat1
        
    # This method gets all of the possible actions from one state to another by check all of the operands' conditions on both the satelites and observations
    #
    # @return moves: an array containing all of the possible moves
    def getLegalMoves(self):
        moves = []
        
         # Idle for both satelites is always possible
        if self.shouldGoSat1:
            moves.append(move("idle", 0, self.sat1))
        if not(self.shouldGoSat1):
            moves.append(move("idle", 0, self.sat2))
        
        # Now, let's check if we can observe and/or transmit any observation
        for i in range(0, len(self.observations)):
            if self.sat1.canObserve(self.observations[i]) and self.shouldGoSat1:
                moves.append(move("observe", self.sat1.costs.get("observeCost"), self.sat1, self.observations[i]))
            if self.sat2.canObserve(self.observations[i]) and not(self.shouldGoSat1):
                moves.append(move("observe", self.sat2.costs.get("observeCost"), self.sat2, self.observations[i]))
                
            if self.sat1.canTransmit(self.observations[i]) and self.shouldGoSat1:
                moves.append(move("transmit", self.sat1.costs.get("transmitCost"), self.sat1, self.observations[i]))
            if self.sat2.canTransmit(self.observations[i]) and not(self.shouldGoSat1):
                moves.append(move("transmit", self.sat2.costs.get("transmitCost"), self.sat2, self.observations[i]))
                 
        # Let's see if the satelites can charge
        if self.sat1.canCharge() and self.shouldGoSat1:
            moves.append(move("charge", 0, self.sat1))
        if self.sat2.canCharge() and not(self.shouldGoSat1):
            moves.append(move("charge", 0, self.sat2))
            
        # Finally, let's check if the satelites can rotate
        if self.sat1.canRotateUp() and self.shouldGoSat1:
            moves.append(move("rotateUp", self.sat1.costs.get("rotateCost"), self.sat1))
        if self.sat1.canRotateDown() and self.shouldGoSat1:
            moves.append(move("rotateDown", self.sat1.costs.get("rotateCost"), self.sat1))
            
        if self.sat2.canRotateUp() and not(self.shouldGoSat1):
            moves.append(move("rotateUp", self.sat2.costs.get("rotateCost"), self.sat2))
        if self.sat2.canRotateDown() and not(self.shouldGoSat1):
            moves.append(move("rotateDown", self.sat2.costs.get("rotateCost"), self.sat2))
        
        return moves
    
    # This method gets the state result of performing a move, this move can be any of the operands of the modeling problem
    #
    # @param move: move to perform
    # @return state resulted of performing the move into the current state with a pointer to it
    def resultSuccessor(self, move):
        if move.name == "idle":
            return self.idle(move.sat)
        
        elif move.name == "observe":
            return self.observe(move.sat, move.observation)
        
        elif move.name == "transmit":
            return self.transmit(move.sat, move.observation)
        
        elif move.name == "charge":
            return self.charge(move.sat)
        
        elif move.name == "rotateUp":
            return self.rotate(move.sat, "up")  
          
        elif move.name == "rotateDown":
            return self.rotate(move.sat, "down")  
        
        else:
            print("Error: la acción " + move + " no esta permitida", end = "\n")
    
    # First operand: A satelite does nothing and just waits
    #
    # Conditions:
    #   - There are no conditions in this operand
    # Effects:
    #   - Increase satelite's hour
    #   
    # @param sat: the satelite which is performing the move
    # @return state resulted of performing the move into the current state with a pointer to it
    def idle(self, sat):
        newSat = copy.deepcopy(sat)
        
        # Increase satelite's hours
        newSat.hour = (newSat.hour + 1) % 24
        
        # Returns succesor result state
        if newSat.id == 1:
            return state(newSat, self.sat2, self.observations, False)
        return state(self.sat1, newSat, self.observations)
    
    # Second operand: A satelite observes an observation
    #
    # Conditions:
    #   - The satelite must be in sun time zone
    #   - Both the observation and the satelite must be in the same hour
    #   - The observation must be within the satelite's view zone
    #   - The satelite must have enought battery to observe
    #   - The observation must not have been observed
    # Effects:
    #   - Increase satelite's hour
    #   - Reduce satelite's battery
    #   - The observation's state changes to observed
    #   - The observation's observerId changes to the satelite's id
    #
    # @param sat: the satelite which is performing the move
    # @param observation: the observations which is being observed 
    # @return state resulted of performing the move into the current state with a pointer to it
    def observe(self, sat, observation):
        newSat = copy.deepcopy(sat)
        newObservations = copy.deepcopy(self.observations)
        
        # Increase satelite's hours
        newSat.hour = (newSat.hour + 1) % 24
        
        # Decrease satelite's battery
        newSat.battery -= sat.costs.get("observeCost")
        
        # Change observation's state
        newObservations[observation.id - 1].state = "observed"
        
        # Change observation's observerId
        newObservations[observation.id - 1].observerId = newSat.id
        
        # Returns succesor result state
        if newSat.id == 1:
            return state(newSat, self.sat2, newObservations, False)
        return state(self.sat1, newSat, newObservations)
        
    # Third operand: A satelite transmit an observation
    #
    # Conditions:
    #   - The satelite must be in sun time zone
    #   - The satelite must have enought battery to transmit
    #   - The observation must not have been transmited
    #   - The satelite which observed the observation must be the same as the one which will transmit it   
    # Effects:
    #   - Increase satelite's hour
    #   - Reduce satelite's battery
    #   - The observation's state changes to transmited
    #   
    # @param sat: the satelite which is performing the move
    # @param observation: the observations which is being transmited 
    # @return state resulted of performing the move into the current state with a pointer to it
    def transmit(self, sat, observation):
        newSat = copy.deepcopy(sat)
        newObservations = copy.deepcopy(self.observations)
        
        # Increase satelite's hours
        newSat.hour = (newSat.hour + 1) % 24
        
        # Decrease satelite's battery
        newSat.battery -= sat.costs.get("transmitCost")
        
        # Change observation's state
        newObservations[observation.id - 1].state = "transmited"
        
        # Returns succesor result state
        if newSat.id == 1:
            return state(newSat, self.sat2, newObservations, False)
        return state(self.sat1, newSat, newObservations)
    
    # Fourth operand: A satelite charges energy
    #
    # Conditions:
    #   - The satelite must be in sun time zone
    #   - The satelite musn't have maximum battery   
    # Effects:
    #   - Increase satelite's hour
    #   - Increase satelite's battery
    #   
    # @param sat: the satelite which is performing the move
    # @return state resulted of performing the move into the current state with a pointer to it
    def charge(self, sat):
        newSat = copy.deepcopy(sat)
        
        # Increase satelite's hours
        newSat.hour = (newSat.hour + 1) % 24
        
        # Increase satelite's battery
        newSat.battery += sat.chargingUnit
        if newSat.battery > newSat.maxBattery:
            newSat.battery = newSat.maxBattery
        
        # Returns succesor result state
        if newSat.id == 1:
            return state(newSat, self.sat2, self.observations, False)
        return state(self.sat1, newSat, self.observations)
    
    # Fifth operand: A satelite rotates towards a direction
    #
    # Conditions:
    #   - The satelite must have enought battery to transmit
    #   - The satelite musn't be in its bound   
    # Effects:
    #   - Increase satelite's hour
    #   - Reduce satelite's battery
    #   - The satelite's viewZone changes towards the direction
    #   
    # @param sat: the satelite which is performing the move
    # @param dir: direction that the satelite will rotate towards
    # @return state resulted of performing the move into the current state with a pointer to it
    def rotate(self, sat, dir):
        newSat = copy.deepcopy(sat)
        
        # Increase satelite's hours
        newSat.hour = (newSat.hour + 1) % 24
        
        # Decrease satelite's battery
        newSat.battery -= sat.costs.get("rotateCost")
        
        # Rotate satelite's viewZone
        if newSat.id == 1:
            if dir == "up":
                newSat.viewZone = [0, 1]
            elif dir == "down":
                newSat.viewZone = [1, 2]
                
            return state(newSat, self.sat2, self.observations, False)
            
        else:
            if dir == "up":
                newSat.viewZone = [1, 2]
            elif dir == "down":
                newSat.viewZone = [2, 3]
                
            return state(self.sat1, newSat, self.observations)
    
    # This function prints all of the information of the state
    #
    # @return void          
    def print(self):
        print("SAT1's INFORMATION:", end="\n")
        self.sat1.print()
        print("")
        print("SAT2's INFORMATION:", end="\n")
        self.sat2.print()
        print("")
        print("OBSERVATIONS' INFORMATION")
        for observation in self.observations:
            observation.print()
    
    # This function compares this state with another one
    #
    # @return True if both states are equal and False if they are not
    def equals(self, state):
        sameObservations = True
        i = 0
        while i < len(self.observations) and i < len(state.observations):
            sameObservations = self.observations[i].equals(state.observations[i])
            i += 1
        return self.sat1.equals(state.sat1) and self.sat2.equals(state.sat2) and sameObservations and self.shouldGoSat1 == state.shouldGoSat1

# Node class:
# 
# Represents a node in the search graph, notice the difference between the node class and the state class: a state is a representation of the problem in a fixed time and
# a node is a representation of both the problem, the move that leaded to it and the cost associated with that move
class node:
    # Constructor, creates a new node
    #
    # @param state: state of the search problem in a fixed time
    # @param move: move which leaded to the state
    # @param g: cost of the move (battery + hours)
    # @param parent: pointer referencing the previous node
    # @return a new instantiation of the node class
    def __init__(self, state, move, g, parent = None):
        self.state = state
        self.move = move
        self.g = g
        self.parent = parent
    
# Problem class:
# 
# Represents the whole search problem to solve
class searchProblem:
    # Constructor, creates a new search problem
    # 
    # @return a new instantiation of the search problem class
    def __init__(self):
        self.initialState = processProblemInputFile(self)
    
    # This function returns the initial state of the problem
    # 
    # @return the initial state of this object    
    def getInitialState(self):
        return self.initialState
    
    # This function checks if a state is a goal state
    # 
    # @param state: state to check
    # @return True if state is a goal state and False if it is not
    def isGoalState(self, state):
        for observation in state.observations:
            if observation.state != "transmited":
                return False
        return True
    
    # This method returns a list of all of the succesors , which are Nodes(state, move, cost, parent)
    #
    # @param currentNode: node to get the succesors of
    # @return a succersors array containing all of the nodes resulting from performing all of the possible moves in the currentnode
    def getSuccessors(self, currentNode):
        successors = []
        # Get all possible moves
        legalMoves = currentNode.state.getLegalMoves()
        for move in legalMoves:
            # Increase 0.5 hours and the corresponding battery cost
            newCost =  0.5 + move.cost
            if currentNode.parent != None:
                # Accumulate the previous cost
                newCost += currentNode.parent.g
            
            newNode = node(currentNode.state.resultSuccessor(move), move, newCost, currentNode)
            
            successors.append(newNode)   
        return successors
        


# INPUT PROCESSING
# ---------------------------------------------
# This method takes a .prob file's path indicating all of the observations coordinates and all of the satelites' parameters and creates a searching problem representing all of
# the information
#
# @param searchProblem: searchProblem in which to store the input file information
# @return the initial state of the searchProblem
def processProblemInputFile(searchProblem):
    file = open(sys.argv[1])
    i = 0
    
    # Get all of the file's lines
    for line in file:
        # Gets all values
        values = line.split(";")
        # Parse the first value
        values[0] = values[0].split(":")[1].strip()
        if i == 0:
            # Process the observations
            initialObservations = processObservationsValues(values)
        elif i == 1:
            # Process the first satelite
            initialSat1 = processSatValues(values)
        else:
            # Process the second satelite
            initialSat2 = processSatValues(values, 2)
        i += 1
    
    # Creates the initial node    
    initialState = state(initialSat1, initialSat2, initialObservations)
    initialMove = move("start", 0, satelite(0, 0, 0, 0, 0, 0, 0))
    initialCost = 0
    
    return node(initialState, initialMove, initialCost)

# This method processes all of the observations' information and creates the corresponding array of observations
#
# @param observationsValues: information of the observations (viewZone and hour)
# @return array containing all of the observations
def processObservationsValues(observationsValues):
    observations = []
    i = 1
    for value in observationsValues:
        observations.append(observation(i, "waiting", int(value[1]), int(value[3])))
        i+=1
    
    return observations

# This method processes all of a satelite's information and creates the corresponding object
#
# @param satValues: information of the satelite
# @param satId: id of the satelite
# @return a new satelite class instantiation
def processSatValues(satValues, satId = 1):
    satObserveCost = int(satValues[0])
    satTransmitCost = int(satValues[1])
    satRotateCost = int(satValues[2])
    satChargingUnit = int(satValues[3])
    satMaxBattery = int(satValues[4].split("\n")[0])
    
    viewZone = [0, 1]
    if satId == 2:
        viewZone = [2, 3]
        
    sat = satelite(satId, viewZone, 0, 1, satMaxBattery, satChargingUnit, {"observeCost": satObserveCost, "transmitCost": satTransmitCost, "rotateCost": satRotateCost})

    
    return sat
        


# OUTPUT PROCESSING
# ---------------------------------------------
# This function generates a .output file representing the steps taken to get to a given solution
#
# @param solution: solution of a searchProblem
# @return void
def generateSolutionFile(solution):
    file = open("./problema.prob.output", "w+")
    
    # We get the path in reverse order
    inversedPath = stateOrderedList()
    current = solution
    while current.parent != None:
        inversedPath.insert(current)
        current = current.parent
    
    i = inversedPath.size() - 1
    counter = 1
    while i >= 0:
        if inversedPath.getElementByIndex(i).move.sat.id == 1:
            file.write(str(counter) + ". SAT1: " + inversedPath.getElementByIndex(i).move.name + ", ")
            counter += 1
        else:
            file.write("SAT2: " + inversedPath.getElementByIndex(i).move.name + "\n")
        i -= 1

# This function generates a .statistics file representing information about a searchProblem solving execution
#
# @param executionTime: time of the searchProblem solving execution
# @param solution: solution of a searchProblem
# @param expandedNodes: number of nodes expanded to get the solution
# @return void
def generateStatisticsFile(executionTime, solution, expandedNodes):
    file = open("./problema.prob.statistics", "w+")
    
    file.write("Tiempo total: " + str(round(executionTime*1000, 3)) + " ms\n")
    
    file.write("Coste total: " + str(math.ceil(solution.g)) + "\n")
    
    current = solution
    i = 0
    while current.parent != None:
        i += 1
        current = current.parent
        
    file.write("Longitud del plan: " + str(math.ceil(i/2)) + " pasos\n")
    file.write("Nodos expandidos: " + str(expandedNodes) + " nodos")



# FUNCTIONS DECLARATION
# ---------------------------------------------
# This functions computes the distance in hours between a satelite and the closest observation
#
# @param sat: satelite to compute the distance with
# @param observations: observations to compute the distance with
# @return an integer representing the number of hours that the satelite has to go through in order to reach the closest waiting observation    
def getTimeDistance(sat, observations):
    totalDistance = 0
    for observation in observations:
        if observation.state == "waiting":
            if observation.hour > sat.hour:
                tempTotalDistance = observation.hour - sat.hour
            else:
                tempTotalDistance = (24 - sat.hour) + observation.hour
            if totalDistance < tempTotalDistance:
                totalDistance = tempTotalDistance
    return totalDistance

# This functions computes the distance in both hours and rotations between a satelite and an observation
#
# @param sat: satelite to compute the distance with
# @param observations: observations to compute the distance with
# @return an integer representing the number of hours and rotations that the satelite has to go through in order to reach the closest waiting observation    
def getManhattanDistance(sat, observations):
    totalDistance = 0
    for observation in observations:
        if observation.state == "waiting":
            verticalDistance =  min((abs(sat.viewZone[0]-observation.viewZone)),(abs(sat.viewZone[1]-observation.viewZone)))
            if observation.hour > sat.hour:
                horizontalDistance = observation.hour - sat.hour
            else:
                horizontalDistance = (24 - sat.hour) + observation.hour
            tempTotalDistance = horizontalDistance + verticalDistance
            if totalDistance < tempTotalDistance:
                totalDistance = tempTotalDistance
    return totalDistance



# HEURISTICS
# ---------------------------------------------
# Null heuristic: Void function to set as default value
#
# @param state: state to compute the heuristic in
# @return integer representing the estimated number of steps between the state and the goal state
def nullHeuristic(state):
    return 0

# First heuristic: Number of steps in hours to reach the closest observation, plus two additional steps of both observation and transmision or number of transmisions
# left to perform
#
# @param state: state to compute the heuristic in
# @return integer representing the estimated number of steps between the state and the goal state
def timeDistance(state):
    # First, compute the manhattan distance of the first satelite to the closest observation
    totalDistanceSat1 = getTimeDistance(state.sat1, state.observations)
    # Second, compute the manhattan distance of the second satelite to the closest observation
    totalDistanceSat2 = getTimeDistance(state.sat2, state.observations)
    
    # Now, if both distances are 0, then there are not waiting observations so we just compute the number of transmisions to make
    if totalDistanceSat1 == 0 and totalDistanceSat2 == 0:
        observationsToTransmit = 0
        for observation in state.observations:
            if observation.state == "observed":
                observationsToTransmit += 1
        return observationsToTransmit
    
    # Otherwhise, we just compute the minimum amount of steps to transmit the closest waiting observation
    return min(totalDistanceSat1, totalDistanceSat2) + 2

# Second heuristic: Number of steps both in hours and in rotations to reach the closest observation, plus two additional steps of both observation and transmision
#
# @param state: state to compute the heuristic in
# @return integer representing the estimated number of steps between the state and the goal state
def manhattanAdaptation(state):
    # First, compute the manhattan distance of the first satelite to the closest observation
    totalDistanceSat1 = getManhattanDistance(state.sat1, state.observations)
    # Second, compute the manhattan distance of the second satelite to the closest observation
    totalDistanceSat2 = getManhattanDistance(state.sat2, state.observations)
    
    # Now, if both distances are 0, then there are not waiting observations so we just compute the number of transmisions to make
    if totalDistanceSat1 == 0 and totalDistanceSat2 == 0:
        observationsToTransmit = 0
        for observation in state.observations:
            if observation.state == "observed":
                observationsToTransmit += 1
        return observationsToTransmit
    
    # Otherwhise, we just compute the minimum amount of steps to transmit the closest waiting observation
    return min(totalDistanceSat1, totalDistanceSat2) + 2

    
    
    
# STATE STORAGE & SORTING
# ---------------------------------------------
# stateOrderedList class:
#
# Represents a custom data structure in which all of the elements are stored and in which the pop method gets the most favorable elements
class stateOrderedList:
    # Constructor, creates a new stateOrderedList
    #
    # @param heuristic: heuristic function with which to compare one elements to another
    # @return a new instantiation of the stateOrderedList
    def __init__(self, heuristic = nullHeuristic): 
        self.list = []
        self.heuristic = heuristic 
  
    # This method checks if the structure is empty
    #
    # @return True is the structure is empty and False if it is not
    def isEmpty(self): 
        return len(self.list) == 0
    
    # This method gets the size of the structure
    #
    # @return an integer representing the lenght of the structure's list
    def size(self):
        return len(self.list)
  
    # This method inserts a new element into the structure
    #
    # @param element: element to insert
    # @return void
    def insert(self, element): 
        self.list.append(element) 
  
    # This method gets and deletes the most favorable element, the one with the minimum f() = g() + h()
    #
    # @param targetSatId: id of the satelite that the node should reference to
    # @return the most favorable element
    def pop(self, targetSatId):  
        min = 0
        
        for i in range(len(self.list)):
            if(self.list[i].move.sat.id == targetSatId):
                min = i
        
        for i in range(len(self.list)):
            if (self.list[i].g + self.heuristic(self.list[i].state) < self.list[min].g + self.heuristic(self.list[min].state)) and (self.list[i].move.sat.id == targetSatId): 
                min = i 
                
        item = copy.deepcopy(self.list[min]) 
        del self.list[min] 
        return item
    
    # This method gets an element based on its state
    #
    # @param state: state to get the element of
    # @return the element which has the same state as the argument's
    def get(self, state):  
        for element in self.list:
            if element.state.equals(state):
                return element
        return False 
    
    # This method gets an element based on its index
    #
    # @param index: index of the element to get
    # @return the element which has the same index as the argument's
    def getElementByIndex(self, index):
        return copy.deepcopy(self.list[index])
    
    # This method checks if an element is present in the structure based on its state
    #
    # @param state: state of the element to check
    # @return True if the element is contained in the structure and false if it is not
    def contains(self, state):
        for element in self.list:
            if element.state.equals(state):
                return True
        return False
    
    # This method deletes an element based on its state
    # @param state: state of the element to look for
    # @return void
    def deletePresentState(self, state):
        for i in range(len(self.list)-1): 
            if self.list[i].state.equals(state):
                del self.list[i]



# PROBLEM SOLVING
# ---------------------------------------------
# This is a general implementation of a graph search problem resolution
#
# @param searchProblem: problem to solve
# @param heuristic: heuristic function to use as a solving guide
# @return False if there is no solution and both the solution node and number of nodes expanded if there is
def aStarSearch(searchProblem, heuristic = nullHeuristic):
    targetSatId = 0
    
    # We first create both open and close lists
    open = stateOrderedList(heuristic)
    close = stateOrderedList(heuristic)
    
    # Now, insert the initial state in open
    open.insert(searchProblem.initialState)
    
    expandedNodes = 0
    
    # We keep the algorithm going until there are no more nodes to expand
    while not(open.isEmpty()):
        # Get the most favorable node, the one with min f() = g() + h()
        current = open.pop(targetSatId)
        
        # If it is a goal state, then HALT
        if searchProblem.isGoalState(current.state):
            return (current, expandedNodes)
        
        else:
            # Expand the node, get all of the succesors
            successors = searchProblem.getSuccessors(current)
            expandedNodes += 1
            # Check this node as expanded
            close.insert(current)
            
            if targetSatId == 0:
                targetSatId = 1
            else:
                targetSatId = 1 if targetSatId == 2 else 2
            
            # For every node generated in the expansion
            for successor in successors:
                # If it is the first time we get this node, we insert it in the open list
                if not(open.contains(successor.state)) and not(close.contains(successor.state)):
                    open.insert(successor)
                
                # If we have already get this node but this time it is more favorable, we substitude it
                elif open.contains(successor.state):
                    if successor.g + heuristic(successor.state) > open.get(successor.state).g + heuristic(successor.state):
                        open.deletePresentState(successor.state)
                        open.insert(successor)
    return False
        


# MAIN EXECUTION
# ---------------------------------------------
# Main execution to solve the searching problem
startTime = time.time()

searchProblem = searchProblem()

if sys.argv[2] == "timeDistance":
    solution = aStarSearch(searchProblem, timeDistance)
    
elif sys.argv[2] == "manhattanAdaptation":
    solution = aStarSearch(searchProblem, manhattanAdaptation)
    
else:
    solution = None
    print("Error: la heuristica introducida no es ninguna opcion existente")
    print("Las opciones disponibles son timeDistance y manhattanAdaptation")

endTime = time.time()



# OUTPUT GENERATION
# ---------------------------------------------
if solution is not None:
    if not solution:
        print("Solution not found")
    else:
        print("Solution found!")
        generateSolutionFile(solution[0])
        generateStatisticsFile(endTime - startTime, solution[0], solution[1])