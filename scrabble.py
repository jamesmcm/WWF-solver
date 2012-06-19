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
        '''Double width tiles taken into account by appending spaces to tiles
            of single width therefore keeping the alignment intact          '''
        
        j=0
        while j<15:
            i=0
            while i<15:
                if len(self.board[j][i])==1:
                    print self.board[j][i] + ' ',
                else:
                    print self.board[j][i],
                i+=1
            if i==15: print

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
        self.emptyTiles=["0", "3W", "3L", "2W", "2L", "*"]
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
        '''AGM: Taking double and triple word tiles into account - the rules state that it doubles/triples it for each
        special tile that is present, so if you play a 5 score word across two DW tiles you get a score of 20, not 15'''
        if doubleWord!=0:
            score=score*(2**doubleWord)
        if tripleWord!=0:
            score=score*(3**tripleWord)
        return score
        
    def possibleWordlist(self, substring):
        mergedList='\n'.join(str(item) for item in self.wordlist)
        possibleList=re.findall(".*"+substring+r"+.*", mergedList)
        try:
            possibleList.remove(substring) #Don't want own substring returned
        except:
            print "Initial substring not in list"
        return possibleList

    def checkWordplay(self, board, Letters, pos, pWord):
        #Take words that could be played, check whether they can be played due to right-most stuff - i.e. do they lay perfectly on to another word or not
        return 0
        
    def boardScan(self, Board, Letters):
        ''' This method will do the board scan.
            Hooking will be dealt with by a special vertical scan in the case of 1 letter plays.'''
        #Horizontal scan
        i=0
        j=0
        k=0
        while j<15:
            while i<15:
                if not (Board.board[j][i] in self.emptyTiles):
                    #stop - use substrings
                    rowsplit=self.splitRow(Board.board[j])
                    print rowsplit
                    for m in range(rowsplit[0]):
                        pWordlist=self.possibleWordlist(rowsplit[1][m][1])
                        #cut down wordlist - first on availability of letters
                        N=len(pWordlist)
                        l=0
                        while l < N:
                            wasPopped=False
                            # for k in range(len(pWordlist[l])):
                                #split it around substring rather than just counting letters - can check if number of letters preceding substring is LE the number of preceding blanks
                                # if not ((pWordlist[l].count(list(pWordlist[l])[k]) == Letters.letters.count(list(pWordlist[l])[k])) or (rowsplit[1][i][1].count(list(pWordlist[l])[k]) == pWordlist[l].count(list(pWordlist[l])[k]))):

                            #Handle letters before substring
                            splitpWord=pWordlist[l].split(rowsplit[1][m][1])
                            lettersCopy=Letters.letters
                            if m==0:
                                cond=(len(splitpWord[0])>rowsplit[1][m][0])
                            else:
                                cond=(len(splitpWord[0])+1>rowsplit[1][m][0])
                            if cond:
                                pWordlist.pop(l)
                                N=len(pWordlist)
                                wasPopped=True
                            else:
                                for k in range(len(splitpWord[0])):
                                    if splitpWord[0].count(splitpWord[0][k]) > Letters.letters.count(splitpWord[0][k]):
                                        pWordlist.pop(l)
                                        N=len(pWordlist)
                                        wasPopped=True
                                        break
                                    else:
                                        #remove used letters from letters copy
                                        lettersCopy=list(lettersCopy)
                                        lettersCopy.remove(splitpWord[0][k])
                                        lettersCopy="".join(lettersCopy)
                                        #This probably repeats work from above and could be streamlined through direct checks and pops

                            #Handle letters after substring - here we need to accommodate the posibility of brdging with later words already played
                            if wasPopped==False:
                                if len(splitpWord[1])>(15-(rowsplit[1][m][3]+len(rowsplit[1][m][1]))):
                                    pWordlist.pop(l)
                                    N=len(pWordlist)
                                    wasPopped=True
                                    
                            if wasPopped==False:
                                allLetters=lettersCopy
                                for p in range(1,rowsplit[0]-m): #taking subsequent words only
                                    allLetters+=rowsplit[1][p][1]
                                # print allLetters
                                for h in range(len(splitpWord[1])):
                                    if splitpWord[1].count(splitpWord[1][h]) > allLetters.count(splitpWord[1][h]):
                                        pWordlist.pop(l)
                                        N=len(pWordlist)
                                        wasPopped=True
                                        break
                                
                            if wasPopped==False:
                                for z in range(len(splitpWord[1])):
                                    # print rowsplit[1][m][3]+len(rowsplit[1][m][1])+z
                                    if not ((Board.board[j][rowsplit[1][m][3]+len(rowsplit[1][m][1])+z] in self.emptyTiles) or (Board.board[j][rowsplit[1][m][3]+len(rowsplit[1][m][1])+z] == list(splitpWord[1])[z])):
                                        pWordlist.pop(l)
                                        N=len(pWordlist)
                                        wasPopped=True
                                        break
                                    
                            if wasPopped==False:
                                #Make sure we have space before next word if applicable
                                if not (rowsplit[1][m][3]+len(rowsplit[1][m][1])+len(splitpWord[1]) -1 == 14):

                                    if not (Board.board[j][rowsplit[1][m][3]+len(rowsplit[1][m][1])+len(splitpWord[1])] in self.emptyTiles):
                                        pWordlist.pop(l)
                                        N=len(pWordlist)
                                        wasPopped=True

                            if wasPopped==False:
                                # print pWordlist[l].split(rowsplit[1][i][1])
                                l+=1
                        print pWordlist
                        #This now works, but there is no check on whether words will fit to the right, this will be done in checkWordplay function
                    break
                i=i+1
            j=j+1
            i=0
                    
        return 0
                        
    def splitRow(self, rowList):
        ''' This method splits the list provided in to a data structure of substrings and the number of preceding blank spaces, and following blank spaces '''
        #data structure is [N, N*[#blankpreceding, SUBSTRING, #blankfollowing, pos]]
        i=0
        N=0
        l=0
        a=0
        b=0
        p=0
        returnData=[N, []]
        inWord=False
        prevWord=False
        #returnData[1].append([p, rowList[a:l],  
        while i<15:
            if not (rowList[i] in self.emptyTiles):
                if inWord==False:
                    inWord=True
                    if prevWord==True:
                        returnData[1].append([prevWordp, prevWordstring, i-l, prevWordpos])
                    N+=1
                    a=i
                    p=i-l
                    pos=i
                    
            elif (rowList[i] in self.emptyTiles):
                if inWord==True:
                    inWord=False
                    b=i
                    l=i
                    prevWord=True
                    prevWordp=p
                    prevWordstring=''.join(rowList[a:l])
                    prevWordpos=pos
                    
            i+=1
        returnData[0]=N
        if inWord==True:
            
            returnData[1].append([p, ''.join(rowList[a:15]), 0, pos])
        elif inWord==False and prevWord==True:
            returnData[1].append([p, ''.join(rowList[a:b]), 15-b, prevWordpos])
        # print returnData
        return returnData

"""
End of function/object definitions, beginning of test/running code
"""

if __name__ == "__main__":
    myBoard=Board()
    myBoard.updateBoard([2,0], "h", "FUC")
    myBoard.updateBoard([2,4], "h", "ING")



    myBoard.printBoard()
    mySolver=Solver()
    myLetters=Letters("YKRAETB")
    mySolver.boardScan(myBoard, myLetters)
    # mySolver=Solver()
    # mySolver.checkWordlist(myLetters, "CO")

