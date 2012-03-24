'''
Use reference pixel to find WWF window (two pixels)
Use vector to get from window to board and crop to board
Use vector to get from board to hand and crop to hand
Implemented multiply + contrast to pick out letters,
    ignore black/white
Crop board into 15x15 cells, crop hand into 7 cells

TODO:
Using:

Tesseract Open Source OCR Engine v3.02 with Leptonica

Write some classes

DPO Sat Mar 24 01:56:21 GMT 2012

'''

import Image
import ImageEnhance
import ImageChops

import StringIO
import subprocess
import sys
import os
import string

class PopBoard(object):

    def __init__(self):
        try:
            self.sshot_img = Image.open("WWF2.jpg")
        except:
            print "Could not find image file"
        self.boardTLToBoardBR = (525,525)
        self.boardTLToHandTL = (127,531)
        self.handTLToHandBR = (272,44)
        self.windowToBoard = (233,60)
        # Get location of the top left of the WWF window
        self.windowTopLeft = self.windowLoc(self.sshot_img)
        self.boardTL = (self.windowTopLeft[0] + self.windowToBoard[0], self.windowTopLeft[1] + self.windowToBoard[1])
        self.handTL = (self.boardTL[0] + self.boardTLToHandTL[0], self.boardTL[1] + self.boardTLToHandTL[1])
        self.cellD = (35,35)
        #self.cellDHand = (23,23)
        self.cellDHand = (38,23)

    def grabBoard(self, img):
        '''
        Returns (cropped) board image using translation vectors relative to reference pixel
        '''
        boardBR = (self.boardTL[0] + self.boardTLToBoardBR[0], self.boardTL[1] + self.boardTLToBoardBR[1])

        board = img.crop(self.boardTL + boardBR)

        return board

    def grabHand(self, img):
        '''
        Returns (cropped) hand image using translation vectors relative to reference pixel
        '''
        handBR = (self.handTL[0] + self.handTLToHandBR[0], self.handTL[1] + self.handTLToHandBR[1])

        hand = img.crop(self.handTL + handBR)

        return hand

    def windowLoc(self, img):
        '''
        Scans through pixels to find the reference pixel value, the top left corner
        of the WWF flash window
        '''

        dat = self.sshot_img.load()

        refPixFS = (173,171,172) # Reference value for fullscreen
        refPixWN = (172,172,172) # Reference value for windowed

        for i in range(0,img.size[1]):
            for j in range(0,img.size[0]):
                if ((dat[j,i] == refPixFS and dat[j+1,i] == refPixFS)or \
                        (dat[j,i] == refPixWN and dat[j+1,i]== refPixWN)):
                    loc = (j,i)
                    return loc

    def contrastBoard(self):
        board = self.grabBoard(self.sshot_img)

        # Convert the board image into greyscale and invert
        
        bwBoard=board.convert("L")
        bwBoardI=ImageChops.invert(bwBoard)
        # Multiply board image with inverted image so that text is black

        bwBoardM = ImageChops.multiply(bwBoardI, bwBoard)

        # Increase contrast

        enh = ImageEnhance.Contrast(bwBoardM)
        bwBoardM = enh.enhance(5.0)

        # Produce pixel image object (array) for operation (operates in place)

        bwBoardMDat = bwBoardM.load()

        # If the pixel value is not black, make it white
        # (No colours any more, I want them to turn black)

        for i in range(0, bwBoardM.size[1]):
            for j in range(0, bwBoardM.size[0]):
                if (bwBoardMDat[j,i]!=0):
                    bwBoardMDat[j,i]=255
        # Debugging
        #bwBoardM.show()

        return bwBoardM

    def contrastHand(self): # Merge these into one function....
        hand = self.grabHand(self.sshot_img)

        bwHand=hand.convert("L")
        bwHandI=ImageChops.invert(bwHand)

        # Multiply hand image with inverted image so that text is black

        bwHandM = ImageChops.multiply(bwHand, bwHandI)

        # Increase contrast

        enh = ImageEnhance.Contrast(bwHandM)
        bwHandM = enh.enhance(5.0)

        # Produce pixel image object (array) for operation (operates in place)

        bwHandMDat = bwHandM.load()

        # If the pixel value is not black, make it white
        # (No colours any more, I want them to turn black)

        for i in range(0, bwHandM.size[1]):
            for j in range(0, bwHandM.size[0]):
                if (bwHandMDat[j,i]!=0):
                    bwHandMDat[j,i]=255
         # Debugging
        #bwHandM.show()

        return bwHandM

    def grabBoardCells(self):
        cells = [["0" for col in range(15)] for row in range(15)]
        board = self.contrastBoard() 

        for i in range(0,15):
            for j in range(0,15):
                cellLoc = (j*self.cellD[1],i*self.cellD[0])
                cropTo = (cellLoc[0]+self.cellD[0],cellLoc[1]+self.cellD[1])
                cells[i][j]=board.crop(cellLoc + cropTo)
                cells[i][j]=cells[i][j].crop((6,6) + (25,30)) # Crop to remove rubbish
                cells[i][j].load()

        return cells

    def grabHandCells(self):
        # Require cellDHand, cell size is not the same as board!
        cells = ["0" for i in range(7)]
        hand = self.contrastHand()
        handOffset = (9,11)
        
        for i in range(0,7):
            cellLoc = (handOffset[0] + i*self.cellDHand[0], handOffset[1])
            cropTo = (cellLoc[0]+self.cellDHand[0], cellLoc[1]+self.cellDHand[1])
            cells[i] = hand.crop(cellLoc + cropTo)
            cells[i] = cells[i].crop((0,0)+(22,21)) # Crop to remove rubbish
            cells[i].load()
        
        return cells
        

# Debugging
pb = PopBoard()
cell = pb.grabBoardCells()

#cell[7][6].show()

board  = [["-" for col in range(15)] for row in range(15)]

path = 'tmp/img'

for i in range(15):
    for j in range(15):
        #print i, j
        stringI = cell[i][j].tostring()
        sizeI = cell[i][j].size
        img = Image.fromstring("L",sizeI,stringI)
        img.save(path+'.png')

        # push to /dev/null to suppress irritating output (each time)
        cmd = 'tesseract' + ' ' + path+'.png'  + ' '+path + ' -psm 7' +' -l eng' + ' > /dev/null' 
        proc = subprocess.call(cmd, shell=True)
        f = file(path+'.txt')
        char = f.read().strip()
        for letter in range(len(string.uppercase)):
            if char == string.uppercase[letter]:
                board[i][j] = char

        #cleanup
        os.remove(path+'.png')
        os.remove(path+'.txt')

for i in range(15):
    for j in range(15):
        print board[i][j],
    print '\n'


