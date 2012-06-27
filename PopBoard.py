#!/usr/bin/python

"""
PopBoard.py

Copyright (C) 2012 Daniel O'Hanlon    

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

"""
Instantiation must be performed with a path to screenshot. GetHandLetters()
and GetBoardLetters() methods return a 1D and 2D list of each, respectively. 

Tesseract is currently ~85% accurate

Uses reference pixel to find WWF window (two pixels)
Uses vector to get from window to board and crop to board
Uses vector to get from board to hand and crop to hand
Implemented multiply + contrast to pick out letters,
    ignore black/white
Crops board into 15x15 cells, crops hand into 7 cells

TODO: Isolate hand, split into two classes perhaps
merge functions to minimise code repetition

Using:

Tesseract Open Source OCR Engine v3.02 with Leptonica:
http://code.google.com/p/tesseract-ocr/

DPO Sun 7 May 2012 02:55:12 BST

"""

import Image
import ImageEnhance
import ImageChops

import StringIO
import subprocess
import sys
import os
import string
import cPickle as pickle

from Bayes import *

class PopBoard(object):

    def __init__(self, sshot_path):

        try:
            self.sshot_img = Image.open(sshot_path)
        except:
            print "Could not find image file at" + sshot_path

        self.boardTLToBoardBR = (525,525)
        self.boardTLToHandTL = (127,531)
        self.handTLToHandBR = (272,44)
        self.windowToBoard = (233,60)

        # Get location of the top left of the WWF window
        self.windowTopLeft = self.windowLoc(self.sshot_img)

        self.boardTL = (self.windowTopLeft[0] + self.windowToBoard[0], self.windowTopLeft[1] + self.windowToBoard[1])
        self.handTL = (self.boardTL[0] + self.boardTLToHandTL[0], self.boardTL[1] + self.boardTLToHandTL[1])
        self.cellD = (35,35)

        self.cellDHand = (38,23)

    def grabBoard(self, img):
        """
        Returns (cropped) board image using translation vectors relative to reference pixel
        """
        boardBR = (self.boardTL[0] + self.boardTLToBoardBR[0], self.boardTL[1] + self.boardTLToBoardBR[1])

        board = img.crop(self.boardTL + boardBR)

        return board

    def grabHand(self, img):
        """
        Returns (cropped) hand image using translation vectors relative to reference pixel
        """
        handBR = (self.handTL[0] + self.handTLToHandBR[0], self.handTL[1] + self.handTLToHandBR[1])

        hand = img.crop(self.handTL + handBR)

        return hand

    def windowLoc(self, img):
        """
        Scans through pixels to find the reference pixel value, the top left corner
        of the WWF flash window
        """

        dat = self.sshot_img.load()

        refPixFS = (173,171,172) # Reference value for fullscreen
        refPixWN = (172,172,172) # Reference value for windowed

        for i in range(0,img.size[1]):
            for j in range(0,img.size[0]):
                if ((dat[j,i] == refPixFS and dat[j+1,i] == refPixFS)or \
                        (dat[j,i] == refPixWN and dat[j+1,i]== refPixWN)):
                    loc = (j,i)
                    return loc
        # nothing found
        return -1

    def contrast(self, cropped_img):
        """
        Provides a high contrast board image for input into Tesseract OCR
        """

        # Convert the board image into greyscal
        
        bwImg=cropped_img.convert("L")

        # Multiply board image with inverted image so that text is black

        bwImgM = ImageChops.multiply(ImageChops.invert(bwImg), bwImg)

        # Increase contrast

        enhancedImg = ImageEnhance.Contrast(bwImgM)
        bwImgM = enhancedImg.enhance(5.0)

        # Produce pixel image object (array) for operation (operates in place)

        bwMDat = bwImgM.load()

        # If the pixel value is not black, make it white
        # (No colours any more, I want them to turn black)

        for i in range(0, bwImgM.size[1]):
            for j in range(0, bwImgM.size[0]):
                if (bwMDat[j,i]!=0):
                    bwMDat[j,i]=255
        # Debugging
        #bwImgM.show()

        return bwImgM

    def grabBoardCells(self):
        """
        Splits the board image into individual cell images
        """
        cells = [["0" for col in range(15)] for row in range(15)]
        board = self.contrast(self.grabBoard(self.sshot_img)) 
        # not pythonic

        for i in range(0,15):
            for j in range(0,15):
                cellLoc = (j*self.cellD[1],i*self.cellD[0])
                cropTo = (cellLoc[0]+self.cellD[0],cellLoc[1]+self.cellD[1])
                cells[i][j]=board.crop(cellLoc + cropTo)
                cells[i][j]=cells[i][j].crop((6,6) + (25,30)) # Crop to remove rubbish
                cells[i][j].load()

        return cells

    def grabHandCells(self):
        """
        Splits the hand image into individual cell images
        """

        cells = ["0" for i in range(7)]
        hand = self.contrast(self.grabHand(self.sshot_img))
        #not pythonic

        handOffset = (9,11)
        
        for i in range(0,7):
            cellLoc = (handOffset[0] + i*self.cellDHand[0], handOffset[1])
            cropTo = (cellLoc[0]+self.cellDHand[0], cellLoc[1]+self.cellDHand[1])
            cells[i] = hand.crop(cellLoc + cropTo)
            cells[i] = cells[i].crop((0,0)+(22,21)) # Crop to remove rubbish
            cells[i].load()

        return cells
        
    def getBoardLetters(self):
        """
        Operates on board cells using Tesseract via a system command and returns the ASCII board letters
        """

        cell = self.grabBoardCells()

        board  = [["-" for col in range(15)] for row in range(15)]

        path = 'tmp/img'

        for i in range(15):
            for j in range(15):

                stringI = cell[i][j].tostring()
                sizeI = cell[i][j].size
                img = Image.fromstring("L",sizeI,stringI)
                img.save(path + '.png')

                # push to /dev/null to suppress irritating output (each time!)

                cmd = 'tesseract' + ' ' + path+'.png'+ ' ' +path +' -l eng' + ' -psm 7' + ' 2> /dev/null' 
                proc = subprocess.call(cmd, shell=True)
                f = file(path + '.txt')
                char = f.read().strip()

                for letter in range(len(string.uppercase)):
                    if char == string.uppercase[letter]:
                        board[i][j] = char

                #cleanup
                os.remove(path+'.png')
                os.remove(path+'.txt')

        return board

    def getHandLetters(self):
        """
        Operates on hand cells using Tesseract via a system command and returns the ASCII board letters
        """

        cell = self.grabHandCells()

        hand  = ["-" for col in range(7)]

        path = 'tmp/img'

        for i in range(7):
            stringI = cell[i].tostring()
            sizeI = cell[i].size
            img = Image.fromstring("L",sizeI,stringI)
            img.save(path + '.png')

            # push to /dev/null to suppress irritating output (each time!)

            cmd = 'tesseract' + ' ' + path+'.png'+ ' ' +path +' -l eng' + ' -psm 7' + ' 2> /dev/null' 
            proc = subprocess.call(cmd, shell=True)
            f = file(path + '.txt')
            char = f.read().strip()

            for letter in range(len(string.uppercase)):
                if char == string.uppercase[letter]:
                    hand[i] = char

            #cleanup
            os.remove(path+'.png')
            os.remove(path+'.txt')

        return hand

    def makevec(self, cell):
        """
        Makes a vector for use with Bayes from a cell image. Probably belongs in a separate class(!)
        """

        xsize = cell.size[0]
        ysize = cell.size[1]

        vec1 = intvec1D(xsize)
        vec2 = intvec2D(ysize)

        letter = cell.load()

        for y in range(0, ysize):
            for x in range(0, xsize):
                vec1[x] = letter[x,y]
            vec2[y] = vec1

        return vec2

    def makelistv(self, list_lett):
        """
        Makes a vector for use with Bayes from a list. Probably belongs in a separate class(!)
        """

        xsize = len(list_lett)
        ysize = len(list_lett[0])

        vec1 = intvec1D(xsize)
        vec2 = intvec2D(ysize)

        for y in range(0, ysize):
            for x in range(0, xsize):
                vec1[x] = list_lett[x][y]
            vec2[y] = vec1

        return vec2

    def makelist(self, cell):
        """
        Makes a list for use with Bayes (eventually) from a cell image. Probably belongs in a separate class(!)
        For pickling (cannot pickle SWIG or PIL objects)
        """

        xsize = cell.size[0]
        ysize = cell.size[1]

        list_lett  = [[0 for col in range(ysize)] for row in range(xsize)]

        letter = cell.load()

        for y in range(0, ysize):
            for x in range(0, xsize):
                list_lett[x][y] = letter[x,y]

        return list_lett


if __name__ == "__main__":

    board = PopBoard("sshot.jpg")
    cell = board.grabBoardCells()

    # board2 = PopBoard("sshot2.jpg")
    # cell2 = board2.grabBoardCells()

    # pickle.dump(board.makelist(cell[3][3]), open("A.p", "wb"))
    # pickle.dump(board.makelist(cell[7][8]), open("B.p", "wb"))
    # pickle.dump(board.makelist(cell[3][4]), open("C.p", "wb"))
    # pickle.dump(board.makelist(cell[3][6]), open("D.p", "wb"))
    # pickle.dump(board.makelist(cell[7][11]), open("E.p", "wb"))
    # pickle.dump(board2.makelist(cell[3][10]), open("F.p", "wb")) #####
    # pickle.dump(board.makelist(cell[9][9]), open("G.p", "wb"))
    # pickle.dump(board2.makelist(cell[5][14]), open("H.p", "wb")) #####
    # pickle.dump(board.makelist(cell[7][7]), open("I.p", "wb"))
    # pickle.dump(board2.makelist(cell[13][5]), open("J.p", "wb")) #####
    # pickle.dump(board2.makelist(cell[2][4]), open("K.p", "wb")) #####
    # pickle.dump(board.makelist(cell[1][11]), open("L.p", "wb"))
    # pickle.dump(board.makelist(cell[3][14]), open("M.p", "wb"))
    # pickle.dump(board.makelist(cell[14][3]), open("N.p", "wb"))
    # pickle.dump(board.makelist(cell[1][10]), open("O.p", "wb"))
    # pickle.dump(board.makelist(cell[3][2]), open("P.p", "wb"))
    # pickle.dump(board2.makelist(cell[5][9]), open("Q.p", "wb")) #####
    # pickle.dump(board.makelist(cell[14][5]), open("R.p", "wb"))
    # pickle.dump(board.makelist(cell[7][10]), open("S.p", "wb"))
    # pickle.dump(board.makelist(cell[1][12]), open("T.p", "wb"))
    # pickle.dump(board.makelist(cell[5][8]), open("U.p", "wb"))
    # pickle.dump(board.makelist(cell[1][9]), open("V.p", "wb"))
    # pickle.dump(board.makelist(cell[9][5]), open("W.p", "wb"))
    # pickle.dump(board.makelist(cell[4][10]), open("X.p", "wb"))
    # pickle.dump(board.makelist(cell[6][6]), open("Y.p", "wb"))
    # pickle.dump(board.makelist(cell[8][14]), open("Z.p", "wb"))

    alphabet = dict.fromkeys(string.ascii_uppercase, 0)
    letters = dict.fromkeys(string.ascii_uppercase, 0)

    for key in alphabet:
        alphabet[key] = board.makelistv(pickle.load(open("etc/" + key + ".p", "rb")))
        letters[key] = Letter(alphabet[key])

    # I_lett = Letter(alphabet["I"])
    # B_lett = Letter(alphabet["B"])
    # S_lett = Letter(alphabet["S"])
    # E_lett = Letter(alphabet["E"])

    Ulett = LetterUnknown(alphabet["A"])

    b = Bayes(cell[7][7].size[0], cell[7][7].size[1], Ulett)

    for key in letters:
        b.insert_letter(key, letters[key])

    # b.insert_letter("I", I_lett)
    # b.insert_letter("B", B_lett)
    # b.insert_letter("S", S_lett)
    # b.insert_letter("E", E_lett)

    b.alphabet_total()

    print b.most_likely()








