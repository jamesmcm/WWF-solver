'''
Use reference pixel to find WWF window (two pixels)
Use vector to get from window to board and crop to board
Use vector to get from board to hand and crop to hand

Implemented multiply + contrast to pick out letters,
    ignore black/white

TODO:
Multiply and contrast hand cropped image
Crop board into 15x15 cells, crop hand into 7 cells
Sum pixel values over cell, compare to known values to
     identify WL, TL (etc) and empty vs letter  
Get all letters and pixel values (groan)

DPO 00:31 19/03/2012
'''



import Image
import ImageEnhance
import ImageChops

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

    def grabBoard(self, img):
        '''
        Returns (cropped) board image using translation vectors relative to reference pixel
        '''
        #boardTL = (self.windowTopLeft[0] + self.windowToBoard[0], self.windowTopLeft[1] + self.windowToBoard[1]) Needs to be in init (?)
        boardBR = (boardTL[0] + self.boardTLToBoardBR[0], boardTL[1] + self.boardTLToBoardBR[1])

        board = img.crop(self.boardTL + boardBR)

        return board

    def grabHand(self, img):
        '''
        Returns (cropped) hand image using translation vectors relative to reference pixel
        '''
        handTL = (self.boardTL[0] + self.boardTLToHandTL[0], self.boardTL[1] + self.boardTLToHandTL[1])
        handBR = (handTL[0] + self.handTLToHandBR[0], handTL[1] + self.handTLToHandBR[1])

        hand = img.crop(handTL + handBR)

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

        bwBoardM = ImageChops.multiply(bwBoard, bwBoardI)

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
        bwHandM.show()
        return bwHandM

    def grabBoardCells(self):
        cellSize = (35,35)
        cellH = (0,35)
        cellV = (35,0)
        cell = [["0" for col in range(15)] for row in range(15)]

        board = self.contrastBoard()

        for i in range(0,15):
            for j in range(0,15):
                cellLoc= (self.boardTL[1]+i*cellH[1],self.boardTL[0]+j*cellV[0])
                cropTo = (cellLoc[0]+cellSize[0],cellLoc[1]+cellSize[1])
                cell[j][i]=board.crop(cellLoc+cropTo)
                print cellLoc+cropTo
        return cell

# Debugging
pb = PopBoard()
#cell = pb.grabBoardCells()
#cell[11][14].show()
pb.contrastHand()
