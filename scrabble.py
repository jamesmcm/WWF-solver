''' General algorithm: Scan left to right.
    Take substrings on board. Find all anagrams of available letters and all substrings.
    Find which of these are possible (how?)
    Place these tiles on board. Score the placement, taking in to account vertical words made as well. '''

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
        
    def solveAnagram(self, string):
        for line in self.wordlist:
            possibleSolution=True
            #line=line.replace("\n", "")
            #print line
            if len(line)!=len(string):
                possibleSolution=False
            while possibleSolution==True:
                for i in range(len(string)):
                    if string.count(line[i])!=line.count(line[i]):
                        possibleSolution==False
                        break
                if possibleSolution==True:
                    return line
myBoard=Board()
mySolver=Solver()
print mySolver.solveAnagram("OOOZ")

