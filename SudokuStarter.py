# netID: ldu917

#!/usr/bin/env python
import struct, string, math
from copy import *
import time

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
    global start_time
    start_time = time.clock()

    empties = findNum(initial_board, 0)
    domains = {(x, y): [] for x in range(initial_board.BoardSize) for y in range(initial_board.BoardSize)}
    # print domains

    for x in domains:
        if x in empties:
            domains[x] = range(1, initial_board.BoardSize+1)
        else:
            domains[x] = [initial_board.CurrentGameBoard[x[0]][x[1]]]

    # run forward checking on initial board
    if forward_checking:
        for x in domains:
            if x not in empties:
                domains, anyEmpty, howMany = forwardCheck(initial_board, domains, initial_board.CurrentGameBoard[x[0]][x[1]], x)
    #print domains
    #print "board structure"
    #print initial_board.CurrentGameBoard

    solved, failed, count, domains = backtrack(initial_board, forward_checking, MRV, Degree, LCV, 0, domains)
    if failed:
        print "Fail"
    print "count:", count

    # print "Your code will solve the initial_board here!"
    # print "Remember to return the final board (the SudokuBoard object)."
    # print "I'm simply returning initial_board for demonstration purposes."
    return solved

def findNum(board_obj, number):
    """ returns a list of all board positions that contain number """

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
    #print board
    if val in board[position[0]]:
        return False, count+1
    if val in (row[position[1]] for row in board):
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

    rowIndices = [x + SquareRow * squareSize for x in range(squareSize)]
    colIndices = [x + SquareCol * squareSize for x in range(squareSize)]

    squareVals = []

    for row in rowIndices:
        for col in colIndices:
            squareVals.append(board[row][col])
    return squareVals

def backtrack(current_state, forward_checking, MRV, Degree, LCV, count, domains):
    """ Implement backtracking algorithm """

    nb = deepcopy(current_state)
    domain_copy = deepcopy(domains)

    if is_complete(nb):
        return nb, False, count, domain_copy

    #if time.clock() - start_time > 600:
    #    print "Out of time"
    #    return nb, True, count, domain_copy

    unassigned = findNum(nb, 0)

    if MRV:
        X, Y = MRVHeuristic(domain_copy, unassigned)
        #print "Using MRV!"
    else:
        X, Y = unassigned[0]
        #print "No MRV :P"

    D = domain_copy[(X,Y)]
    for val in D:
    
        domain_copy = deepcopy(domains)
        consistent, count = isConsistent(nb, val, (X, Y), count)
        # !!! IF forward checking, val is already consistent !!!

        #if consistent, assign value and continue dfs
        if consistent:
            anyEmpty = False
            if forward_checking:
                print "forward check", (X,Y), val, domain_copy[(0,5)]
                domain_copy, anyEmpty, howMany = forwardCheck(nb, domain_copy, val, (X,Y))
                print "after fc ", domain_copy[(0,5)]
                #print "Forward check!"
            if not anyEmpty:
                nb.CurrentGameBoard[X][Y] = val
                domain_copy[(X,Y)] = [val]
                next_board, failure, count, new_domain = backtrack(nb, forward_checking, MRV, Degree, LCV, count, domain_copy)
                if not failure:
                    return next_board, False, count, new_domain
            else:
                domain_copy = deepcopy(domains)

    print "failed at ", val, "in ", (X,Y)
    return nb, True, count, domains

def forwardCheck(board_obj, original_domain, val, pos):
    """ do the forward checking """
    print "checking ", pos
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
    print keys
    howMany = 0
    # actually check domains; exit if forward checking leaves one var with an empty domain
    for key in keys:
        if val in domains[key]:
            domains[key].remove(val)
            print "removing ", val, "from ", key
            howMany += 1
            if len(domains[key]) == 0:
                #print "forward check failed", key
                #print original_domain[(0,3)]
                print "domain empty: ", key
                return original_domain, True, howMany

    #print original_domain[(0,3)]
    return domains, False, howMany

def MRVHeuristic(domains, unassigned):
    """ chooses unassigned variable with fewest values remaining in its domain """

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

four = init_board("input_puzzles/easy/4_4.sudoku")
nine = init_board("input_puzzles/easy/9_9.sudoku")
sixteen = init_board("input_puzzles/easy/16_16.sudoku")
twofive = init_board("input_puzzles/easy/25_25.sudoku")
