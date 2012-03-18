''' General algorithm: Scan left to right.
    Take substrings on board. Find all anagrams of available letters and all substrings.
    Find which of these are possible (how?)
    Place these tiles on board. Score the placement, taking in to account vertical words made as well.

    TODO:
    Rastering algorithm.
    Blank tiles.
    Bridging words.
    Hooks.
    35 point bonus if all 7 tiles used.

    Algorithm: Scan across find all substrings, use these as letters and check for *substring* in wordlist for each substring
    Then drop returned words that we do not have additional letters for
    Then check words can be played (i.e. check position is empty or equal to the character being placed)
    
    '''
import re

class Board(object):
    '''This class holds the current board. Boards are 15x15'''

    def __init__(self):
        '''Board initialised here.'''
        self.board=[["0" for col in range(15)] for row in range(15)]
        #Add special tiles
        self.board[0][3]="3W"
        self.board[3][0]="3W"
        self.board[1][2]="2L"
        self.board[2][1]="2L"
        self.board[0][6]="3L"
        self.board[1][5]="2W"
        self.board[2][4]="2L"
        self.board[3][3]="3L"
        self.board[4][2]="2L"
        self.board[5][1]="2W"
        self.board[6][0]="3L"
        self.board[4][6]="2L"
        self.board[5][5]="3L"
        self.board[6][4]="2L"
        #mirror board, 7 is centre
        i=0
        j=0
        while j<7:
            while i<7:
                self.board[j][14-i]=self.board[j][i]
                self.board[14-j][i]=self.board[j][i]
                self.board[14-j][14-i]=self.board[j][i]                
                i+=1
            j+=1
            i=0
        #add remainders
        self.board[7][3]="2W"
        self.board[7][7]="*"
        self.board[7][11]="2W"
        self.board[3][7]="2W"
        self.board[11][7]="2W"
        
    def updateBoard(self, position, direction, word):
        #Board[Y-coordinate][X-coordinate]
        #Position given as [y, x]
        if direction == 'h':
            self.board[position[0]][position[1]:position[1]+len(word)]=word
        if direction == 'v':
            #self.board[position[0]:position[0]+len(word)][position[1]]=word
            i=0
            while i<len(word):
                self.board[position[0]+i][position[1]]=word[i]
                i+=1

    def printBoard(self):
        j=0
        while j<15:
            print ' '.join(self.board[j])
            j+=1

class Letters(object):
    '''This class holds the current letters.'''

    def __init__(self, letters):
        self.letters=letters

    def updateLetters(self, letters):
        self.letters=letters

class Solver(object):
    '''This class contains the solving algorithms.'''

    def __init__(self):
        f = open('./wordlist.txt', 'r')
        self.wordlist=f.read().split("\n")
        f.close()
        self.letterValues={"A":1, "B":4, "C":4, "D":2, "E":1, "F":4, "G":3, "H":3, "I":1, "J":10, "K":5, "L":2, "M":4, "N":2, "O":1, "P":4, "Q":10, "R":1, "S":1, "T":1, "U":2, "V":5, "W":4, "X":8, "Y":3, "Z":10, "*":0}
        
    def solveAnagram(self, string):
        ''' This method solves basic anagrams from string to wordlist.
            This will be used to take the substrings and return possible words to play. '''
        
        for line in self.wordlist:
            possibleSolution=True
            if len(line)!=len(string):
                possibleSolution=False
            while possibleSolution==True:
                for i in range(len(string)):
                    if string.count(line[i])!=line.count(line[i]):
                        possibleSolution=False
                        break
                if possibleSolution==True:
                  return line

    def scoreWord(self, Board, position, direction, word):
        ''' This method scores the one word play given. Perhaps bridged words should be scored separately, as they are in the rules, to avoid complication.
            This may complicate finding the bridge words though. Remember 35 point bonus if all 7 tiles used has not been applied here.'''
        tripleWord=0
        doubleWord=0
        score=0
        xpos=position[1]
        ypos=position[0]
        for i in range (len(word)):
            if direction=="h":
                if Board.board[ypos][xpos+i]=="3W":
                    tripleWord+=1
                    score+=self.letterValues[word[i]]
                elif Board.board[ypos][xpos+i]=="2W":
                    doubleWord+=1
                    score+=self.letterValues[word[i]]
                elif Board.board[ypos][xpos+i]=="2L":
                    score+=2*self.letterValues[word[i]]
                elif Board.board[ypos][xpos+i]=="3L":
                    score+=3*self.letterValues[word[i]]
                else :
                    score+=self.letterValues[word[i]]
            if direction=="v":
                if Board.board[ypos+i][xpos]=="3W":
                    tripleWord+=1
                    score+=self.letterValues[word[i]]
                elif Board.board[ypos+i][xpos]=="2W":
                    doubleWord+=1
                    score+=self.letterValues[word[i]]
                elif Board.board[ypos+i][xpos]=="2L":
                    score+=2*self.letterValues[word[i]]
                elif Board.board[ypos+i][xpos]=="3L":
                    score+=3*self.letterValues[word[i]]
                else :
                    score+=self.letterValues[word[i]]
        if doubleWord!=0:
            score=score*2*doubleWord
        if tripleWord!=0:
            score=score*3*tripleWord
        return score
        
    def possibleWordlist(self, substring):
        mergedList='\n'.join(str(item) for item in self.wordlist)
        return possibleList=re.findall(".*"+substring+r"+.*", mergedList)

    def checkWordplay(self, boardString, Letters):
        
    def boardScan(self, Board):
        ''' This method will do the board scan.
            Hooking will be dealt with by a special vertical scan in the case of 1 letter plays.'''
        #Horizontal scan
        emptyTiles=["0", "3W", "3L", "2W", "2L"]
        return 0
            

myBoard=Board()
myLetters=Letters("abcdefg")
mySolver=Solver()
mySolver.checkWordlist(myLetters, "CO")

