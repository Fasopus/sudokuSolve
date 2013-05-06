#Global variable for tracking how many nodes we visit
global Nodes
Nodes = 0

#Crossproduct for building board
def CrossProduct(X,Y):
    return [x + y for x in X for y in Y]
    
#Increment Nodes    
def Add_Node():
    global Nodes
    Nodes = Nodes + 1

#Zero out node counter
def Zero_Node():
    global Nodes
    Nodes = 0

##############################################################################
#Original inspiration for setting up the Sudoku problem using dictionaries and 
#using crossproducts to quickly create the lists for the 27 constraints that 
#exist comes from the code/essay publically available at: 
#norvig.com/sudoku.html
#The most relevant code is in the first code box listed in the essay which is
#the major basis for lines 29-45 of this file
##############################################################################

#Columns will be numbered and rows alphabetized
columns = '123456789'
rows = 'ABCDEFGHI'
    
#Cross Product of Rows and Columns gives us all of our cells
cells = CrossProduct(rows,columns)
    
#Series of cross products to build a list of every constraint,
#first the cube then the row/column constraints
ConditionList = ([CrossProduct(SquareRow,SquareColumn) for SquareRow in ('ABC','DEF','GHI')
                  for SquareColumn in ('123','456','789')])
ConditionList = ConditionList + ([CrossProduct(row,columns) for row in rows])
ConditionList = ConditionList + ([CrossProduct(rows,column) for column in columns])

#Pull all the conditions for a given cell out of the big list
CellToConditions = dict((cell,[cond for cond in ConditionList if cell in cond]) for cell in cells)
#Filter conditions down, removes the cell itself and any redundancy
ConditionalPeers = dict((cell,set(sum(CellToConditions[cell],[]))-set([cell])) for cell in cells)

#End of staging code/begining of actual functions used in solving the problem

#This function assigns a value in the solutions dictionary
#then removes it from availablility for that cells peers
#This is called repeatively during input to build the starting grid
#As well as anytime we wish to set a new state
def SetSolutionValue(cell,value,solutions,AvailableValues):
    solutions[cell] = value
    for peer in ConditionalPeers[cell]:
        AvailableValues[peer] = AvailableValues[peer].replace(value,'')
    

    
    
#Resets the selected cell so its blank
def RemoveSolutionValue(cell,solutions):
    #Only try to remove non empty values
    assert(solutions[cell]!='0')
    solutions[cell] = '0'


#Takes the string representation of our starting board and converts it to dictionary
def StringRepToDictRep(String):
    Characters = [character for character in String]
    DictRep = dict(zip(cells,Characters))
    #Dictionary is now build but the available values are not properly set!
    return DictRep

def SetupAvailableValues(Solution):
    #Every cell could be any value at this point,
    #we will pull away from this after we take our input
    Available = dict((cell,columns) for cell in cells)
    for cell in cells:
        #Only on non blank cells
        if (Solution[cell] != '0'):
            #Formally add it to the grid
            SetSolutionValue(cell,Solution[cell],Solution,Available)
            #These are our originaly specified cells and cannot change
            Available[cell] = Solution[cell]
    return Available

#Return a tuple of values that still need to be assigned
def FindUnassignedCells(Solutions):
    Unassigned = ([cell for cell in cells if Solutions[cell] == '0'])
    return Unassigned

#Check if we are complete
def CheckSolution(Solutions):
    #If every cell has been assigned a value then we are complete
    #Constraints are enforced by SetSolutionValue, the only
    #Values we try to add are valid ones
    if all(Solutions[cell] != '0' for cell in cells):
        return True
    return False

#Recursive function for backtrace solver
def Recursive_Backtrace(Solutions,AvailableValues):
   #Check if we have a solution
    if CheckSolution(Solutions) == True:
        return Solutions
    Unassigned = FindUnassignedCells(Solutions)
    #No special method, just pick first unassigned cell
    Var = Unassigned[0]
    #We can explore this node so we will
    Add_Node()
    #Check our available values to see if we can keep going
    for Value in AvailableValues[Var]:
        #Don't need to check if the value is valid, we know that any values in
        #AvailableValues are clear to use because of how SetSolutionValue invalidates
        #Make a copy of Available values so we dont have to worry about restoring the current
        #one should this attempt fail
        NewAvailableValues = AvailableValues.copy()
        #Assign the value and make it unavailable for peers according to NewAvailableValues
        SetSolutionValue(Var,Value,Solutions,NewAvailableValues)
        #Recurse
        Result = Recursive_Backtrace(Solutions,NewAvailableValues)
        #If we get anything but false we have solved the problem!
        if Result != False:
            return Result
        #If we get here we've failed somewhere down the line
        #Since we made a duplicate of AvailableValues we don't have to restore it
        #only need to restore our solutions dictionary
        RemoveSolutionValue(Var,Solutions)
    #If we get here we've exhausted everything with no solutions so we return a failure
    return False
    
    

#Solve using backtrace solving   
def BacktraceSolve(Problem):
    #Setup our time tracking
    from datetime import datetime
    start = datetime.now()
    
    #Stage our problem and begin solving it
    Solutions = StringRepToDictRep(Problem)
    AvailableValues = SetupAvailableValues(Solutions)
    Result = Recursive_Backtrace(Solutions,AvailableValues)
    
    #Completed solving the code, calculate runtime and output data
    finish = datetime.now()
    runtime = finish - start
    if Result != False:
        print ("Backtrace Sudoku solved exploring " + str(Nodes) +
             " nodes in " + str(runtime.total_seconds()) + " seconds")
    else:
        print "FAILURE"
    return Result;



#Recursive function for Backtrace + Forward Check solver
def Recursive_BacktraceForwardcheck(Solutions,AvailableValues):
   #Check if we have a solution
    if CheckSolution(Solutions) == True:
        return Solutions
    #Forwardchecking
    if any(len(AvailableValues[cell]) == 0 for cell in cells):
        return False
    Unassigned = FindUnassignedCells(Solutions)
    #No special method, just pick first unassigned cell
    Var = Unassigned[0]
    #Explore the next node
    Add_Node()
    #Check all posible values to try and continue solving the problem
    for Value in AvailableValues[Var]:
        #Make a copy of Available values so we dont have to worry about restoring the
        #current one should this attempt fail
        NewAvailableValues = AvailableValues.copy()
        #Set the value in our solution and make it unavailable for peers in NewAvailableValues
        SetSolutionValue(Var,Value,Solutions,NewAvailableValues)
        #Recurse
        Result = Recursive_BacktraceForwardcheck(Solutions,NewAvailableValues)
        #If we get anything but False here we've solved the puzzle!
        if Result != False:
            return Result
        #If we get here we failed, restore the solutions dictionary,
        #dont need to worry about AvailableValues since we copied it
        RemoveSolutionValue(Var,Solutions)
    #If we get here we've exhausted everything with no solutions so we fail
    return False
    
    

#Solve using backtrace + forwardchecking    
def BacktraceForwardCheckingSolve(Problem):
    #Setup our time tracking
    from datetime import datetime
    start = datetime.now()
    
    #Stage problem and begin solver
    Solutions = StringRepToDictRep(Problem)
    AvailableValues = SetupAvailableValues(Solutions)
    Result = Recursive_BacktraceForwardcheck(Solutions,AvailableValues)
    
    #We've finished solving, output information
    finish = datetime.now()
    runtime = finish - start
    if Result != False:
        print ("Backtrace w Forwardchecking Sudoku solved exploring " + str(Nodes) +
               " nodes in " + str(runtime.total_seconds()) + " seconds")
    else:
        print "FAILURE"
    return Result

#Select the next variable we should use according to our heuristics
def HeuristicSelect(Unassigned,AvailableValues):
    #Guaranteed to be bigger than anything we should see
    MinLen = 10
    #Find the minimum number of availables we have 
    for cell in Unassigned:
        if len(AvailableValues[cell]) < MinLen:
            MinLen = len(AvailableValues[cell])
    
    #Find a list of all nodes that are the most constrained(miniumum number of choices)
    Most_Constrained_Variables = ([cell for cell in Unassigned
                                   if len(AvailableValues[cell]) == MinLen])
    
    #If more than one we tiebreak
    if len(Most_Constrained_Variables) > 1:
        #Find which cells our tied variables are still constraining on
        Constraining_Data = dict((cell,[peer for peer in ConditionalPeers[cell] if peer in Unassigned])
            for cell in Most_Constrained_Variables)
        #Guaranteed atleast one length will be longer than this
        MaxLen = 0
        #Scan through and find the maximum length
        for cell in Most_Constrained_Variables:
            if len(Constraining_Data[cell]) > MaxLen:
                MaxLen = len(Constraining_Data[cell])
        
        #Grab all those with MaxLen
        Most_Constraining_Variables = ([cell for cell in Most_Constrained_Variables
                                        if len(Constraining_Data[cell]) == MaxLen])
        
        #If more than one we tiebreak again!
        if len(Most_Constraining_Variables) > 1:
            #Wont ever effect more than 24 other cells, start with '0' as value
            Num_Constrained = 24
            Constraining_Value = '0'
            #Just pick a cell to start with, this should get mutated anyways
            Cell = Most_Constraining_Variables[0]
            #for every cell and every cells value check how many peers that
            #that value will constrain
            for cell in Most_Constraining_Variables:
                for Value in AvailableValues[cell]:
                    if (len([peer for peer in ConditionalPeers[cell]
                             if Value in AvailableValues[peer]])) < Num_Constrained:
                        Num_Constrained = len([peer for peer in ConditionalPeers[cell]
                                               if Value in AvailableValues[peer]])
                        Constraining_Value = Value
                        Cell = cell
            #We now know where the least constraining value is
            #We stick it to the front of the available values list for the variable
            #Causing it to be picked first
            AvailableValues[Cell] = AvailableValues[Cell].replace(Constraining_Value,"")
            AvailableValues[Cell] = Constraining_Value + AvailableValues[Cell]
            #Note here if two tie this will return the first one seen
            return Cell
            
            
        #If we get here only 1 so we return it
        return Most_Constraining_Variables[0]    
    #If we get here only 1 so we return it
    return Most_Constrained_Variables[0]
    
#Recursive backtrace + forwardcheck + heuristics
def Recursive_BacktraceForwardcheckHeuristics(Solutions,AvailableValues):
   #Check if we have a solution
    if CheckSolution(Solutions) == True:
        return Solutions
    #Forwardchecking
    if any(len(AvailableValues[cell]) == 0 for cell in cells):
        return False
    Unassigned = FindUnassignedCells(Solutions)
    #No special method, just pick first unassigned cell
    Var = HeuristicSelect(Unassigned,AvailableValues)
    #Explore the next node
    Add_Node()
    #Check all posible values to try and continue solving the problem
    for Value in AvailableValues[Var]:
        #Make a copy of Available values so we dont have to worry about restoring the
        #current one should this attempt fail
        NewAvailableValues = AvailableValues.copy()
        #Set the value in our solution and make it unavailable for peers in NewAvailableValues
        SetSolutionValue(Var,Value,Solutions,NewAvailableValues)
        #Recurse
        Result = Recursive_BacktraceForwardcheckHeuristics(Solutions,NewAvailableValues)
        #If we get anything but False here we've solved the puzzle!
        if Result != False:
            return Result
        #If we get here we failed, restore the solutions dictionary,
        #dont need to worry about AvailableValues since we copied it
        RemoveSolutionValue(Var,Solutions)
    #If we get here we've exhausted everything with no solutions so we fail
    return False




#Solve using heristic solving   
def HeuristicSolve(Problem):
    #Setup our time tracking
    from datetime import datetime
    start = datetime.now()
 
    #Stage our problem and begin solving it
    Solutions = StringRepToDictRep(Problem)
    AvailableValues = SetupAvailableValues(Solutions)
    Unassigned = FindUnassignedCells(Solutions)
    Result = Recursive_BacktraceForwardcheckHeuristics(Solutions,AvailableValues)
    
        #We've finished solving, output information
    finish = datetime.now()
    runtime = finish - start
    if Result != False:
        print ("Backtrace w Forwardchecking and Heuristics Sudoku solved exploring " + str(Nodes) +
               " nodes in " + str(runtime.total_seconds()) + " seconds")
    else:
        print "FAILURE"
    return Result
    


#Sudokus turned into strings!
Easy = '904000058000100097001800406000600040050409010090001000506004300340008000780000904'
Medium = '005020004000901006940070020480700093000000000750004018030010059500208000600050300'
Difficult = '200904000346080000900362000003000050805000109060000300000219006000040938000807002'
Evil = '020008600800007000073040000200005090500609004090300005000090310000200007002400080'

#Solve our sudoku using all our methods!
EasySol = BacktraceSolve(Easy)
Zero_Node()
MedSol = BacktraceSolve(Medium)
Zero_Node()
DiffSol = BacktraceSolve(Difficult)
Zero_Node()
EvilSol = BacktraceSolve(Evil)
Zero_Node()
EasySol2 = BacktraceForwardCheckingSolve(Easy)
Zero_Node()
MedSol2 = BacktraceForwardCheckingSolve(Medium)
Zero_Node()
DiffSol2 = BacktraceForwardCheckingSolve(Difficult)
Zero_Node()
EvilSol2 = BacktraceForwardCheckingSolve(Evil)
Zero_Node()
EasySol3 = HeuristicSolve(Easy)
Zero_Node()
MedSol3 = HeuristicSolve(Medium)
Zero_Node()
DiffSol3 = HeuristicSolve(Difficult)
Zero_Node()
EvilSol3 = HeuristicSolve(Evil)

for cell in cells:
    #I've checked the backtrace solutions by hand
    #Since we know they are correct, and these are
    #true Sudoku puzzles, the faster
    #Methods should have the exact same solutions
    assert(EasySol[cell] == EasySol2[cell])
    assert(MedSol[cell] == MedSol2[cell])
    assert(DiffSol[cell] == DiffSol2[cell])
    assert(EvilSol[cell] == EvilSol2[cell])
    assert(EasySol[cell] == EasySol3[cell])
    assert(MedSol[cell] == MedSol3[cell])
    assert(DiffSol[cell] == DiffSol3[cell])
    assert(EvilSol[cell] == EvilSol3[cell])
    
print ("Sudoku complete and solutions checked!")
