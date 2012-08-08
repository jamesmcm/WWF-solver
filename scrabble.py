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
            of single width therefore keeping the alignment intact. '''
        
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
        mergedList='\n'.join(str(item) for item in self.wordlist) #get all the words separated by \n
        mergedList=re.sub('\r', '', mergedList) #remove \r characters
        possibleList=re.findall(".*"+substring+r"+.*", mergedList) 
        #return all words that contain the substring,r denotes rawstring
        #import pdb; pdb.set_trace() - debugger code
        try:
            possibleList.remove(substring) #Don't want own substring returned (i.e. don't return the already played word)
        except:
            print "Initial substring not in list" #i.e. word already played on board, isn't in dictionary?
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
        ''' Scans across board left to right then down a row then left to right (like reading a page)
        until it hits the first letter, it then calls splitRow to get the words on the current row
        and their spacings'''
        while j<15: #row number (y co-ordinate)
            while i<15: #column number (x co-ordinate)
                if not (Board.board[j][i] in self.emptyTiles): #if (letter) then...
                    #stop - use substrings
                    rowsplit=self.splitRow(Board.board[j]) #get words on row
                    print rowsplit
                    for m in range(rowsplit[0]):
                        pWordlist=self.possibleWordlist(rowsplit[1][m][1])
                        #calls possibleWordList on each word to find possible words that can be formed
                        #based on that word
                        #cut down wordlist - first on availability of letters
                        N=len(pWordlist) #number of possible words
                        l=0
                        while l < N:
                            wasPopped=False
                            # for k in range(len(pWordlist[l])):
                                #split it around substring rather than just counting letters - can check if number of letters preceding substring is LE the number of preceding blanks
''' was this ever done?? is this how it works now?? or is this how it used to work? or a future idea? '''
                                # if not ((pWordlist[l].count(list(pWordlist[l])[k]) == Letters.letters.count(list(pWordlist[l])[k])) or (rowsplit[1][i][1].count(list(pWordlist[l])[k]) == pWordlist[l].count(list(pWordlist[l])[k]))):

                            #Handle letters before substring
                            splitpWord=pWordlist[l].split(rowsplit[1][m][1])
#split the possible words about the substring (already played word)
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
                        #This now works, but there is no check on whether words will fit to the right
                        #this will be done in checkWordplay function
                    break
                i=i+1
            j=j+1
            i=0
                    
        return 0
                        
    def splitRow(self, rowList):
        ''' This method splits the list provided in to a data structure of substrings and the number of preceding blank spaces, and following blank spaces '''
        '''data structure is:
        [N, [#blankpreceding, SUBSTRING1, #blankfollowing, position],
            [#blankpreceding, SUBSTRING2, #blankfollowing, position],
        ...,[#blankpreceding, SUBSTRINGN, #blankfollowing, position]]'''
        # where N is the number of substrings found 
        i=0 #iterates across row
        N=0 #Number of substrings found
        l=0 # the position of the end of the previous word? always seems to be equal to b??
        a=0 # the position of the most recently encountered start of a word 
        b=0 # the position of the most recently encountered end of a word
        p=0 # the number of preceding empty tiles
        returnData=[N, []] #Data structure to be returned
        inWord=False #Flag which declares whether the cursor is currently in a word or on empty tile
        prevWord=False #Flag which declares whether a word has previously been encountered on the row

        #returnData[1].append([p, rowList[a:l],   umm... wtf was this? It isn't even complete?  

        while i<15:
            if not (rowList[i] in self.emptyTiles): # equivalent to if(letter)
                if inWord==False:
                    inWord=True #we are now in a word so if this is the start of a word the flag must be set
                    if prevWord==True:
                        returnData[1].append([prevWordp, prevWordstring, i-l, prevWordpos])
                        #we are now in a word, so we know how many spaces come after the previous word
                        #therefore we now have sufficient information to return the previous word to
                        #the data structure - obviously this requires that there was a previous word
                        #thus the flag check
                    N+=1 #increase substring (word) count by one
                    a=i # set a to be the start of the new word
                    p=i-l # calculate number of preceding empty tiles of new word
                    pos=i # set pos to be start of the word
                    
            elif (rowList[i] in self.emptyTiles): #if we are on an empty tile
                if inWord==True:
                    inWord=False #check if we have left a word and update flag
                    b=i
                    l=i #set b and l to the position of the first space after the word
                    prevWord=True #we just left a word so now there is obv. a previous word in existence
                    prevWordp=p #set the number of preceding empty tiles of the previous word
                    #this doesn't actually seem necessary as the previous word data is pushed PRIOR
                    #to setting the new p value so it is redundant, but safer I guess?
                    prevWordstring=''.join(rowList[a:l]) 
                    '''grabs previous word - python doesn't include the 2nd index so it doesn't
                    grab the space,i.e. a noob would guess it'd be a:(l-1), python also counts from zero'''
                    prevWordpos=pos #grabs previous word position
                    
            i+=1
        returnData[0]=N #after scan is complete puts total word count as first bit of data returned
        if inWord==True:
            #if we have reached the end of the board and are still in a word, then there are no
            #spaces following that word, and the word ends at the end of the row
            returnData[1].append([p, ''.join(rowList[a:15]), 0, pos])
        elif inWord==False and prevWord==True:
            #if we have reached the end and are not in a word, then the previous word (assuming one exists)
            #has spaces following it up until the end of the board
            returnData[1].append([p, ''.join(rowList[a:b]), 15-b, prevWordpos])
        # print returnData
        return returnData

    def splitColumn(self, colList):
        ''' Analogous method to above but for columns not rows - however I believe a better implementation
        than the above method would be to concatenate the colList into a string and then use the regular
        expression library to extract the relevant information, the data should be returned in the same form
        as splitRow for consistency - I will code this asap, but lack of WLAN makes it hard to look up
        libraries'''
        N=0 #Number of substrings (words) found
        returnData = [N, []] #Data structure to be returned
        #In order to allow this to be successful first must replace all item in emptyTiles with spaces
        for item in colList:
            if item in self.emptyTiles:
                item = " "
        #need to check for letters and split then calculate values
        

"""
End of function/object definitions, beginning of test/running code
"""

if __name__ == "__main__":
    myBoard=Board()
    myBoard.updateBoard([2,0], "h", "LON")
    myBoard.updateBoard([2,4], "h", "ING")



    myBoard.printBoard()
    mySolver=Solver()
    myLetters=Letters("YKRAEGB")
    mySolver.boardScan(myBoard, myLetters)
    # mySolver=Solver()
    # mySolver.checkWordlist(myLetters, "CO")

