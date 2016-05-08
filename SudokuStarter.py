#!/usr/bin/env python
import struct, string, math
from copy import *

class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""
  
    def __init__(self, size, board):
      """the constructor for the SudokuBoard"""
      self.BoardSize = size #the size of the board
      self.CurrentGameBoard= board #the current state of the game board

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
        value placed on the GameBoard row and col are both zero-indexed"""

        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        #return a new board of the same size with the value added
        return SudokuBoard(self.BoardSize, self.CurrentGameBoard)
                                                                  
                                                                  
    def print_board(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for i in range(div):
            dash += "----"
            space += "    "
        for i in range(div):
            line += dash + "+"
            sep += space + "|"
        for i in range(-1, self.BoardSize):
            if i != -1:
                print "|",
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] > 9:
                        print self.CurrentGameBoard[i][j],
                    elif self.CurrentGameBoard[i][j] > 0:
                        print "", self.CurrentGameBoard[i][j],
                    else:
                        print "  ",
                    if (j+1 != self.BoardSize):
                        if ((j+1)//div != j/div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((i+1)//div != i/div):
                print line
            else:
                print sep

def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
    the value of each cell. Array elements holding a 0 are considered to be
    empty."""

    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val
    
    return board
    
def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
    correctly."""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    #check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if BoardArray[row][col]==0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
                            == BoardArray[row][col])
                        and (SquareRow*subsquare + i != row)
                        and (SquareCol*subsquare + j != col)):
                            return False
    return True

def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    board = parse_file(file_name)
    return SudokuBoard(len(board), board)

def solve(initial_board, forward_checking = False, MRV = False, Degree = False,
    LCV = False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """
    
    empties = findNum(initial_board, 0)
    domains = {(x, y): [] for x in range(initial_board.BoardSize) for y in range(initial_board.BoardSize)}
    
    for x in empties:
        domains[x] = range(1, initial_board.BoardSize+1) 
    
    # run forward checking on initial board
    if forward_checking:
        for x in domains.keys():
            if x not in empties:
                domains, anyEmpty = forwardCheck(initial_board, domains, initial_board.CurrentGameBoard[x[0]][x[1]], x)
    
    solved, failed, count, domains = backtrack(initial_board, forward_checking, MRV, Degree, LCV, 0, domains)    
    print "count:", count
    
    # print "Your code will solve the initial_board here!"
    # print "Remember to return the final board (the SudokuBoard object)."
    # print "I'm simply returning initial_board for demonstration purposes."
    return solved

def findNum(board_obj, number):
    """ finds all board positions that contain number """
    
    found = []
    board = board_obj.CurrentGameBoard
    for row_number, row in enumerate(board):
        for col_number, col in enumerate(row):
            if col == number:
                found.append((row_number, col_number))
   
    return found
    
def isConsistent(board_obj, val, position, count):
    """ determines if value is consistent with current board state """
    board = board_obj.CurrentGameBoard
    if val in board[position[0]]:
        return False, count+1
    elif val in (row[position[1]] for row in board):
        return False, count+1
    elif val in getSquare(board_obj, position, int(math.sqrt(board_obj.BoardSize))):
        return False, count+1
    else:
        return True, count+1
        
def getSquare(board_obj, pos, squareSize):
    """ return list of val in subsquare of position """
    
    board = board_obj.CurrentGameBoard
    SquareRow = pos[0] // squareSize
    SquareCol = pos[1] // squareSize
    
    rowIndices = [x + SquareRow * squareSize for x in range(0, squareSize)]
    colIndices = [x + SquareCol * squareSize for x in range(0, squareSize)]
    
    squareVals = []
    
    for row in rowIndices:
        for col in colIndices:
            squareVals.append(board[row][col])
    return squareVals
            
def backtrack(current_state, forward_checking, MRV, Degree, LCV, count, domains):
    """ Implement backtracking algorith """
    
    nb = deepcopy(current_state)
    domain_copy = deepcopy(domains)
    
    if is_complete(nb):
        return nb, False, count, domain_copy
    
    unassigned = findNum(nb, 0)
    result = nb
    
    if MRV:
        X, Y = MRVHeuristic(domain_copy, unassigned)
        #print "Using MRV!"
    else:     
        X, Y = unassigned[0]
        #print "No MRV :P"
        
    D = domain_copy[(X,Y)]
    for val in D:
        #print X, Y, D, val
        consistent, count = isConsistent(nb, val, (X, Y), count)
        if consistent:
            
            anyEmpty = False
            
            if forward_checking:
                domain_copy, anyEmpty = forwardCheck(nb, domain_copy, val, (X,Y))
                #print "Forward check!"
   

            if not anyEmpty:
                nb.CurrentGameBoard[X][Y] = val
                    
                result, failure, count, domain_copy = backtrack(result, forward_checking, MRV, Degree, LCV, count, domain_copy)
                if not failure: 
                    return result, False, count, domain_copy      
                
            # else:
            #     print "reset domains"
            #     new_domain = domain_copy 
    
    print "domain empty: ", X, Y
    return nb, True, count, domains
    
def forwardCheck(board_obj, original_domain, val, pos):
    """ do the forward checking """
    domains = deepcopy(original_domain)
    squareSize = int(math.sqrt(board_obj.BoardSize))
    
    SquareRow = pos[0] // squareSize
    SquareCol = pos[1] // squareSize
    
    rowIndices = [x + SquareRow * squareSize for x in range(squareSize)]
    colIndices = [x + SquareCol * squareSize for x in range(squareSize)]
    keys = [(x, y) for x in rowIndices for y in colIndices]
    keys += [(pos[0], y) for y in range(board_obj.BoardSize)]
    keys += [(x, pos[1]) for x in range(board_obj.BoardSize)]
    keys = list(set(keys))
    keys.remove(pos)
    
    howMany = 0
    # actually check domains; exit if forward checking leaves one var with an empty domain
    for key in keys:
        if val in domains[key]:
            domains[key].remove(val)
            howMany += 1
            if len(domains[key]) == 0:
                #print "forward check failed", key
                #print original_domain[(0,3)]
                return original_domain, True, howMany
    
    #print original_domain[(0,3)]        
    return domains, False, howMany
    
def MRVHeuristic(domains, unassigned):    
    """ chooses unassigned variable with fewest values remaining it its domain """
    
    otherDomains = {k: domains[k] for k in unassigned}
    #print unassigned
    #print otherDomains
    smallest = min(otherDomains, key=lambda k: len(otherDomains[k]))
    #print smallest
    
    return smallest[0], smallest[1]

def LCVHeuristic(board_obj, domains, varDomain):
    """ minimize forward check removals """

    currentMin = -1
    for val in varDomain:
        __, ___, howMany = forwardCheck(board_obj, domains, val, varDomain[val])
        if currentMin == -1 or howMany < currentMin:
            currentMin = howMany
            currentBest = val

    return currentBest

def DegreeHeuristic(board_obj, domains, unassigned):
    """ sum of unassigned var in row, col, subsquare """
    
    maxConstraints = 0
    for pos in unassigned:
        squareSize = int(math.sqrt(board_obj.BoardSize))
        
        SquareRow = pos[0] // squareSize
        SquareCol = pos[1] // squareSize
        
        rowIndices = [x + SquareRow * squareSize for x in range(squareSize)]
        colIndices = [x + SquareCol * squareSize for x in range(squareSize)]
        keys = [(x, y) for x in rowIndices for y in colIndices]
        keys += [(pos[0], y) for y in range(board_obj.BoardSize)]
        keys += [(x, pos[1]) for x in range(board_obj.BoardSize)]
        keys = list(set(keys))
        keys.remove(pos)

        count = 0
        for key in keys:
            if key in unassigned:
                count += 1
        if count > maxConstraints:
            maxConstraints = count
            currentBest = pos

    return currentBest