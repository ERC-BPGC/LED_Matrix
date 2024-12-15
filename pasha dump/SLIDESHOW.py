import tkinter as tk
# import keyboard # for getting key inputs
import time
import random
import json

import math
import serial
# from serial import Serial
# import serial.tools.list_ports


# CREDITS

# ╔═══════════════BASE FRAMEWORK═════════════════════╗
# ║ object creation and management : AYUSH YADAV     ║
# ║ collisions, overlap detection  : AYUSH YADAV     ║
# ║ object translation             : AYUSH YADAV     ║
# ║ object rotation                : AYUSH YADAV     ║
# ║ font                           : AYUSH YADAV     ║
# ║ line, rectangle                : AYUSH YADAV     ║
# ║ input detection                : AYUSH YADAV     ║
# ╠═════════════════════GAMES════════════════════════╣
# ║ Snake Game                     : AYUSH YADAV     ║
# ║                                : GRACE PAUL      ║ (artwork)
# ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
# ║ Pong Game                      : ATHARV SALONKHE ║                             
# ║                                : AYUSH YADAV     ║ (bug fixes)
# ║                                : GRACE PAUL      ║ (artwork)
# ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
# ║ Tetris                         : HRISHANT        ║ 
# ║                                : NILESH BHATIA   ║
# ║                                : GRACE PAUL      ║ (artwork)
# ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
# ║ Space Shooter                  : GRACE PAUL      ║
# ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░║
# ║ Shoot the pixel                : NILESH BHATIA   ║
# ╚═════════SOFTWARE HARDWARE COMMUNICATION══════════╝
#           - NILAY WANI
#           - HRISHANT
#           - ATHARV SALONKHE


# SOME ASSUMPTIONS
# X values are the column numbers starting from 0 (LEFT) to 19 (RIGHT)
# Y values are the row numbers starting from 0 (TOP) to 39 (BOTTOM)
background = "#000000" # default color of the empty space change if needed

class object:
    # This class consists of one object (i.e. group of colored pixels)
    # the object acts as a incompressible / indestructible entity that can translate in space
    # the object structure is defined as follows
    # assume the object's origin to be at the origin of cartesian system then make a dictionary as follows
    # {
    #   "hexValueOfColor" : [(x1,y1),(x2,y2),(x3,y3)], 
    #   "hexValueOfColor" : [(x1,y1),(x2,y2),(x3,y3)], 
    #   "hexValueOfColor" : [(x1,y1),(x2,y2),(x3,y3)],
    #   ...
    # }
    # There can be many pixels of same color thus the above coloring system is taken
    # color of indivisual pixel can be changed later on using the function provided in this class [not recommended though
    # considering the simplicity of our display aka LED MATRIX]
    # 'data' is a dictionary consisting of the following
    # {
    #   "z_value" : int,
    #   "pos" : [int, int],
    #   "stayInFrame" : True,
    #   "collision" : True,
    #   "rotation" : False
    # }
    # 'z_value' : indicates the position of the object in z axis, higher the value further it is infront of the LED MATRIX,
    # thus 0 is at the back and 10 is infront if in any scenario two objects overlap z_value will decide which will be 
    # displayed infront
    # 'pos' : it represents the (X,Y) coordinate of the origin of the object on the LED MATRIX
    # 'stayInFrame' : a basic system that prevent the object from going out of bound 
    # 'collision' : a basic system that prevent the object from colliding with other objects
    # objects will collide only if offset() function is used and both the objects have "collision" set to True also both should
    # share the same layer (i.e. they have same zVal)
    # 'rotation' : enables object to rotate by multiples of 90 in either direction CW / CCW ... this system also checks if 
    # rotation in the desired direction is possible

    # OBJECT VARIABLES
    curr_pos = [0,0] # default value
    pixelArr = [] # consists of the hexadecial values of the pixels relative to origin ROW-WISE (top row first)
    bound_origin = [0,0] # the origin wrt the bounding box
    zVal = 0 # the location of object outward from the plane (Z position)
    frameCollision = False # turned True when bound collision is enabled
    collision = False # turned True when collision is enabled
    rotation = False # turned True when rotation is enabled
    pixDict = None # storing pixel dictionary to be used when rotation enabled
    rot_mid = None # stores mid position when rotation enabled

    # other variables
    topPad = 0
    botPad = 0
    lefPad = 0
    rigPad = 0
    minY = 0
    maxY = 0
    minX = 0
    maxX = 0

    def getBoundingBox(self, arrObj):

        if isinstance(arrObj, dict):
            arr = []
            for key in arrObj.keys():
                for coord in arrObj[key]:
                    arr.append(coord)
        else:
            arr = arrObj.copy()

        self.minY = None
        self.maxY = None
        self.minX = None
        self.maxX = None

        firstTime = True

        # print(arr)
        for coord in arr:
            
            if firstTime:
                self.minY = coord[1]
                self.maxY = coord[1]
                self.minX = coord[0]
                self.maxX = coord[0]
                firstTime = False

            # X
            if coord[0] < self.minX:
                self.minX = coord[0]
            if coord[0] > self.maxX:
                self.maxX = coord[0]

            # Y
            if coord[1] < self.minY:
                self.minY = coord[1]
            if coord[1] > self.maxY:
                self.maxY = coord[1]
        
        if self.rotation:
            # if rotation is enabled making a free pixel Arr to allow for rotation
            j = 1 + 2 * max([
                abs(self.maxX),
                abs(self.minX),
                abs(self.maxY),
                abs(self.minY)
            ])
            return [j,j]
        else:
            return [self.maxX-self.minX+1, self.maxY-self.minY+1]
    
    def calcPadding(self):
        self.lefPad = -self.minX
        self.rigPad = self.maxX
        self.topPad = -self.minY
        self.botPad = self.maxY
        # self.lefPad = self.bound_origin[0]
        # self.rigPad = len(self.pixelArr[0]) - self.bound_origin[0] - 1
        # self.topPad = self.bound_origin[1]
        # self.botPad = len(self.pixelArr) - self.bound_origin[1] - 1

        # print(self.lefPad) # DEBUG
        # print(self.rigPad)
        # print(self.topPad)
        # print(self.botPad)
    
    def calcBoundOrigin(self, size):
        # getting midpoint of the object and updating bound origin
        boundX = 0
        boundY = 0

        if self.rotation:
            mid = int((size[0] - 1)/2)
            self.bound_origin = [mid, mid]
        else:
            if self.minX < 0:
                boundX = -self.minX
            else:
                boundX = 0
            
            if self.minY < 0:
                boundY = -self.minY
            else:
                boundY = 0
            
            self.bound_origin = [boundX, boundY]

    def __init__(self, obj, data):
        # here 'obj' holds the dictionary of colored pixels thus defining the object
        # 'data' consists of other data as was stated above, these values are used to define the behaviour of this object

        # assigning basic variables
        if "pos" in data.keys():
            self.curr_pos = data["pos"]
        else:
            self.curr_pos = [0,0]

        if "z_value" in data.keys():
            self.zVal = data["z_value"]
        else:
            self.zVal = 0
        
        if "stayInFrame" in data.keys():
            self.frameCollision = data["stayInFrame"]
        else:
            self.frameCollision = False
        
        if "collision" in data.keys():
            self.collision = data["collision"]
        else:
            self.collision = False

        if "rotation" in data.keys():
            self.rotation = data["rotation"]
        else:
            self.rotation = False
        
        if self.rotation:
            self.pixDict = obj

        # making the blank pixel array
            
        # getting order of matrix
        size = self.getBoundingBox(obj)
        
        self.calcBoundOrigin(size)

        if self.rotation:
            mid = int((size[0] - 1)/2)
            self.rot_mid = mid

        self.pixelArr = []
        # making one row
        row_temp = []
        for i in range(size[0]):
            row_temp.append(None)
        # adding these rows in pixel array to create the blank array
        for i in range(size[1]):
            self.pixelArr.append(row_temp.copy())

        # coloring apropriate pixels
        #   iterating through the dictionary and coloring the pixels
        for k in obj.keys():
            for coord in obj[k]:
                # here k stores the hexadecimal value of the color and coord are the relative coordinated of pixels
                arrCoord_X = self.bound_origin[0] + coord[0]
                arrCoord_Y = self.bound_origin[1] + coord[1]
                self.pixelArr[arrCoord_Y][arrCoord_X] = k

        self.calcPadding() # calculate padding
    
    def translate(self, delta):
        newVec = [
            self.curr_pos[0] + delta[0],
            self.curr_pos[1] + delta[1]
        ]

        if self.frameCollision:
            if delta[0] > 0:
                # checking right wall calculation
                while (newVec[0] + self.rigPad) >= 20:
                    newVec[0] -= 1
            
            if delta[0] < 0:
                # checking left wall calculation
                while (newVec[0] - self.lefPad) <= -1:
                    newVec[0] += 1
            
            if delta[1] > 0:
                # checking bot wall calculation
                while (newVec[1] + self.botPad) >= 40:
                    newVec[1] -= 1
            
            if delta[1] < 0:
                # checking bot wall calculation
                while (newVec[1] - self.topPad) <= -1:
                    newVec[1] += 1
        
        self.curr_pos = newVec.copy()
    
    def changeColor(self, coord, color):
        arrCoord_X = self.bound_origin[0] + coord[0]
        arrCoord_Y = self.bound_origin[1] + coord[1]

        self.pixelArr[arrCoord_Y][arrCoord_X] = color

def updateCollision(obj, newPixArr):
    obj.pixelArr = newPixArr

    coordArr = []
    for y in range(len(newPixArr)):
        for x in range(len(newPixArr)):
            if newPixArr[y][x] is not None:
                if obj.rotation:
                    coordArr.append([
                        x - obj.rot_mid,
                        y - obj.rot_mid
                    ])
                else:
                    coordArr.append([
                        x,
                        y
                    ])

    size = obj.getBoundingBox(coordArr)
    obj.calcPadding()
    obj.calcBoundOrigin(size)

# this functions is used to check collisions with the objects already present in objArr
def checkOverlap(obj, newPos, against=None):
    global objArr

    checkObjs = None
    if against is not None:
        checkObjs = against.copy()
    else:
        checkObjs = objArr.copy()
    
    isOverLap = False
    for ob in checkObjs:
        if ob.collision and (ob != obj) and (ob.zVal == obj.zVal):
            for y in range(len(ob.pixelArr)):
                for x in range(len(ob.pixelArr[y])):
                    if ob.pixelArr[y][x] is not None:
                        if ob.rotation:
                            coordX = x - ob.rot_mid + ob.curr_pos[0]
                            coordY = y - ob.rot_mid + ob.curr_pos[1]
                        else:
                            coordX = x + ob.curr_pos[0] + ob.minX
                            coordY = y + ob.curr_pos[1] + ob.minY

                        for yN in range(len(obj.pixelArr)):
                            for xN in range(len(obj.pixelArr[yN])):
                                if obj.pixelArr[yN][xN] is not None:
                                    if obj.rotation:
                                        coordNX = xN - obj.rot_mid + newPos[0]
                                        coordNY = yN - obj.rot_mid + newPos[1]
                                    else:
                                        coordNX = xN + newPos[0] + obj.minX
                                        coordNY = yN + newPos[1] + obj.minY

                                    if (coordNX == coordX) and (coordNY == coordY):
                                        isOverLap = True
                                
                                if isOverLap:
                                    break
                            if isOverLap:
                                break
                    
                    if isOverLap:
                        break
                if isOverLap:
                    break
        if isOverLap:
            break

    # print(isOverLap) # DEBUG
    return isOverLap

def offset(obj, offset, against=None):

    if offset[0] == 0:
        Xdir = 0
    else:
        Xdir = int(offset[0] / abs(offset[0]))
    
    if offset[1] == 0:
        Ydir = 0
    else:
        Ydir = int(offset[1] / abs(offset[1]))

    C2 = offset.copy()

    j = [0,0]

    while True:
        if offset[0] - j[0] == 0:
            step = round(C2[1] - j[1])
        else:
            step = round((C2[1] - j[1]) / (abs(offset[0] - j[0])))
        j[0] += Xdir

        if against is not None:
            isOverlapping = checkOverlap(obj, [
                obj.curr_pos[0] + j[0],
                obj.curr_pos[1] + j[1]
            ], against)
        else:
            isOverlapping = checkOverlap(obj, [
                obj.curr_pos[0] + j[0],
                obj.curr_pos[1] + j[1]
            ])

        if isOverlapping:
            pass
        else:
            obj.translate([Xdir,0])
        
        for y in range(abs(step)):
            j[1] += Ydir

            if against is not None:
                isOverlapping = checkOverlap(obj, [
                    obj.curr_pos[0] + j[0],
                    obj.curr_pos[1] + j[1]
                ], against)
            else:
                isOverlapping = checkOverlap(obj, [
                    obj.curr_pos[0] + j[0],
                    obj.curr_pos[1] + j[1]
                ])

            if isOverlapping:
                pass
            else:
                obj.translate([0,Ydir])
        
        if (j == C2):
            break

def rotate(obj, amt, against=None):
    # this function rotates the given 'obj' by 'amt'
    # amt +1 = CCW by 90 degree ; +2 = CCW by 180 degree
    # amt -1 = CW  by 90 degree ; -2 = CW  by 180 degree

    def checkBounds(obj):

        # print(obj.lefPad, obj.rigPad)
        if (obj.curr_pos[0] < 0) or (obj.curr_pos[0] > 19):
            return False
        if (obj.curr_pos[1] < 0) or (obj.curr_pos[1] > 39):
            return False
        if obj.curr_pos[0] + obj.rigPad > 19:
            return False
        if obj.curr_pos[0] - obj.lefPad < 0:
            return False
        if obj.curr_pos[1] + obj.botPad > 39:
            return False
        if obj.curr_pos[1] - obj.topPad < 0:
            return False
        return True
    
    def getNewPixArr():
        mid = obj.rot_mid
        newPixArr = []

        # make empty
        temp = []
        for x in range(len(obj.pixelArr)):
            temp.append(None)
        for x in range(len(obj.pixelArr)):
            newPixArr.append(temp.copy())
        
        # iterating through the original Array and making the necessary swaps
        for y in range(len(obj.pixelArr)):
            for x in range(len(obj.pixelArr)):
                dX = x - mid
                dY = y - mid

                # CCW SWAP
                if amt < 0:
                    newPixArr[mid + dX][mid - dY] = obj.pixelArr[y][x]
                else:
                    newPixArr[mid - dX][mid + dY] = obj.pixelArr[y][x] 
        return newPixArr
    
    if not obj.rotation:
        raise Exception("object set to rotation:False yet rotate function was accessed")
    
    preservedArr = obj.pixelArr.copy() # save PixArr

    # resolve Rotate
    while amt > 4:
        amt -= 4
    while amt < -4:
        amt += 4
    
    # print(checkOverlap(obj,obj.curr_pos, against=against), not checkBounds(obj)) 
    
    # iterate rotation
    for a in range(abs(amt)):
        updateCollision(obj, getNewPixArr())

        # print(obj.lefPad, obj.rigPad, obj.topPad, obj.botPad, checkBounds(obj))
        # checking if this rotation causes collision
        if checkOverlap(obj, obj.curr_pos, against=against) or (not checkBounds(obj)):
            print("YO")
            # reverting changes
            updateCollision(obj, preservedArr.copy())

            # breaking the loop
            break
    

#         [0,0],[1,0],[2,0],
#         [0,1],[1,1],[2,1],
#         [0,2],[1,2],[2,2],
#         [0,3],[1,3],[2,3],
#         [0,4],[1,4],[2,4]

txtDict = {
    '0':[
        [0,0],[1,0],[2,0],
        [0,1],      [2,1],
        [0,2],      [2,2],
        [0,3],      [2,3],
        [0,4],[1,4],[2,4]
    ],
    '1':[
        [0,0],
        [0,1],
        [0,2],
        [0,3],
        [0,4]
    ],
    '2':[
        [0,0],[1,0],[2,0],
                    [2,1],
        [0,2],[1,2],[2,2],
        [0,3],
        [0,4],[1,4],[2,4]
    ],
    '3':[
        [0,0],[1,0],[2,0],
                    [2,1],
        [0,2],[1,2],[2,2],
                    [2,3],
        [0,4],[1,4],[2,4]
    ],
    '4':[
        [0,0],      [2,0],
        [0,1],      [2,1],
        [0,2],[1,2],[2,2],
                    [2,3],
                    [2,4]
    ],
    '5':[
        [0,0],[1,0],[2,0],
        [0,1],
        [0,2],[1,2],[2,2],
                    [2,3],
        [0,4],[1,4],[2,4]
    ],
    '6':[
        [0,0],[1,0],[2,0],
        [0,1],
        [0,2],[1,2],[2,2],
        [0,3],      [2,3],
        [0,4],[1,4],[2,4]
    ],
    '7':[
        [0,0],[1,0],[2,0],
                    [2,1],
                    [2,2],
                    [2,3],
                    [2,4]
    ],
    '8':[
        [0,0],[1,0],[2,0],
        [0,1],      [2,1],
        [0,2],[1,2],[2,2],
        [0,3],      [2,3],
        [0,4],[1,4],[2,4]
    ],
    '9':[
        [0,0],[1,0],[2,0],
        [0,1],      [2,1],
        [0,2],[1,2],[2,2],
                    [2,3],
        [0,4],[1,4],[2,4]
    ],
    'A':[
        [0,0],[1,0],[2,0],
        [0,1],      [2,1],
        [0,2],[1,2],[2,2],
        [0,3],      [2,3],
        [0,4],      [2,4]
    ],
    'B':[
        [0,0],[1,0],
        [0,1],      [2,1],
        [0,2],[1,2],
        [0,3],      [2,3],
        [0,4],[1,4]
    ],
    'C':[
              [1,0],[2,0],
        [0,1],
        [0,2],
        [0,3],
              [1,4],[2,4]
    ],
    'D':[
        [0,0],[1,0],
        [0,1],      [2,1],
        [0,2],      [2,2],
        [0,3],      [2,3],
        [0,4],[1,4],
    ],
    'E':[
        [0,0],[1,0],[2,0],
        [0,1],
        [0,2],[1,2],
        [0,3],
        [0,4],[1,4],[2,4]
    ],
    'F':[
        [0,0],[1,0],[2,0],
        [0,1],
        [0,2],[1,2],
        [0,3],
        [0,4],
    ],
    'G':[
        [0,0],[1,0],[2,0],
        [0,1],
        [0,2],      [2,2],
        [0,3],      [2,3],
        [0,4],[1,4],[2,4]
    ],
    'H':[
        [0,0],      [2,0],
        [0,1],      [2,1],
        [0,2],[1,2],[2,2],
        [0,3],      [2,3],
        [0,4],      [2,4]
    ],
    'I':[
        [0,0],[1,0],[2,0],
              [1,1],
              [1,2],
              [1,3],
        [0,4],[1,4],[2,4]
    ],
    'J':[
                    [2,0],
                    [2,1],
        [0,2],      [2,2],
        [0,3],      [2,3],
              [1,4]
    ],
    'K':[
        [0,0],      [2,0],
        [0,1],      [2,1],
        [0,2],[1,2],
        [0,3],      [2,3],
        [0,4],      [2,4]
    ],
    'L':[
        [0,0],
        [0,1],
        [0,2],
        [0,3],
        [0,4],[1,4],[2,4]
    ],
    'M':[
        [0,0],                  [4,0],
        [0,1],[1,1],      [3,1],[4,1],
        [0,2],      [2,2],      [4,2],
        [0,3],                  [4,3],
        [0,4],                  [4,4]
    ],
    'N':[
        [0,0],            [3,0],
        [0,1],[1,1],      [3,1],
        [0,2],      [2,2],[3,2],
        [0,3],            [3,3],
        [0,4],            [3,4]
    ],
    'O':[
              [1,0],
        [0,1],      [2,1],
        [0,2],      [2,2],
        [0,3],      [2,3],
              [1,4]
    ],
    'P':[
        [0,0],[1,0],[2,0],
        [0,1],      [2,1],
        [0,2],[1,2],[2,2],
        [0,3],
        [0,4],
    ],
    'Q':[
              [1,0],[2,0],
        [0,1],            [3,1],
        [0,2],            [3,2],
        [0,3],      [2,3],[3,3],
              [1,4],[2,4],[3,4],[4,4]
    ],
    'R':[
        [0,0],[1,0],
        [0,1],      [2,1],
        [0,2],[1,2],
        [0,3],      [2,3],
        [0,4],      [2,4]
    ],
    'S':[
        [0,0],[1,0],[2,0],
        [0,1],
        [0,2],[1,2],[2,2],
                    [2,3],
        [0,4],[1,4],[2,4]
    ],
    'T':[
        [0,0],[1,0],[2,0],
              [1,1],
              [1,2],
              [1,3],
              [1,4]
    ],
    'U':[
        [0,0],      [2,0],
        [0,1],      [2,1],
        [0,2],      [2,2],
        [0,3],      [2,3],
        [0,4],[1,4],[2,4]
    ],
    'V':[
        [0,0],      [2,0],
        [0,1],      [2,1],
        [0,2],      [2,2],
        [0,3],      [2,3],
              [1,4]
    ],
    'W':[
        [0,0],                  [4,0],
        [0,1],                  [4,1],
        [0,2],      [2,2],      [4,2],
        [0,3],      [2,3],      [4,3],
              [1,4],      [3,4]
    ],
    'X':[
        [0,0],      [2,0],
        [0,1],      [2,1],
              [1,2],
        [0,3],      [2,3],
        [0,4],      [2,4]
    ],
    'Y':[
        [0,0],      [2,0],
        [0,1],      [2,1],
              [1,2],
              [1,3],
              [1,4]
    ],
    'Z':[
        [0,0],[1,0],[2,0],
                    [2,1],
              [1,2],
        [0,3],
        [0,4],[1,4],[2,4]
    ],
    '+':[

              [1,1],
        [0,2],[1,2],[2,2],
              [1,3]
    ],
    '-':[
        

        [0,2],[1,2],[2,2]
        

    ],
    '*':[
        

        [0,2],      [2,2],
              [1,3],
        [0,4],      [2,4]
    ],
    '/':[

                    [2,1],
              [1,2],
        [0,3]
        
    ]
}


def txtObj(txt, cursor, fill, zValue, stayInFrame=True,collision=False):
    tLength = cursor[0]
    for c in txt:
        if c == '1':
            tLength += 2
        elif c in "MWQ":
            tLength += 6
        elif c == "N":
            tLength += 5
        else:
            tLength += 4
    
    if tLength > 20:
        raise Exception("txt length exceeded X pixel limit for the text = " + txt)
    else:
        pointArr = []
        travellingCursor = cursor.copy()

        for c in txt:
            charPix = txtDict[c]

            for coord in charPix:
                pointArr.append([
                    coord[0] + travellingCursor[0],
                    coord[1] + travellingCursor[1]
                ])
            
            if c == '1':
                travellingCursor[0] += 2
            elif c in "MWQ":
                travellingCursor[0] += 6
            elif c == "N":
                travellingCursor[0] += 5
            else:
                travellingCursor[0] += 4
        
        # centralize
        for index in range(len(pointArr)):
            pointArr[index] = [
                pointArr[index][0] - cursor[0],
                pointArr[index][1] - cursor[1]
            ]
        
        return object({
        fill:pointArr
        },{
            "z_value": zValue,
            "pos": cursor,
            "stayInFrame": stayInFrame,
            "collision": collision
        })

def rectangleObj(C1, C2, fill, zValue, stayInFrame=True,collision=False):
    Xsteps = C2[0] - C1[0]
    Ysteps = C2[1] - C1[1]

    if (Xsteps == 0) or (Ysteps == 0):
        return lineObj(C1, C2, fill, zValue, stayInFrame)

    Ydir = int(Ysteps / abs(Ysteps))
    Xdir = int(Xsteps / abs(Xsteps))

    pointArr = []

    yPos = C1[1]

    for i in range(Ysteps + 1):
        j = C1[0] - Xdir  # travelling X

        while j != C2[0]:
            j += Xdir
            pointArr.append([j, yPos])
    
        yPos += Ydir

    yPos -= Ydir

    # centralize
    for index in range(len(pointArr)):
        pointArr[index] = [
            pointArr[index][0] - C1[0],
            pointArr[index][1] - C1[1]
        ]

    return object({
        fill:pointArr
    },{
        "z_value": zValue,
        "pos": C1,
        "stayInFrame": stayInFrame,
        "collision": collision
    }) 

def lineObj(C1, C2, fill, zValue, stayInFrame=True,collision=False):
    # this function returns a 'object' which is a line from coord C1 to C2 => coord = [C1, C2]
    # making point array
    Xsteps = C2[0] - C1[0]
    Ysteps = C2[1] - C1[1]

    
    pointArr = []

    if (Xsteps == 0) and (Ysteps != 0):
        # veticle Line
        Ydir = int(Ysteps / abs(Ysteps))
        j = C1[1] - Ydir  # travelling Y
        while j != C2[1]:
            j += Ydir
            pointArr.append([C1[0],j])
    elif (Ysteps == 0) and (Xsteps != 0):
        # horizontal Line
        Xdir = int(Xsteps / abs(Xsteps))
        j = C1[0] - Xdir  # travelling X
        while j != C2[0]:
            j += Xdir
            pointArr.append([j,C1[1]])
    else:
        Xdir = int(Xsteps / abs(Xsteps))
        Ydir = int(Ysteps / abs(Ysteps))

        j = []  # travelling coordinate
        first = True

        while j != C2:
            if first:
                first = False
                j = C1.copy()
                pointArr.append(j)
            else:
                inst_Ysteps = C2[1] - j[1]
                inst_Xsteps = abs(C2[0] - j[0])  # keeping X positive always

                dY = round(inst_Ysteps / inst_Xsteps)

                j = [j[0] + Xdir, j[1]]
                if abs(dY) == 0:
                    pointArr.append(j)
                for c in range(abs(dY)):
                    j = [j[0], j[1] + Ydir]
                    pointArr.append(j)
    
    # centralize
    for index in range(len(pointArr)):
        pointArr[index] = [
            pointArr[index][0] - C1[0],
            pointArr[index][1] - C1[1]
        ]
    
    return object({
        fill:pointArr
    },{
        "z_value": zValue,
        "pos": C1,
        "stayInFrame": stayInFrame,
        "collision": collision
    })

def getKeyState(key):
    # returns True if th stated key is presssed
    if keyboard.is_pressed(key): # if key 'q' is pressed
        return True
    return False


objArr = [] # a list of all objects that exist on screen (only objects in this list will be rendered)
end = False # make it True when the game has ended will end the code
once = True # breaker
timeGone = 0 # time Gone
currTime = time.time()
deltaTime = 0
scoreLeft = 0
scoreRight = 0
health = 0
leftColor = "#ff0000"
rightColor = "#00ff00"
healthLeft = 0
healthRight = 0
fps = 30
targetDt = 1 / fps
frameTime = 0
mainMatrix = []

# LIFE can be in range [0, 5]
# ================================================================================================
gameChoice = None
callHome = True
beginTimer = False
beginGame = False
displayScore = False
counter = 0
titleCounter = 0
titleDisplayed = False
debugCounter = 0

# =================================================================================================
snakeArr = []
applePos = []
snakeMove = []
snakeAppleAloneTime = 0
snakeAppleEscape = 5
introsnake  = object({
"#4ddb0f": [[0,0], [1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0], [10,0], [11,0], [12,0], [13,0], [14,0], [15,0], [16,0], [17,0], [18,0], [19,0], [20,0],
            [0,1], [1,1], [2,1], [3,1], [4,1], [5,1], [6,1], [7,1], [8,1], [9,1], [10,1], [11,1], [12,1], [13,1], [14,1], [15,1], [16,1], [17,1], [18,1], [19,1], [20,1],
            [-1,-1],[-2, -2],[-2,-1],[-3,-1],[-3,0],[-4,0],[-1,1],[-2,1],[-3,1],[-4,1],[-1,2],[-2,2],[-3,2],[-2,3]],
"#205907": [[0,-1], [1,-1], [2,-1], [3,-1], [4,-1], [5,-1], [6,-1], [7,-1], [8,-1], [9,-1], [10,-1], [11,-1], [12,-1], [13,-1], [14,-1], [15,-1], [16,-1], [17,-1], [18,-1], [19,-1],[-1,-2]],
"#92fc65": [[0,2], [1,2], [2,2], [3,2], [4,2], [5,2], [6,2], [7,2], [8,2], [9,2], [10,2], [11,2], [12,2], [13,2], [14,2], [15,2], [16,2], [17,2], [18,2], [19,2], [20,1], [-1,3]],
"#f5f5f5": [[-1,0]],
"#000000": [[-2,0]]
},
{
    "z_value": 6,
    "pos": [20,8],
    "stayInFrame": False,
    "collision" : False
})
introsnake1  = object({
"#4ddb0f": [[0,0], [-1,0], [-2,0], [-3,0], [-4,0], [-5,0], [-6,0], [-7,0], [-8,0], [-9,0], [-10,0], [-11,0], [-12,0], [-13,0], [-14,0], [-15,0], [-16,0], [-17,0], [-18,0], [-19,0], [-20,0],
            [0,1], [-1,1], [-2,1], [-3,1], [-4,1], [-5,1], [-6,1], [-7,1], [-8,1], [-9,1], [-10,1], [-11,1], [-12,1], [-13,1], [-14,1], [-15,1], [-16,1], [-17,1], [-18,1], [-19,1], [-20,1],
            [1,-1],[2, -2],[2,-1],[3,-1],[3,0],[4,0],[1,1],[2,1],[3,1],[4,1],[1,2],[2,2],[3,2],[2,3]],
"#205907": [[0,-1], [-1,-1], [-2,-1], [-3,-1], [-4,-1], [-5,-1], [-6,-1], [-7,-1], [-8,-1], [-9,-1], [-10,-1], [-11,-1], [-12,-1], [-13,-1], [-14,-1], [-15,-1], [-16,-1], [-17,-1], [-18,-1], [-19,-1], [1,-2]],
"#92fc65": [ [0,2], [-1,2], [-2,2], [-3,2], [-4,2], [-5,2], [-6,2], [-7,2], [-8,2], [-9,2], [-10,2], [-11,2], [-12,2], [-13,2], [-14,2], [-15,2], [-16,2], [-17,2], [-18,2], [-19,2], [-20,1], [1,3]],
"#f5f5f5": [[1,0]],
"#000000": [[2,0]]
},
{
    "z_value": 6,
    "pos": [0,20],
    "stayInFrame": False,
    "collision" : False
})
introsnake2  = object({
"#4ddb0f": [[0,0], [1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0], [10,0], [11,0], [12,0], [13,0], [14,0], [15,0], [16,0], [17,0], [18,0], [19,0], [20,0],
            [0,1], [1,1], [2,1], [3,1], [4,1], [5,1], [6,1], [7,1], [8,1], [9,1], [10,1], [11,1], [12,1], [13,1], [14,1], [15,1], [16,1], [17,1], [18,1], [19,1], [20,1],
            [-1,-1],[-2, -2],[-2,-1],[-3,-1],[-3,0],[-4,0],[-1,1],[-2,1],[-3,1],[-4,1],[-1,2],[-2,2],[-3,2],[-2,3]],
"#205907": [[0,-1], [1,-1], [2,-1], [3,-1], [4,-1], [5,-1], [6,-1], [7,-1], [8,-1], [9,-1], [10,-1], [11,-1], [12,-1], [13,-1], [14,-1], [15,-1], [16,-1], [17,-1], [18,-1], [19,-1],[-1,-2]],
"#92fc65": [[0,2], [1,2], [2,2], [3,2], [4,2], [5,2], [6,2], [7,2], [8,2], [9,2], [10,2], [11,2], [12,2], [13,2], [14,2], [15,2], [16,2], [17,2], [18,2], [19,2], [20,1], [-1,3]],
"#f5f5f5": [[-1,0]],
"#000000": [[-2,0]]
},
{
    "z_value": 6,
    "pos": [25,30],
    "stayInFrame": False,
    "collision" : False
})
SnakeHead = object({"#013220":[[0,0]]},
            {"z_value": 5,
            "pos": [10,35],
            "stayInFrame": True,
            "collision" : True
            })



SnaTxt1 = txtObj("SNA", [4,13], "#034d04", 5, False)
SnaTxt2 = txtObj("KE", [6, 19], "#034d04", 5, False)
backgro2  = rectangleObj([0,0],[19,39], "#f5f75e", 1)


# =================================================================================================
pongPaddleT = None
attPaddle = None
pongBall = None
pongPowerUp = None
pongOnce = None
pongBallVel = None
pongBreakTimer = None
pongEnd = None
backgro1  = rectangleObj([0,0],[19,39], "#034d04", 1)
# =================================================================================================
attPaddle = None
attBall = None
attOnce = None
attBallVel = None

# =================================================================================================
spcOnce = None
spcGun = None
spcGunPos = None
spcBs = None
spcKeyReg = None
spcKeyChoice = None
spcKeys = None

count = 0
countm= 0
flagc = 0
obj1 = None
obj2 = None
text = None
Index = None
life = 3
GameFlag = 1
Gf3 = 1
Gf2 = 1
Gf1 = 1
Gf0 = 1
score = 0
scoreflag  =1
endflag = 1

# ====================================================================================
targetonce = None
game_over_gyro = None
count = 0
game_time = 60
targets_hit = []
targets_missed = []
target_timer = 4
game_start_time = 0
target_spawn_time = 0
crosshair = object({
    "#ffffff": [[-1,0],[1,0],[0,1],[0,-1],[0,0]], #if i want them to have same color, put them in the same line, if i want different color, different line
    },
    {
        "z_value": 2,
        "pos": [11,25],
        "collision" : True,
        "stayInFrame": True
    })
target = object({
    "#ff0000": [[2,0],[2,1],[2,2],[2,-1],[2,-2],[1,2],[1,-2],[0,2],[0,-2],[-1,2],[-1,-2],[-2,2],[-2,1],[-2,0],[-2,-1],[-2,-2]],
    "#ffff00": [[0,0]],
    "#eb9e34": [[1,0],[1,1],[0,1],[0,-1],[-1,-1],[1,-1],[-1,1],[-1,0]]
    },
    {
        "z_value": 1,
        "pos": [random.randint(1,18),random.randint(4,38)],
        "collision" : True
    })
obj3 = rectangleObj([0,0],[19,39], fill=None,zValue=3,stayInFrame=True, collision=True)

#ser = None
speedupgame=2 #speed up game every n successful hits 
score_addr = 50
score_subtr = 25
calibrate = [0,0] 
values =[]
gun_distance = 40 #trial and error se nikalo
hit_locations = [[1,0],[1,1],[0,1],[0,-1],[-1,-1],[1,-1],[-1,1],[-1,0],[0,0]]
clean_input = True




bs1 = object({ #battleship
    "#021ed4": [[0,-1], [0,-2]], #red
    "#7b1ff2": [[0,1]], #grey
    "#367beb": [[0,0]], #og
    "#3f3cfa": [[-1,0],[1,0]], #dark blue
    "#005285": [[-1,1],[1,1],[-1,2],[1,2]] #boosters
    },
    {
        "z_value": 5,
        "pos": [10,37],
        "collision" : True,
        "stayInFrame": True
    })
obj2 = object({  #bullet
    "#ff8a05": [[0,2]], #Orange1
    "#ff3b05": [[0,1]], #Orange2
    "#7a0000": [[0,0]] #Red]
    },
    {
        "z_value": 4,
        "pos": [15,-15],
        "collision" : True
    })
obj3 = object({  #bullet
    "#ff8a05": [[0,2]], #Orange1
    "#ff3b05": [[0,1]], #Orange2
    "#7a0000": [[0,0]] #Red]
    },
    {
        "z_value": 4,
        "pos": [9,9],
        "collision" : True
    })
obj4 = object({  #bullet
    "#ff8a05": [[0,2]], #Orange1
    "#ff3b05": [[0,1]], #Orange2
    "#7a0000": [[0,0]] #Red]
    },
    {
        "z_value": 4,
        "pos": [4,2],
        "collision" : True
    })
obj5 = object({  #bullet
    "#ff8a05": [[0,2]], #Orange1
    "#ff3b05": [[0,1]], #Orange2
    "#7a0000": [[0,0]] #Red]
    },
    {
        "z_value": 4,
        "pos": [8,-7],
        "collision" : True
    })
obj6 = object({  #bullet
    "#ff8a05": [[0,2]], #Orange1
    "#ff3b05": [[0,1]], #Orange2
    "#7a0000": [[0,0]] #Red]
    },
    {
        "z_value": 4,
        "pos": [17, 0],
        "collision" : True
    })

bul1 = object({  #bullet
    "#028000": [[0,-1]],
    "#0eff0a": [[0,0]] #Bullet
    },
    {
        "z_value": 3,
        "pos": [bs1.curr_pos[0],bs1.curr_pos[1] -3],
        "collision" : True
    })
bul2 = object({  #bullet
    "#028000": [[0,-1]],
    "#0eff0a": [[0,0]] #Bullet
    },
    {
        "z_value": 3,
        "pos": [bs1.curr_pos[0],bs1.curr_pos[1] +4],
        "collision" : True
    })
bul3 = object({  #bullet
    "#028000": [[0,-1]],
    "#0eff0a": [[0,0]] #Bullet
    },
    {
        "z_value": 3,
        "pos": [bs1.curr_pos[0],bs1.curr_pos[1] +11],
        "collision" : True
    })
heart1  = object({  #heart
    "#f2022a": [[-1, -1], [1, -1] ],
    "#a32603": [[1, 0], [0, 1]],
    "#f777aa": [[0, 0], [-1, 0]]
    },
    {
        "z_value": 6,
        "pos": [9, 2],
        "collision" : True
    })
heart2  = object({  #heart
    "#f2022a": [[-1, -1], [1, -1] ],
    "#a32603": [[1, 0], [0, 1]],
    "#f777aa": [[0, 0], [-1, 0]]
    },
    {
        "z_value": 6,
        "pos": [13, 2],
        "collision" : True
    })
heart3  = object({  #heart
    "#f2022a": [[-1, -1], [1, -1] ],
    "#a32603": [[1, 0], [0, 1]],
    "#f777aa": [[0, 0], [-1, 0]]
    },
    {
        "z_value": 6,
        "pos": [17, 2],
        "collision" : True
    })
Mon1  = object({  #design
    "#78d7ff": [[0,0], [-1,0], [-2,0], [-3,0], [1, 0], [2,0], [3,0],[0,-1], [1, -1], [2, -1], [-1,-1], [-2,-1],
                [-2,-2], [1,-2], [-3,-3], [0,-3], [0,1], [-3,1], [-4,1], [3,1], [0,2],[-1,2], [-2,2], [-3,2], [1,2], [2,2], [3,2], [4,2],
                    [-2,3], [1,3], [4,3], [-4,1], [-6,1], [-7,1], [-9,1], [-10,1],
                    [0,4], [-3,4], [-5,4], [-7,4], [-9, 4], [3,4]  ],
    "#f0c297": [[-2,1], [1,1]],
    "#1a466b": [[-1,1], [2,1]]
    },
    {
        "z_value": 3,
        "pos": [-35, 21],
        "collision" : False
    })
Mon2  = object({  #design
    "#3dff6e": [[0,0], [-3,0], [3,0], [0,-1], [-1,-1], [-2,-1], [-3,-1], [1,-1], [2,-1], [3,-1], [-1,-2], [-2,-2], [1,-2], [2,-2],
                [-1,-3], [1,-3], [0,1], [-1,1], [-2,1], [-3,1], [-4,1], [1,1], [2,1], [3,1], [4,1], [-2,2], [2,2],
                [-4,2], [4,2], [-4,3], [4,3], [-1,3], [1,3], [6,1], [7,1], [6,3], [8,3]],
    "#0e0f2c": [[-2,0], [1,0]],
    "#78d7ff": [[-1,0], [2,0]]
    },
    {
        "z_value": 3,
        "pos": [55, 10],
        "collision" : False
    })
Mon3  = object({  #design
    "#f5a15d": [[0,0], [-2,0], [2,0], [0,1], [-1,1], [-2,1], [1,1], [2,1], [0,-1], [-1,-1], [-2,-1], [1,-1], [2,-1], [-4,-1], [4,-1], [-2,-2], [2, -2], 
                [0,-3], [-4,-3], [4,-3], [0,-4], [-2,-4], [2,-4], [-2,-5], [2,-5], [-4,-5], [4,-5], [-4,-6], [4,-6], [-2,-7], [2,-7], [-4,-8], [4,-8]],
    "#c6d831": [[0,2], [-1,2], [1,2], [0,3], [-3,0], [3,0], [-3,-1], [3,-1], [-3,-2], [3,-2], [-4,-2], [4,-2], [-1,-4], [1,-4]],
    "#401102": [[-1,0], [1,0]]
    },
    {
        "z_value": 3,
        "pos": [9, -50],
        "collision" : False
    })
backg = rectangleObj([0,0], [19,4], "#e28df7", 1 )
backgro5  = rectangleObj([0,4], [19,39], "#e28df7", 1 ) 
line = lineObj([0,5],[20,5], "#7a0000", 1, True)
# line1 = txtObj("G",[1,6],"#c6d831",2,True)
# line2 = txtObj("R",[1,12],"#c6d831",2,True)
# line3 = txtObj("C",[1,18],"#c6d831",2,True)
Space = txtObj("SPACE", [0,-8], "#f002e8", 2, False)
Invader = txtObj("NVDR", [2,-2], "#f002e8", 2, False)

Scoreobj = txtObj(str(score), [1, 0], "#f59905", 6, True)
# =================================================================================================
TETROMINOS = None
COLORS = None
obj_playing = None
tetOnce = None
shape_color = None
shape_playing = None
playing = None
filled_pixels = None
Game_Over = None
count = None
obj1 = None
obj2 = None
obj3 = None
line_filled = None
Last_Empty_Line = None
transformed_matrix = None


def updateScoreHeader():

    global objArr, leftColor, scoreLeft, healthLeft, rightColor, scoreRight, healthRight

    # Displaying health

    if scoreLeft + scoreRight > 0:

        for i in range(healthLeft):
            lifeItem = object({
                leftColor : [[0,0]]
            }, {
                "z_value" : 100,
                "pos" : [i*2, 2],
                "stayInFrame" : False,
                "collision" : False,
                "rotation" : False
            })
            objArr.append(lifeItem)
        
        for i in range(healthRight):
            lifeItem = object({
                rightColor : [[0,0]]
            }, {
                "z_value" : 100,
                "pos" : [19 - i*2, 2],
                "stayInFrame" : False,
                "collision" : False,
                "rotation" : False
            })
            objArr.append(lifeItem)
        
        # Displaying Score
        
        binScoreL = str(bin(scoreLeft))[2:]
        binScoreR = str(bin(scoreRight))[2:]

        scoreArray = []
        unScoreArray = []
        for i in range(len(binScoreL)):
            if (i%2)==0:
                if binScoreL[i] == "1":
                    scoreArray.append([int(i/2),0])
                else:
                    unScoreArray.append([int(i/2),0])
            else:
                if binScoreL[i] == "1":
                    scoreArray.append([int((i-1)/2),1])
                else:
                    unScoreArray.append([int((i-1)/2),1])

        for i in range(len(binScoreR)):
            if (i%2)==0:
                if binScoreR[i] == "1":
                    scoreArray.append([19-int(i/2),0])
                else:
                    unScoreArray.append([19-int(i/2),0])
            else:
                if binScoreR[i] == "1":
                    scoreArray.append([19-int((i-1)/2),1])
                else:
                    unScoreArray.append([19-int((i-1)/2),1])

        scoreObj = object({
            "#dddddd" : scoreArray,
            "#444444" : unScoreArray
        }, {
            "z_value" : 100,
            "pos" : [0,0],
            "stayInFrame" : False,
            "collision" : False,
            "rotation" : False
        })
        objArr.append(scoreObj)

def home():
    global gameChoice
    global callHome
    global once, beginTimer, beginGame, displayScore, counter, titleCounter
    global titleDisplayed, objArr, background, scoreLeft, scoreRight, targetDt

    global snakeArr, applePos, snakeMove, snakeAppleAloneTime, snakeAppleEscape
    global pongPaddleT, attPaddle, pongBall, pongPowerUp, pongOnce, pongBallVel, pongBreakTimer, pongEnd
    global attPaddle, attBall, attOnce, attBallVel, attStage
    global spcGunPos, spcOnce, spcBs, spcKeyReg, spcKeyChoice
    global TETROMINOS, COLORS, obj_playing, tetOnce, shape_color, shape_playing, playing, filled_pixels, Game_Over
    global count, obj1, obj2, obj3, line_filled, Last_Empty_Line, transformed_matrix
    global count, countm, flagc , obj1, obj2, text, Index, life , GameFlag , Gf3 , Gf2 , Gf1 , Gf0 , score, scoreflag, endflag

    objArr.clear()
    background = "#000000"

    screenColorData1 = {"#302c2e": [[0, 0], [0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0], [8, 0], [9, 0], [10, 0], [11, 0], [12, 0], [13, 0], [14, 0], [15, 0], [16, 0], [17, 0], [18, 0], [19, 0], [0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1], [6, 1], [7, 1], [8, 1], [9, 1], [10, 1], [11, 1], [12, 1], [13, 1], [14, 1], [15, 1], [16, 1], [17, 1], [18, 1], [19, 1], [0, 2], [1, 2], [2, 2], [3, 2], [4, 2], [5, 2], [6, 2], [7, 2], [8, 2], [9, 2], [10, 2], [11, 2], [12, 2], [13, 2], [14, 2], [15, 2], [16, 2], [17, 2], [18, 2], [19, 2], [0, 3], [1, 3], [2, 3], [3, 3], [4, 3], [5, 3], [6, 3], [7, 3], [8, 3], [9, 3], [10, 3], [11, 3], [12, 3], [13, 3], [14, 3], [15, 3], [16, 3], [17, 3], [18, 3], [19, 3], [0, 4], [1, 4], [2, 4], [3, 4], [4, 4], [5, 4], [6, 4], [7, 4], [8, 4], [9, 4], [10, 4], [11, 4], [12, 4], [13, 4], [14, 4], [15, 4], [16, 4], [17, 4], [18, 4], [19, 4], [0, 5], [1, 5], [2, 5], [3, 5], [4, 5], [5, 5], [6, 5], [7, 5], [8, 5], [9, 5], [10, 5], [11, 5], [12, 5], [13, 5], [14, 5], [15, 5], [16, 5], [17, 5], [18, 5], [19, 5], [0, 6], [1, 6], [2, 6], [3, 6], [4, 6], [5, 6], [6, 6], [7, 6], [8, 6], [9, 6], [10, 6], [11, 6], [12, 6], [13, 6], [14, 6], [15, 6], [16, 6], [17, 6], [18, 6], [19, 6], [0, 7], [1, 7], [2, 7], [3, 7], [4, 7], [5, 7], [6, 7], [7, 7], [8, 7], [9, 7], [10, 7], [11, 7], [12, 7], [13, 7], [14, 7], [15, 7], [16, 7], [17, 7], [18, 7], [19, 7], [0, 8], [1, 8], [2, 8], [3, 8], [4, 8], [5, 8], [6, 8], [7, 8], [8, 8], [9, 8], [10, 8], [11, 8], [12, 8], [13, 8], [14, 8], [15, 8], [16, 8], [17, 8], [18, 8], [19, 8], [12, 20], [4, 22], [6, 26], [8, 26]], "#28ccdf": [[0, 9], [1, 9], [2, 9], [3, 9], [4, 9], [5, 9], [6, 9], [7, 9], [8, 9], [9, 9], [10, 9], [11, 9], [12, 9], [13, 9], [14, 9], [15, 9], [16, 9], [17, 9], [18, 9], [19, 9], [1, 12], [16, 15], [17, 15], [18, 15], [18, 16], [16, 17], [17, 17], [18, 17], [16, 18], [16, 19], [17, 19], [18, 19], [16, 25], [16, 26], [16, 27], [18, 27], [16, 28], [17, 28], [18, 28], [18, 29], [16, 35], [17, 35], [18, 35], [16, 36], [16, 37], [17, 37], [18, 37], [16, 38], [18, 38], [16, 39], [17, 39], [18, 39]], "#eea160": [[0, 10], [1, 10], [2, 10], [3, 10], [4, 10], [5, 10], [6, 10], [7, 10], [8, 10], [13, 10], [14, 10], [15, 10], [17, 10], [18, 10], [19, 10], [2, 11], [3, 11], [4, 11], [5, 11], [6, 11], [7, 11], [8, 11], [9, 11], [12, 11], [13, 11], [14, 11], [17, 11], [18, 11], [19, 11], [0, 12], [4, 12], [7, 12], [8, 12], [13, 12], [14, 12], [15, 12], [17, 12], [18, 12], [19, 12], [2, 13], [3, 13], [4, 13], [5, 13], [6, 13], [7, 13], [8, 13], [10, 13], [11, 13], [13, 13], [14, 13], [15, 13], [17, 13], [18, 13], [19, 13], [0, 14], [1, 14], [2, 14], [3, 14], [4, 14], [5, 14], [6, 14], [7, 14], [8, 14], [9, 14], [10, 14], [11, 14], [12, 14], [13, 14], [14, 14], [18, 14], [19, 14]], "#f47e1b": [[9, 10], [12, 10], [10, 11], [11, 11], [9, 12], [12, 12], [9, 13], [12, 13], [9, 20], [8, 21], [10, 21], [7, 22], [11, 22], [8, 23], [10, 23], [9, 24], [6, 31], [7, 31], [7, 32], [7, 33]], "#39314b": [[10, 10]], "#cfc6b8": [[11, 10]], "#3978a8": [[16, 10], [0, 11], [1, 11], [15, 11], [16, 11], [16, 12], [0, 13], [1, 13], [16, 13], [15, 14], [16, 14], [17, 14], [15, 20], [16, 20], [17, 20], [17, 21], [16, 22], [17, 22], [17, 23], [15, 24], [16, 24], [17, 24], [15, 30], [16, 30], [17, 30], [15, 31], [15, 32], [16, 32], [17, 32], [17, 33], [15, 34], [16, 34], [17, 34]], "#394778": [[2, 12], [3, 12]], "#71aa34": [[5, 12], [0, 17], [1, 17], [2, 17], [6, 34], [7, 34], [8, 34], [9, 34]], "#397b44": [[6, 12], [3, 17]], "#f4b41b": [[10, 12], [11, 12], [9, 21], [8, 22], [10, 22], [9, 23], [0, 30], [1, 30], [1, 31], [2, 31], [0, 36], [13, 36], [0, 37], [13, 37], [0, 38], [13, 38]], "#ebbea8": [[0, 15], [1, 15], [2, 15], [3, 15], [4, 15], [5, 15], [6, 15], [7, 15], [8, 15], [9, 15], [10, 15], [11, 15], [12, 15], [13, 15], [14, 15], [15, 15], [19, 15], [0, 16], [1, 16], [2, 16], [3, 16], [4, 16], [5, 16], [6, 16], [7, 16], [8, 16], [9, 16], [10, 16], [11, 16], [12, 16], [13, 16], [14, 16], [15, 16], [16, 16], [17, 16], [19, 16], [4, 17], [5, 17], [6, 17], [7, 17], [8, 17], [9, 17], [10, 17], [11, 17], [12, 17], [13, 17], [14, 17], [15, 17], [19, 17], [0, 18], [1, 18], [2, 18], [3, 18], [4, 18], [5, 18], [6, 18], [7, 18], [8, 18], [9, 18], [10, 18], [11, 18], [12, 18], [13, 18], [14, 18], [15, 18], [17, 18], [18, 18], [19, 18], [0, 19], [1, 19], [2, 19], [3, 19], [4, 19], [5, 19], [6, 19], [7, 19], [8, 19], [9, 19], [10, 19], [11, 19], [12, 19], [13, 19], [14, 19], [15, 19], [19, 19]], "#f1b5cb": [[0, 20], [1, 20], [2, 20], [3, 20], [4, 20], [5, 20], [6, 20], [7, 20], [8, 20], [10, 20], [11, 20], [13, 20], [14, 20], [18, 20], [19, 20], [0, 21], [1, 21], [2, 21], [4, 21], [6, 21], [7, 21], [12, 21], [14, 21], [15, 21], [16, 21], [18, 21], [19, 21], [0, 22], [1, 22], [2, 22], [3, 22], [5, 22], [6, 22], [12, 22], [13, 22], [14, 22], [15, 22], [18, 22], [19, 22], [0, 23], [1, 23], [2, 23], [4, 23], [6, 23], [7, 23], [11, 23], [12, 23], [13, 23], [14, 23], [15, 23], [16, 23], [18, 23], [19, 23], [0, 24], [1, 24], [2, 24], [3, 24], [4, 24], [5, 24], [6, 24], [7, 24], [8, 24], [10, 24], [11, 24], [12, 24], [13, 24], [14, 24], [18, 24], [19, 24]], "#7d7071": [[3, 21], [5, 21], [11, 21], [13, 21], [3, 23], [5, 23]], "#b6d53c": [[9, 22]], "#e2a0ff": [[0, 25], [1, 25], [2, 25], [3, 25], [4, 25], [5, 25], [7, 25], [9, 25], [10, 25], [11, 25], [12, 25], [13, 25], [14, 25], [15, 25], [17, 25], [18, 25], [19, 25], [0, 26], [1, 26], [2, 26], [3, 26], [4, 26], [10, 26], [11, 26], [12, 26], [13, 26], [14, 26], [15, 26], [17, 26], [18, 26], [19, 26], [0, 27], [1, 27], [2, 27], [3, 27], [11, 27], [12, 27], [13, 27], [14, 27], [15, 27], [17, 27], [19, 27], [0, 28], [1, 28], [2, 28], [3, 28], [4, 28], [5, 28], [9, 28], [10, 28], [11, 28], [12, 28], [13, 28], [14, 28], [15, 28], [19, 28], [0, 29], [1, 29], [2, 29], [3, 29], [4, 29], [6, 29], [8, 29], [10, 29], [11, 29], [12, 29], [13, 29], [14, 29], [15, 29], [16, 29], [17, 29], [19, 29]], "#a93b3b": [[6, 25], [8, 25], [5, 26], [9, 26], [4, 27], [10, 27], [6, 28], [8, 28], [5, 29], [7, 29], [9, 29], [3, 32], [4, 32], [3, 33], [4, 33]], "#e6482e": [[7, 26], [5, 27], [6, 27], [7, 27], [8, 27], [9, 27], [7, 28]], "#16db93": [[2, 30], [3, 30], [4, 30], [5, 30], [6, 30], [7, 30], [8, 30], [9, 30], [10, 30], [11, 30], [12, 30], [13, 30], [14, 30], [18, 30], [19, 30], [0, 31], [3, 31], [4, 31], [5, 31], [8, 31], [9, 31], [10, 31], [12, 31], [13, 31], [14, 31], [16, 31], [17, 31], [18, 31], [19, 31], [0, 32], [1, 32], [2, 32], [5, 32], [6, 32], [8, 32], [9, 32], [13, 32], [14, 32], [18, 32], [19, 32], [0, 33], [1, 33], [2, 33], [5, 33], [6, 33], [8, 33], [9, 33], [10, 33], [11, 33], [12, 33], [13, 33], [14, 33], [15, 33], [16, 33], [18, 33], [19, 33], [0, 34], [1, 34], [2, 34], [3, 34], [4, 34], [5, 34], [10, 34], [11, 34], [12, 34], [13, 34], [14, 34], [18, 34], [19, 34]], "#8e478c": [[11, 31], [10, 32], [11, 32], [12, 32]], "#9b6a6c": [[0, 35], [1, 35], [2, 35], [3, 35], [4, 35], [5, 35], [6, 35], [7, 35], [8, 35], [9, 35], [10, 35], [11, 35], [12, 35], [13, 35], [14, 35], [15, 35], [19, 35], [1, 36], [2, 36], [3, 36], [4, 36], [5, 36], [6, 36], [7, 36], [8, 36], [9, 36], [10, 36], [11, 36], [12, 36], [14, 36], [15, 36], [17, 36], [18, 36], [19, 36], [1, 37], [2, 37], [3, 37], [4, 37], [5, 37], [6, 37], [7, 37], [8, 37], [9, 37], [10, 37], [11, 37], [12, 37], [14, 37], [15, 37], [19, 37], [1, 38], [3, 38], [4, 38], [5, 38], [6, 38], [7, 38], [8, 38], [9, 38], [10, 38], [11, 38], [12, 38], [14, 38], [15, 38], [17, 38], [19, 38], [0, 39], [1, 39], [2, 39], [3, 39], [4, 39], [5, 39], [6, 39], [7, 39], [8, 39], [9, 39], [10, 39], [11, 39], [12, 39], [13, 39], [14, 39], [15, 39], [19, 39]], "#ffaeb6": [[2, 38]]}

    homeScreen = object(screenColorData1, {
        "z_value": 0,
        "pos": [0,0]
    })

    # objArr.append(homeScreen)
    
    
    targetonce = True
    once = True
    gameChoice = 6
    callHome = False
    targetDt = 1 / 30

    if gameChoice is not None:
        once = True
        beginTimer = False
        beginGame = False
        displayScore = False
        counter = 1
        titleCounter = 0
        titleDisplayed = False
        scoreLeft = 0
        scoreRight = 0

def demoGame():

    def countDown(num):

        # A demo count down characters have been made, can be changed as per needs

        global objArr

        num = int(num)

        if (num > 3) or (num < 0):
            raise Exception("time out of range")
        
        objArr.clear()

        if num == 3:
            countObj = txtObj("3",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 2:
            countObj = txtObj("2",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 1:
            countObj = txtObj("1",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        else:
            countObj = txtObj("GO",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        

    # variable access
    global objArr, deltaTime, once, beginTimer, counter, beginGame, displayScore
    global gameChoice, callHome, titleCounter, titleDisplayed, debugCounter
    global leftColor, rightColor, scoreLeft, scoreRight, healthLeft, healthRight

    if once:
        if not titleDisplayed:
            print("game 1 now playing")
            # Game initialization
            objArr.clear()
            once = True

            # this is your title : make exactly one object that comprises of your entire title screen
            game1Title = txtObj("T",[9,17],"#ffff00",1,True,False)

            objArr.append(game1Title)

            print("Timer begins")

            titleDisplayed = True
        else:
            titleCounter += deltaTime
            if titleCounter >= 1:
                once = False
                beginTimer = True
    elif beginTimer:
        counter -= deltaTime
        
        if counter <= 0:
            beginTimer = False
            beginGame = True
            objArr.clear()
        elif counter <= 0.1:
            countDown(1)
        elif counter <= 0.4:
            countDown(2)
        elif counter >= 0.7:
            countDown(3)
    elif beginGame:

        def endGame():
            global beginGame, displayScore, counter
            # Call this function to end game
            beginGame = False
            displayScore = True
            counter = 0
        
        objArr.clear()
        
        # GAME HERE
        
        updateScoreHeader()
        debugCounter += deltaTime

        print("GAME RUNNING")

        scoreLeft += 2
        scoreRight += 1

        if debugCounter > 360:
            endGame()
    else:
        if displayScore:
            objArr.clear()

            # display score here
            print("SCORE")

            displayScore = False
        else:
            counter += deltaTime

            if counter >= 5:
                gameChoice = None
                callHome = True
                print("OVER :(")

def game1():
    # TETRIS

    def countDown(num):

        # A demo count down characters have been made, can be changed as per needs

        global objArr

        num = int(num)

        if (num > 3) or (num < 0):
            raise Exception("time out of range")
        
        objArr.clear()
        
        objArr.append(backgro1)

        if num == 3:
            countObj = txtObj("3",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 2:
            countObj = txtObj("2",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 1:
            countObj = txtObj("1",[9,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        else:
            countObj = txtObj("GO",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        

    # variable access
    global objArr, deltaTime, once, beginTimer, counter, beginGame, displayScore
    global gameChoice, callHome, titleCounter, titleDisplayed, debugCounter
    global leftColor, rightColor, scoreLeft, scoreRight, healthLeft, healthRight

    global TETROMINOS, COLORS, tetOnce, obj_playing, shape_color, shape_playing, count, obj1, obj2, obj3, tetris1, tetris2, backgro1
    global line_filled, Last_Empty_Line, filled_pixels, transformed_matrix, gameFlag, introrect, introcube, intro1, intro2, intro3, intro4, intro5, intro6, game_start_time
    gameFlag = 1
    if once:
        if not titleDisplayed:
            print("game 1 now playing")
            # Game initialization
            objArr.clear()
            once = True



            print("Timer begins")

            titleDisplayed = True
        else:
            titleCounter += deltaTime
            if titleCounter >= 1:
                once = False
                beginTimer = True
                game_start_time = time.time()
                tetris1 = txtObj("TET", [3,6], "#ff0505", 3, False)
                tetris2 = txtObj("RIS", [6,12], "#ff0505", 3, False)
                introcube = rectangleObj([13,-3], [24, 0], "#0af7ef", 3, False, False)
                introrect = rectangleObj([3,-3], [14, 0], "#bd8111", 3, False, False)
                intro1 = object({
                    "#bf0fb6": [[0,0],[1,0],[2,0],[3,0],[0,1],[1,1],[2,1],[3,1],[0,2],[1,2],[2,2],[3,2],[0,3], [1,3], [2,3],[3,3],
                                [0,4],[1,4],[2,4],[3,4],[0,5],[1,5],[2,5],[3,5],[0,6],[1,6],[2,6],[3,6],[0,7],[1,7],[2,7],[3,7],
                                [4,4],[5,4],[6,4],[7,4],[4,5],[5,5],[6,5],[7,5],[4,6],[5,6],[6,6],[7,6],[4,7],[5,7],[6,7],[7,7],
                                [8,4],[9,4],[10,4],[11,4],[8,5],[9,5],[10,5],[11,5],[8,6],[9,6],[10,6],[11,6],[8,7],[9,7],[10,7],[11,7]]
                },
                {
                    "z_value": 4,
                    "pos": [4,-13],
                    "collision": False,
                })
                intro2 = object({
                    "#930ddb": [[0,0],[1,0],[2,0],[3,0],[0,1],[1,1],[2,1],[3,1],[0,2],[1,2],[2,2],[3,2],[0,3],[1,3],[2,3],[3,3],
                                [4,0,],[5,0],[6,0],[7,0],[4,1],[5,1],[6,1],[7,1],[4,2],[5,2],[6,2],[7,2],[4,3],[5, 3],[6,3],[7,3],
                                [8,0],[9,0],[10,0],[11,0],[8,1],[9,1],[10,1],[11,1],[8,2],[9,2],[10,2],[11,2],[8,3],[9,3],[10,3],[11,3],
                                [4,4],[5,4],[6,4],[7,4],[4,5],[5,5],[6,5],[7,5],[4,6],[5,6],[6,6],[7,6],[4,7],[5,7],[6,7],[7,7]]
                },
                {
                    "z_value": 4,
                    "pos": [0,-14],
                    "collision": False,
                })
                intro3 = object({
                    "#bd1411": [[0,0],[1,0],[2,0],[3,0],[0,1],[1,1],[2,1],[3,1],[0,2],[1,2],[2,2],[3,2],[0,3], [1,3], [2,3],[3,3], 
                                [0,4], [1,4],[2,4],[3,4],[0,5],[1,5],[2,5],[3,5],[0,6],[1,6],[2,6],[3,6],[0,7],[1,7],[2,7],[3,7],
                            [4,0],[5,0],[6,0],[7,0],[4,1],[5,1],[6,1],[7,1],[4,2],[5,2],[6,2],[7,2],[4,3],[5,3],[6,3],[7,3],
                            [-4,4],[-3,4],[-2,4],[-1,4],[-4,5],[-3,5],[-2,5],[-1,5],[-4,6],[-3,6],[-2,6],[-1,6],[-4,7],[-3,7],[-2,7],[-1,7]]
                },
                {
                    "z_value": 4,
                    "pos": [16,-14],
                    "collision": False,
                })
                intro4 = object({
                    "#583bcc": [[0,0],[1,0],[2,0],[3,0],[0,1],[1,1],[2,1],[3,1],[0,2],[1,2],[2,2],[3,2],[0,3], [1,3], [2,3],[3,3],
                                [0,4],[1,4],[2,4],[3,4],[0,5],[1,5],[2,5],[3,5],[0,6],[1,6],[2,6],[3,6],[0,7],[1,7],[2,7],[3,7],
                                [4,4],[5,4],[6,4],[7,4],[4,5],[5,5],[6,5],[7,5],[4,6],[5,6],[6,6],[6,7],[4,7],[5,7],[6,7],[7,7],
                                [8,4],[9,4],[10,4],[11,4],[8,5],[9,5],[10,5],[11,5],[8,6],[9,6],[10,6],[11,6],[8,7],[9,7],[10,7],[11,7]]
                },
                {
                    "z_value": 4,
                    "pos": [12,-10],
                    "collision": False,
                })
                intro5 = object({
                    "#4acc3b": [[0,0],[1,0],[2,0],[3,0],[0,1],[1,1],[2,1],[3,1],[0,2],[1,2],[2,2],[3,2],[0,3],[1,3],[2,3],[3,3],
                                [4,0,],[5,0],[6,0],[7,0],[4,1],[5,1],[6,1],[7,1],[4,2],[5,2],[6,2],[7,2],[4,3],[5, 3],[6,3],[7,3],
                                [8,0],[9,0],[10,0],[11,0],[8,1],[9,1],[10,1],[11,1],[8,2],[9,2],[10,2],[11,2],[8,3],[9,3],[10,3],[11,3],
                                [4,4],[5,4],[6,4],[7,4],[4,5],[5,5],[6,5],[7,5],[4,6],[5,6],[6,6],[7,6],[4,7],[5,7],[6,7],[7,7]]
                },
                {
                    "z_value": 4,
                    "pos": [3, -11],
                    "collision": False,
                })
                intro6 = object({
                    "#0cb5f2": [[0,0],[1,0],[2,0],[3,0],[0,1],[1,1],[2,1],[3,1],[0,2],[1,2],[2,2],[3,2],[0,3], [1,3], [2,3],[3,3], 
                                [0,4], [1,4],[2,4],[3,4],[0,5],[1,5],[2,5],[3,5],[0,6],[1,6],[2,6],[3,6],[0,7],[1,7],[2,7],[3,7],
                            [4,0],[5,0],[6,0],[7,0],[4,1],[5,1],[6,1],[7,1],[4,2],[5,2],[6,2],[7,2],[4,3],[5,3],[6,3],[7,3],
                            [-4,4],[-3,4],[-2,4],[-1,4],[-4,5],[-3,5],[-2,5],[-1,5],[-4,6],[-3,6],[-2,6],[-1,6],[-4,7],[-3,7],[-2,7],[-1,7]]
                },
                {
                    "z_value": 4,
                    "pos": [9,-2],
                    "collision": False,
                })
                
    elif(currTime-game_start_time <3):
        if gameFlag==1:
            gameFlag=0
            objArr.append(intro1)
            objArr.append(intro2)
            objArr.append(intro3)
            objArr.append(intro4)
            objArr.append(intro5)
            objArr.append(intro6)
            objArr.append(introcube)
            objArr.append(introrect)
            objArr.append(tetris1)
            objArr.append(tetris2)
            
            objArr.append(backgro1)
        offset(intro1, [0,2])
        offset(intro2, [0,3])
        offset(intro3, [0,3])
        offset(intro5, [0,3])
        offset(intro4, [0,4])
        offset(intro6, [0,3])
        offset(introcube,[0,2])
        offset(introrect, [0,3])
        
    elif(currTime-game_start_time >=3 and currTime-game_start_time<4):
        if (gameFlag ==0):
            gameFlag = 1
            objArr.pop(objArr.index(intro1))
            objArr.pop(objArr.index(intro2))
            objArr.pop(objArr.index(intro3))
            objArr.pop(objArr.index(intro4))
            objArr.pop(objArr.index(intro5))
            objArr.pop(objArr.index(intro6))
            objArr.pop(objArr.index(introcube))
            objArr.pop(objArr.index(introrect))
            objArr.pop(objArr.index(tetris1))
            objArr.pop(objArr.index(tetris2))
            print("popped")
    
    elif beginTimer:
        beginTimer = False
        beginGame = True
    elif beginGame:

        def endGame():
            global beginGame, displayScore, counter
            # Call this function to end game
            beginGame = False
            displayScore = True
            counter = 0
        
        def has_collided_with_bottom(obj):
            # Check if the object's bounding box extends beyond the bottom of the screen
            if obj.curr_pos[1] + obj.botPad == 39:
                return True
            else:
                return False
            
        def collided_with_bottom(obj):
            global obj_playing, obj3

            return checkOverlap(obj_playing, [obj.curr_pos[0], obj.curr_pos[1]+1], against=[obj3])
        
        def createTetromino():
            global shape_color, shape_playing
            shape_color = random.randint(0,6)
            shape_playing = list(tuple(TETROMINOS[random.randint(0,6)]))
            # shape_playing = list(tuple(TETROMINOS[-1]))

            obj = object({
                COLORS[shape_color]: shape_playing
            },
            {
                "z_value": 4,
                "pos": [10,4],
                "collision": True,
                "stayInFrame": True,
                "rotation": True
            })
            return obj
        
        def getMatrix():
            global transformed_matrix
            global filled_pixels, obj3
            global COLORS
            global mainMatrix
            grid = obj3.pixelArr.copy()

            transformed_matrix = []
            filled_pixels = grid.copy()
            # Iterate through each row in the input matrix
            for row in grid:
                # Create a new row for the transformed matrix
                transformed_row = []

                # Iterate through each element in the row
                for element in row:
                    # Check if the element is "000000" and replace it with 0, otherwise replace with 1
                    # transformed_element = 0 if element == "#000000" else 1
                    if element not in COLORS:
                        transformed_element = 0
                    else: 
                        transformed_element = 1

                    # Append the transformed element to the transformed row
                    transformed_row.append(transformed_element)

                # Append the transformed row to the transformed matrix
                transformed_matrix.append(transformed_row)
            return transformed_matrix
        
        def checkLineFull(transformed_matrix):
            global line_filled,Last_Empty_Line

            # print(transformed_matrix)
            for sublist in transformed_matrix:
                # Calculate the sum of elements in the sublist
                sublist_sum = sum(sublist)
                # Check if the sum is equal to 20
                if sublist_sum == 20:
                    line_filled = transformed_matrix.index(sublist)
                    print(line_filled)
                    return True
            # If no sublist has a sum equal to 20, return False
            return False
        
        def updateGame():
            global obj_playing, playing, shape_playing, shape_color, filled_pixels, Game_Over, scoreLeft

            
            if (has_collided_with_bottom(obj_playing) or collided_with_bottom(obj_playing)) and not Game_Over:
                # If collision with bottom, spawn a new tetromino
                temp = obj_playing.curr_pos
                # objArr.remove(obj_playing)
                for item in shape_playing:
                    obj3.changeColor([item[0]+temp[0],item[1]+temp[1]],COLORS[shape_color])

                # updateCollision(obj3, obj3.pixelArr)

                while checkLineFull(getMatrix()):
                    i = line_filled
                    while i >= 6:
                        for j in range(0,20):
                            if i == 6:
                                obj3.changeColor([j,i],None)
                            elif filled_pixels[i-1][j] not in COLORS:
                                obj3.changeColor([j,i],None)
                            else:
                                obj3.changeColor([j,i],filled_pixels[i-1][j])
                        i -= 1
                        scoreLeft += 50
                shape_playing = TETROMINOS[random.randint(0,6)]
                newTetromino = createTetromino()
                scoreLeft += 10
                playing = True
                obj_playing = newTetromino
                objArr.append(newTetromino)
                # temp2 = obj_playing.curr_pos
                # offset(obj_playing,[0,3])
                # if temp2 == obj_playing.curr_pos:
                #     Game_Over = True
                #     print("YOOOOOOOOOOOOOOOOOOOOOOOOOOOOOo")
                return False
        
        def Tet_rotate(obj, amt):
            # this function rotates the given 'obj' by 'amt'
            # amt +1 = CCW by 90 degree ; +2 = CCW by 180 degree
            # amt -1 = CW  by 90 degree ; -2 = CW  by 180 degree
            if amt ==-1:
                for i in shape_playing:
                    shape_playing[shape_playing.index(i)] = [-i[1],i[0]]
            elif amt ==1:
                for i in shape_playing:
                    shape_playing[shape_playing.index(i)] = [i[1],-i[0]]
            
            def checkBounds(obj):

                # print(obj.lefPad, obj.rigPad)
                if (obj.curr_pos[0] < 0) or (obj.curr_pos[0] > 19):
                    return False
                if (obj.curr_pos[1] < 0) or (obj.curr_pos[1] > 39):
                    return False
                if obj.curr_pos[0] + obj.rigPad > 19:
                    return False
                if obj.curr_pos[0] - obj.lefPad < 0:
                    return False
                if obj.curr_pos[1] + obj.botPad > 39:
                    return False
                if obj.curr_pos[1] - obj.topPad < 0:
                    return False
                return True
            
            def getNewPixArr():
                mid = obj.rot_mid
                newPixArr = []

                # make empty
                temp = []

                for x in range(len(obj.pixelArr)):
                    temp.append(None)
                for x in range(len(obj.pixelArr)):
                    newPixArr.append(temp.copy())
                
                # iterating through the original Array and making the necessary swaps
                for y in range(len(obj.pixelArr)):
                    for x in range(len(obj.pixelArr)):
                        dX = x - mid
                        dY = y - mid

                        # CCW SWAP
                        if amt < 0:
                            newPixArr[mid + dX][mid - dY] = obj.pixelArr[y][x]
                        else:
                            newPixArr[mid - dX][mid + dY] = obj.pixelArr[y][x] 
                return newPixArr
            
            preservedArr = obj.pixelArr.copy() # save PixArr

            # resolve Rotate
            while amt > 4:
                amt -= 4
            while amt < -4:
                amt += 4
            
            # iterate rotation
            for a in range(abs(amt)):
                newArr = getNewPixArr()

                # checking if this rotation causes collision
                obj.pixelArr = newArr

                coordArr = []
                for y in range(len(newArr)):
                    for x in range(len(newArr)):
                        if newArr[y][x] is not None:
                            coordArr.append([
                                x - obj.rot_mid,
                                y - obj.rot_mid
                            ])

                size = obj.getBoundingBox(coordArr)
                obj.calcPadding()
                obj.calcBoundOrigin(size)

                if checkOverlap(obj, obj.curr_pos, against=[obj3]) or (not checkBounds(obj)):
                    # reverting changes
                    newArr = preservedArr.copy()
                    obj.pixelArr = newArr
                    if amt == -1:
                        for i in shape_playing:
                            shape_playing[shape_playing.index(i)] = [i[1],-i[0]]
                    elif amt == 1:
                        for i in shape_playing:
                            shape_playing[shape_playing.index(i)] = [-i[1],i[0]]
                    # recreating the coord map
                    coordArr = []
                    for y in range(len(newArr)):
                        for x in range(len(newArr)):
                            if newArr[y][x] is not None:
                                coordArr.append([
                                    x - obj.rot_mid,
                                    y - obj.rot_mid
                                ])
                    
                    # recalculating the appropriate variables
                    size = obj.getBoundingBox(coordArr)
                    obj.calcPadding()
                    obj.calcBoundOrigin(size)

                    # breaking the loop
                    break
        
        objArr.clear()
        
        # GAME HERE
        if tetOnce:
            tetOnce = False

            obj3 = rectangleObj([0,0],[19,39], fill=None,zValue=4,stayInFrame=True, collision=True)
            
            obj_playing = createTetromino()
            objArr.append(obj3)
            objArr.append(obj_playing)
        else:
            # print(obj_playing.rigPad)
            if getKeyState('A') and not Game_Over:
                offset(obj_playing, [-1,0], against=[obj3])
            elif getKeyState('D') and not Game_Over:
                offset(obj_playing, [1,0], against=[obj3])
            elif getKeyState('S') and not Game_Over:
                offset(obj_playing, [0,1], against=[obj3])
            elif getKeyState('W') and not Game_Over:
                Tet_rotate(obj_playing, -1)
            else:
                pass
            # print(obj_playing.rigPad)
            gameEnded = False
            emptyCount = 0
            for i in obj3.pixelArr:
                if i.count(None) == 20:
                    emptyCount += 1
            if emptyCount <= 15:
                endGame()
                gameEnded = True

            if not gameEnded:
                updateGame()
                offset(obj_playing, [0,1])

                objArr.append(obj3)
                objArr.append(obj_playing)

        
        
        # print(deltaTime)
        
        updateScoreHeader()
    else:
        if displayScore:
            objArr.clear()

            # display score here
            scoreObj = txtObj("SCORE",[0,14],"#bc4749",5,False,False)
            objArr.append(scoreObj)
            scoreObj = txtObj(str(scoreLeft),[1,21],"#bc4749",5,False,False)
            objArr.append(scoreObj)

            displayScore = False
        else:
            counter += deltaTime

            if counter >= 5:
                gameChoice = None
                callHome = True
                print("OVER :(")
    
    # lol
    objArr.append(backgro1)

def game2():
    # SNAKE
    # created by AYUSH YADAV

    def countDown(num):

        # A demo count down characters have been made, can be changed as per needs

        global objArr

        num = int(num)

        if (num > 3) or (num < 0):
            raise Exception("time out of range")
        
        objArr.clear()

        if num == 3:
            countObj = txtObj("3",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 2:
            countObj = txtObj("2",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 1:
            countObj = txtObj("1",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        else:
            countObj = txtObj("GO",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        

    # variable access
    global objArr, deltaTime, once, beginTimer, counter, beginGame, displayScore
    global gameChoice, callHome, titleCounter, titleDisplayed, debugCounter
    global leftColor, rightColor, scoreLeft, scoreRight, healthLeft, healthRight, introsnake, introsnake1, introsnake2

    global snakeArr, objArr, applePos, snakeMove, snakeAppleAloneTime, snakeAppleEscape, game_start_time, gameFlag
    global backgro2, SnaTxt1, SnaTxt2
    gameFlag = 1
    if once:
        if not titleDisplayed:
            print("game 2 now playing")
            # Game initialization
            objArr.clear()
            once = True

            game_start_time = time.time()

            titleDisplayed = True
        else:
            titleCounter += deltaTime
            if titleCounter >= 1:
                once = False
                beginTimer = True
    elif(currTime-game_start_time <5):
        if gameFlag==1:
            gameFlag=0
            objArr.append(introsnake)
            objArr.append(introsnake1)
            objArr.append(introsnake2)
            objArr.append(SnaTxt1)
            objArr.append(SnaTxt2)
            
            objArr.append(backgro2)
        offset(introsnake, [-1,0])
        offset(introsnake1, [1,0])
        offset(introsnake2, [-1,0])
        
    elif(currTime-game_start_time >=5 and currTime-game_start_time<6):
        if (gameFlag ==0):
            gameFlag = 1
            objArr.pop(objArr.index(introsnake))
            objArr.pop(objArr.index(introsnake1))
            objArr.pop(objArr.index(introsnake2))
            objArr.pop(objArr.index(SnaTxt1))
            objArr.pop(objArr.index(SnaTxt2))
    elif beginTimer:
        counter -= deltaTime
        
        if counter <= 0:
            beginTimer = False
            beginGame = True
            objArr.clear()
        elif counter <= 1:
            countDown(1)
        elif counter <= 2:
            countDown(2)
        elif counter >= 3:
            countDown(3)
    elif beginGame:

        def endGame():
            global beginGame, displayScore, counter
            # Call this function to end game
            beginGame = False
            displayScore = True
            counter = 0
        
        def changeApplePos():

            global applePos, snakeArr

            applePos = [
                random.randint(0,19),
                random.randint(2,39)
            ]

            while applePos in snakeArr:
                applePos = [
                    random.randint(0,19),
                    random.randint(2,39)
                ]
        
        objArr.clear()
        
        # GAME HERE

        if getKeyState("W"):
            if snakeMove != [0, 1]:
                snakeMove = [0, -1]
        elif getKeyState("A"):
            if snakeMove != [1, 0]:
                snakeMove = [-1, 0]
        elif getKeyState("S"):
            if snakeMove != [0, -1]:
                snakeMove = [0, 1]
        elif getKeyState("D"):
            if snakeMove != [-1, 0]:
                snakeMove = [1, 0]
        else:
            pass

        
        nxtPos = [
            snakeArr[0][0] + snakeMove[0],
            snakeArr[0][1] + snakeMove[1]
        ]

        if nxtPos[0] < 0:
            nxtPos[0] += 20
        
        if nxtPos[0] > 19:
            nxtPos[0] -= 20

        if nxtPos[1] < 2:
            nxtPos[1] += 38
        
        if nxtPos[1] > 39:
            nxtPos[1] -= 38

        if (nxtPos in snakeArr) and (nxtPos != snakeArr[0]):
            endGame()
        else:
            if nxtPos == applePos:
                snakeAppleEscape += 0.1
                snakeAppleAloneTime = 0
                newArr = [nxtPos]
                newArr.extend(snakeArr)
                snakeArr = newArr.copy()

                changeApplePos()
            else:
                if len(snakeArr) == 1:
                    snakeArr[0] = nxtPos
                else:
                    newArr = [nxtPos]
                    newArr.extend(snakeArr)
                    snakeArr = newArr[:-1].copy()
        
        if snakeAppleAloneTime >= snakeAppleEscape:
            changeApplePos()
            snakeAppleEscape -= 0.1
            snakeAppleAloneTime = 0
        else:
            snakeAppleAloneTime += deltaTime
        
        if snakeAppleEscape <= 0:
            endGame()
        
        # make the huge pixel square
        snakeObj = rectangleObj([0,0],[19,39],"#ffffff",60,False,False)
        for x in range(20):
            for y in range(40):
                if [x,y] in snakeArr:
                    if [x,y] == snakeArr[0]:
                        snakeObj.changeColor([x,y],"#386641") # head
                    else:
                        snakeObj.changeColor([x,y],"#6a994e") # body
                else:
                    snakeObj.changeColor([x,y],None)
        
        objArr.append(snakeObj)

        appleObj = object({
            "#e94f37" : [[0,0]]
        },{
            "z_value" : 60,
            "pos" : applePos,
            "stayInFrame" : True,
            "collision" : False,
            "rotation" : False
        })

        objArr.append(appleObj)

        scoreLeft = len(snakeArr) * 10
        scoreRight = 0
        healthLeft = 0
        healthRight = 0

        # AESTHATICS
        background = "#a7c957"
        
        updateScoreHeader()
        debugCounter += deltaTime
    else:
        if displayScore:
            objArr.clear()

            # display score here
            scoreObj = txtObj("SCORE",[0,14],"#bc4749",5,False,False)
            objArr.append(scoreObj)
            scoreObj = txtObj(str(scoreLeft),[1,21],"#bc4749",5,False,False)
            objArr.append(scoreObj)

            displayScore = False
        else:
            counter += deltaTime

            if counter >= 5:
                gameChoice = None
                callHome = True
                print("OVER :(")
    objArr.append(backgro2)

def game3():
    # PONG
    # created by ATHARV SALONKHE
    # bug fixes, other significant adjustments by AYUSH YADAV
    
    def countDown(num):

        # A demo count down characters have been made, can be changed as per needs

        global objArr

        num = int(num)

        if (num > 3) or (num < 0):
            raise Exception("time out of range")
        
        objArr.clear()
        objArr.append(backgro)

        if num == 3:
            countObj = txtObj("3",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 2:
            countObj = txtObj("2",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 1:
            countObj = txtObj("1",[9,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        else:
            countObj = txtObj("GO",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        

    # variable access
    global objArr, deltaTime, once, beginTimer, counter, beginGame, displayScore
    global gameChoice, callHome, titleCounter, titleDisplayed, debugCounter, ping, pong
    global leftColor, rightColor, scoreLeft, scoreRight, healthLeft, healthRight, game_start_time, gameFlag

    global pongPaddleT, attPaddle, pongBall, pongPowerUp, pongOnce, pongBallVel, pongBreakTimer, intro1, intro2, backgro
    gameFlag = 1
    if once:
        if not titleDisplayed:
            print("game 1 now playing")
            # Game initialization
            objArr.clear()
            print("cleared")
            once = True

            # this is your title : make exactly one object that comprises of your entire title screen
           

            print("Timer begins")

            titleDisplayed = True
        else:
            titleCounter += deltaTime
            if titleCounter >= 1:
                once = False
                beginTimer = True
                game_start_time = time.time()
                backgro  = rectangleObj([0,0],[19,39], "#9effae", 1)
                intro2 =  object({
                "#0444ba": [[0,0], [1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0],
                            [1,1], [2,1], [3,1], [4,1], [5,1], [6,1], [7,1], [8,1], [9,1],
                            [2,2], [3,2], [4,2], [5,2], [6,2], [7,2], [8,2],
                            [3,3], [4,3], [5,3], [6,3], [7,3], [8,3], 
                            [4,4], [5,4], [6,4],
                            [0,-1], [1,-1], [2,-1], [3,-1], [4,-1], [5,-1], [6,-1], [7,-1], [8,-1], [9,-1], 
                            [0,-2], [1,-2], [2,-2], [3,-2], [4,-2], [5,-2], [6,-2], [7,-2], [8,-2], [9,-2],
                           [0,-3], [1,-3], [2,-3], [3,-3], [4,-3], [5,-3], [6,-3], [7,-3], [8,-3], [9,-3], 
                           [0,-4], [1,-4], [2,-4], [3,-4], [4,-4], [5,-4], [6,-4], [7,-4], [8,-4], [9,-4],
                           [0,-5], [1,-5], [2,-5], [3,-5], [4,-5], [5,-5], [6,-5], [7,-5], [8,-5], 
                           [1,-6], [2,-6], [3,-6], [4,-6], [5,-6], [6,-6], [7,-6], 
                           [2,-7], [3,-7], [4,-7], [5,-7], [6,-7]],
                "#032057": [[1,-7], [0,-6], [-1,-5], [-1,-4], [-1,-3], [-1,-2], [-1,-1], [-1,0], [0,1], [1,2], [2,3], [3,4]],
                "#050101": [[6,-8], [5,-8], [4,-8], [3,-8], [2,-8], [1,-8], [0,-7], [-1,-6], [-2,-5], [-2,-4], [-2,-3], [-2,-2], [-2,-1], [-2,0], [-1,1], [-2,1], 
                            [0,2], [-1,2], [-2,2], [1,3], [0,3], [-1,3], [-2,3], [2,4], [1,4], [0,4], [6,5], [5,5], [4,5], [3,5], [2,5], [1,5], [0,5], 
                            [7,4], [8,4], [9,3], [9,2], [10,1], [10,0], [10,-1], [10,-2], [10,-3], [10,-4], [9,-5], [8,-6], [7,-7]],
                "#ba5604": [[-1,4], [-2,4], [-1,5], [-2,5], [-3,5], [-2,6],[-3,6],[-4,6], [-3,7],[-4,7],[-5,7],[-3,8]]
                },
                {
                    "z_value": 5,
                    "pos": [24,28],
                    "collision": False,
                })
                ping = txtObj("PING", [1,6], "#0ea3e8", 3, False)
                pong = txtObj("PONG", [3,12], "#d4514a", 3, False)
                intro1 = object({
                "#db2525": [[0,0],[-1,0],[-2,0],[-3,0], [-4,0], [-5,0], [-6,0], [-7,0], [-8,0], [-9,0],
                            [-1,1],[-2,1], [-3,1], [-4,1], [-5,1], [-6,1], [-7,1], [-8,1], [-9,1], 
                            [-2,2], [-3,2], [-4,2], [-5,2], [-6,2], [-7,2], [-8,2],
                            [-3,3], [-4,3], [-5,3], [-6,3], [-7,3], [-8,3],
                            [-4,4],[-5,4],[-6,4],
                            [0,-1], [-1,-1], [-2,-1], [-3,-1], [-4,-1], [-5,-1], [-6,-1], [-7,-1], [-8,-1], [-9,-1],
                            [0,-2], [-1,-2], [-2,-2], [-3,-2], [-4,-2], [-5,-2], [-6,-2], [-7,-2], [-8,-2], [-9,-2],
                            [0,-3], [-1,-3], [-2,-3], [-3,-3], [-4,-3], [-5,-3], [-6,-3], [-7,-3], [-8,-3], [-9,-3], 
                            [0,-4], [-1,-4], [-2,-4], [-3,-4], [-4,-4], [-5,-4], [-6,-4], [-7,-4], [-8,-4], [-9,-4], 
                            [0,-5], [-1,-5], [-2,-5], [-3,-5], [-4,-5], [-5,-5], [-6,-5], [-7,-5], [-8,-5],
                            [-1,-6], [-2,-6], [-3,-6], [-4,-6], [-5,-6], [-6,-6], [-7,-6],
                            [-2,-7], [-3,-7], [-4,-7], [-5,-7], [-6,-7]],
                "#631111": [[-1,-7],[0,-6],[1,-5],[1,-4],[1,-3],[1,-2],[1,-1],[1,0],[0,1],[-1,2],[-2,3],[-3,4]],
                "#050101": [[-6,-8],[-5,-8],[-4,-8],[-3,-8],[-2,-8],[-1,-8],[0,-7],[1,-6],[2,-5],[2,-4],[2,-3],[2,-2],[2,-1],[2,0],[1,1],[2,1],
                            [0,2],[1,2],[2,2],[-1,3],[0,3],[1,3],[2,3],[-2,4],[-1,4],[0,4],[-6,5],[-5,5],[-4,5],[-3,5],[-2,5],[-1,5],[0,5],
                            [-7,4],[-8,4],[-9,3],[-9,2],[-10,1],[-10,0],[-10,-1],[-10,-2],[-10,-3],[-10,-4],[-9,-5],[-8,-6],[-7,-7]],
                "#ba5604": [[1,4],[2,4],[1,5],[2,5],[3,5],[2,6],[3,6],[4,6],[3,7],[4,7],[5,7],[3,8]]


                },
                {
                    "z_value": 4,
                    "pos": [-4,23],
                    "collision": False,
                })
                intro2 =  object({
                "#0444ba": [[0,0], [1,0], [2,0], [3,0], [4,0], [5,0], [6,0], [7,0], [8,0], [9,0],
                            [1,1], [2,1], [3,1], [4,1], [5,1], [6,1], [7,1], [8,1], [9,1],
                            [2,2], [3,2], [4,2], [5,2], [6,2], [7,2], [8,2],
                            [3,3], [4,3], [5,3], [6,3], [7,3], [8,3], 
                            [4,4], [5,4], [6,4],
                            [0,-1], [1,-1], [2,-1], [3,-1], [4,-1], [5,-1], [6,-1], [7,-1], [8,-1], [9,-1], 
                            [0,-2], [1,-2], [2,-2], [3,-2], [4,-2], [5,-2], [6,-2], [7,-2], [8,-2], [9,-2],
                           [0,-3], [1,-3], [2,-3], [3,-3], [4,-3], [5,-3], [6,-3], [7,-3], [8,-3], [9,-3], 
                           [0,-4], [1,-4], [2,-4], [3,-4], [4,-4], [5,-4], [6,-4], [7,-4], [8,-4], [9,-4],
                           [0,-5], [1,-5], [2,-5], [3,-5], [4,-5], [5,-5], [6,-5], [7,-5], [8,-5], 
                           [1,-6], [2,-6], [3,-6], [4,-6], [5,-6], [6,-6], [7,-6], 
                           [2,-7], [3,-7], [4,-7], [5,-7], [6,-7]],
                "#032057": [[1,-7], [0,-6], [-1,-5], [-1,-4], [-1,-3], [-1,-2], [-1,-1], [-1,0], [0,1], [1,2], [2,3], [3,4]],
                "#050101": [[6,-8], [5,-8], [4,-8], [3,-8], [2,-8], [1,-8], [0,-7], [-1,-6], [-2,-5], [-2,-4], [-2,-3], [-2,-2], [-2,-1], [-2,0], [-1,1], [-2,1], 
                            [0,2], [-1,2], [-2,2], [1,3], [0,3], [-1,3], [-2,3], [2,4], [1,4], [0,4], [6,5], [5,5], [4,5], [3,5], [2,5], [1,5], [0,5], 
                            [7,4], [8,4], [9,3], [9,2], [10,1], [10,0], [10,-1], [10,-2], [10,-3], [10,-4], [9,-5], [8,-6], [7,-7]],
                "#ba5604": [[-1,4], [-2,4], [-1,5], [-2,5], [-3,5], [-2,6],[-3,6],[-4,6], [-3,7],[-4,7],[-5,7],[-3,8]]
                },
                {
                    "z_value": 5,
                    "pos": [24,28],
                    "collision": False,
                })

    elif(currTime-game_start_time <3):
        if gameFlag==1:
            gameFlag=0
            objArr.append(intro1)
            objArr.append(intro2)
            objArr.append(ping)
            objArr.append(pong)
            
            objArr.append(backgro)
        offset(intro1, [1, 0])
        offset(intro2, [-1,0])
        
    elif(currTime-game_start_time >=3 and currTime-game_start_time<4):
        if (gameFlag ==0):
            gameFlag = 1
            objArr.pop(objArr.index(intro1))
            objArr.pop(objArr.index(intro2))
            objArr.pop(objArr.index(ping))
            objArr.pop(objArr.index(pong))
            print("popped")
    elif beginTimer:
        counter -= deltaTime
        
        if counter <= 0:
            beginTimer = False
            beginGame = True
            objArr.clear()
            objArr.append(backgro)
        elif counter <= 1:
            countDown(1)
        elif counter <= 2:
            countDown(2)
        elif counter >= 3:
            countDown(3)
    elif beginGame:

        def endGame():
            global beginGame, displayScore, counter
            # Call this function to end game
            beginGame = False
            displayScore = True
            counter = 0
        
        objArr.clear()
        objArr.append(backgro)
        
        # GAME HERE
        if pongOnce:

            pongPaddleT = object({
                "#080cd1": [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]
            }, {
                "z_value": 4,
                "pos": [8, 2],
                "stayInFrame": True,
                "collision": True
            })
            attPaddle = object({
                "#d13408": [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]
            }, {
                "z_value": 4,
                "pos": [8, 38],
                "stayInFrame": True,
                "collision": True
            })
            pongBall = object({
                "#f4f1de": [[0, 0]]
            }, {
                "z_value": 3,
                "pos": [
                    random.randint(5,15),
                    random.randint(0,2) + 19
                ],
                "stayInFrame": True,
                "collision": True
            })

            objArr.extend([
                attPaddle, pongBall, pongPaddleT
            ])

            pongOnce = False
        else:

            def shortenPaddle(ref):
                
                global pongPaddleT, attPaddle, pongEnd

                if len(ref.pixelArr[0]) > 1:
                    TpixArr = ref.pixelArr[0].copy()
                    TpixArr.pop(len(TpixArr)-1)
                    updateCollision(ref,[TpixArr])
                else:
                    endGame()

                    if ref == pongPaddleT:
                        pongEnd = 1
                    else:
                        pongEnd = -1
            
            def lengthenPaddle(ref):
                if len(ref.pixelArr[0]) >= 1:
                    TpixArr = ref.pixelArr[0].copy()
                    TpixArr.append(TpixArr[-1])
                    updateCollision(ref,[TpixArr])

            if getKeyState("Q"):
                if pongPaddleT.curr_pos[0] >= 0:
                    offset(pongPaddleT, [-1,0])
            if getKeyState("E"):
                if pongPaddleT.curr_pos[0] <= 19 - len(pongPaddleT.pixelArr[0]):
                    offset(pongPaddleT, [1,0])
            if getKeyState("A"):
                if attPaddle.curr_pos[0] >= 0:
                    offset(attPaddle, [-1,0])
            if getKeyState("D"):
                if attPaddle.curr_pos[0] <= 19 - len(attPaddle.pixelArr[0]):
                    offset(attPaddle, [1,0])

            if pongBreakTimer >= 1.5:
                offset(pongBall,pongBallVel)
            else:
                pongBreakTimer += deltaTime

            if pongBall.curr_pos[0] in [0,19]:
                pongBallVel[0] *= -1
            
            if (pongBall.curr_pos[1] == 3) and (pongBall.curr_pos[0] >= pongPaddleT.curr_pos[0]) and (pongBall.curr_pos[0] <= (pongPaddleT.curr_pos[0] + len(pongPaddleT.pixelArr[0])-1)):
                pongBallVel[1] *= -1
            if (pongBall.curr_pos[1] == 37) and (pongBall.curr_pos[0] >= attPaddle.curr_pos[0]) and (pongBall.curr_pos[0] <= (attPaddle.curr_pos[0] + len(attPaddle.pixelArr[0])-1)):
                pongBallVel[1] *= -1
            
            if pongBall.curr_pos[1] <= 1:
                shortenPaddle(pongPaddleT)
                lengthenPaddle(attPaddle)
                newPos = [
                    random.randint(5,15),
                    random.randint(0,2) + 19
                ]
                offset(pongBall,[
                    newPos[0] - pongBall.curr_pos[0],
                    newPos[1] - pongBall.curr_pos[1]
                ])
                pongBallVel = [
                    random.choice([1,-1]),
                    random.choice([1,-1])
                ]
                pongBreakTimer = 0
            
            if pongBall.curr_pos[1] >= 39:
                shortenPaddle(attPaddle)
                lengthenPaddle(pongPaddleT)
                newPos = [
                    random.randint(5,15),
                    random.randint(0,2) + 19
                ]
                offset(pongBall,[
                    newPos[0] - pongBall.curr_pos[0],
                    newPos[1] - pongBall.curr_pos[1]
                ])
                pongBallVel = [
                    random.choice([1,-1]),
                    random.choice([1,-1])
                ]
                pongBreakTimer = 0

            objArr.extend([
                attPaddle, pongBall, pongPaddleT
            ])
        
        updateScoreHeader()
        debugCounter += deltaTime

        # print("GAME RUNNING")
    else:
        if displayScore:
            objArr.clear()

            # display score here
            print("SCORE")

            if pongEnd == -1:
                # TOP WON
                winScreen = object({
                    "#ffffff": [
                        [0,0], [-1,1], [1,1], [-2,2], [2,2]
                    ]
                }, {
                    "z_value": 9,
                    "pos": [10, 20],
                    "stayInFrame": True,
                    "collision": False
                })

                objArr.append(winScreen)
            else:
                # BOT WON
                winScreen = object({
                    "#ffffff": [
                        [0,0], [-1,-1], [1,-1], [-2,-2], [2,-2]
                    ]
                }, {
                    "z_value": 9,
                    "pos": [10, 20],
                    "stayInFrame": True,
                    "collision": False
                })

                objArr.append(winScreen)

            displayScore = False
        else:
            counter += deltaTime

            if counter >= 5:
                gameChoice = None
                callHome = True
                print("OVER :(")

def game4():
    # ATTARI
    # created by AYUSH YADAV

    def countDown(num):

        # A demo count down characters have been made, can be changed as per needs

        global objArr

        num = int(num)

        if (num > 3) or (num < 0):
            raise Exception("time out of range")
        
        objArr.clear()

        if num == 3:
            countObj = txtObj("3",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 2:
            countObj = txtObj("2",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 1:
            countObj = txtObj("1",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        else:
            countObj = txtObj("GO",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        

    # variable access
    global objArr, deltaTime, once, beginTimer, counter, beginGame, displayScore
    global gameChoice, callHome, titleCounter, titleDisplayed, debugCounter
    global leftColor, rightColor, scoreLeft, scoreRight, healthLeft, healthRight

    global attPaddle, attBall, attOnce, attBallVel, attStage

    if once:
        if not titleDisplayed:
            print("game 1 now playing")
            # Game initialization
            objArr.clear()
            once = True

            # this is your title : make exactly one object that comprises of your entire title screen
            game1Title = txtObj("T",[9,17],"#ffff00",1,True,False)

            objArr.append(game1Title)

            print("Timer begins")

            titleDisplayed = True
        else:
            titleCounter += deltaTime
            if titleCounter >= 1:
                once = False
                beginTimer = True
    elif beginTimer:
        counter -= deltaTime
        
        if counter <= 0:
            beginTimer = False
            beginGame = True
            objArr.clear()
        elif counter <= 1:
            countDown(1)
        elif counter <= 2:
            countDown(2)
        elif counter >= 3:
            countDown(3)
    elif beginGame:

        def endGame():
            global beginGame, displayScore, counter
            # Call this function to end game
            beginGame = False
            displayScore = True
            counter = 0
        
        objArr.clear()
        
        # GAME HERE
        if attOnce:
            attOnce = False

            attPaddle = object({
                "#81b29a": [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0]]
            }, {
                "z_value": 4,
                "pos": [8, 38],
                "stayInFrame": True,
                "collision": True
            })
            attBall = object({
                "#f4f1de": [[0, 0]]
            }, {
                "z_value": 3,
                "pos": [10, 36],
                "stayInFrame": True,
                "collision": True
            })

            walls = [
                [
                    [0, 0], [1, 0], [2, 0]
                ],
                [
                    [0, 0], [1, 0], [2, 0],
                                    [2, 1],
                                    [2, 2]
                ],
                [
                            [1, -1],
                    [0, 0], [1, 0], [2, 0],
                            [1, 1]
                ],
                [
                    [0, 0],        [2, 0],
                            [1, 1],
                    [0, 2],        [2, 2]
                ],
                [
                    [0,0],
                    [0,1],
                    [0,2]
                ]
            ]

            lvl = []
            cellCount = 0
            # generate level
            while True:
                wallChoice = walls[random.randint(0, len(walls)-1)]
                cellCount += len(wallChoice)

                cellPos = [
                    random.randint(0, 19),
                    random.randint(0, 25)
                ]

                for coord in wallChoice:
                    newCoord = [
                        coord[0] + cellPos[0],
                        coord[1] + cellPos[1]
                    ]

                    if newCoord[0] < 0:
                        newCoord[0] += 20
                    if newCoord[0] > 19:
                        newCoord[0] -= 20

                    if newCoord[1] < 0:
                        newCoord[1] += 25
                    if newCoord[1] > 25:
                        newCoord[1] -= 25
                    
                    if (newCoord not in lvl) and (newCoord != [0,0]):
                        lvl.append(newCoord)

                if cellCount >= 50:
                    break

            attStage = object({
                None : [[0,0]],
                "#ffffff": lvl
            }, {
                "z_value": 4,
                "pos": [0, 0],
                "stayInFrame": True,
                "collision": True
            })

            objArr.extend([
                attPaddle, attBall, attStage
            ])
        else:

            if getKeyState("Left"):
                if attPaddle.curr_pos[0] >= 0:
                    offset(attPaddle, [-1,0])
            if getKeyState("Right"):
                if attPaddle.curr_pos[0] <= 19 - len(attPaddle.pixelArr[0]):
                    offset(attPaddle, [1,0])

            # check collision with level
            newPos = [
                attBall.curr_pos[0] + attBallVel[0],
                attBall.curr_pos[1] + attBallVel[1]
            ]

            for y in range(len(attStage.pixelArr)):
                for x in range(len(attStage.pixelArr[y])):
                    if attStage.pixelArr[y][x] is not None:
                        coordX = x + attStage.curr_pos[0] + attStage.minX
                        coordY = y + attStage.curr_pos[1] + attStage.minY

                        if (coordX == newPos[0]) and (coordY == newPos[1]):

                            def checkExistence(checkPosRel):

                                global attStage

                                cX = checkPosRel[0] - attStage.curr_pos[0] - attStage.minX
                                cY = checkPosRel[1] - attStage.curr_pos[1] - attStage.minY

                                if (cY >= 0) and (cY < len(attStage.pixelArr)):
                                    if (cX >= 0) and (cX < len(attStage.pixelArr[cY])):
                                        if attStage.pixelArr[cY][cX] is not None:
                                            return True
                                        else:
                                            return False
                                    return False
                                return False


                            print("DAMN") # collision will happen

                            # getting the surround state
                            surroundState = [
                                [None, None, None],
                                [None, None, None],
                                [None, None, None]
                            ]

                            for m in range(3):
                                relX = m - 1
                                for n in range(3):
                                    relY = n - 1
                                    if (relX == 0) and (relY == 0):
                                        pass
                                    else:
                                        checkX = attBall.curr_pos[0] + relX
                                        checkY = attBall.curr_pos[1] + relY

                                        if (checkX >= 0) and (checkX <= 19):
                                            if (checkY >= 0) and (checkY <= 39):
                                                
                                                print(checkX, checkY)
                                                surroundState[n][m] = checkExistence([checkX, checkY])
                            
                            # debug surround state
                            for ja in surroundState:
                                print(ja)
                            
                            if attBallVel == [1, -1]:
                                # going top right
                                if surroundState[0][1] and (not surroundState[1][2]):
                                    attBallVel = [1, 1]
                                elif (not surroundState[0][1]) and surroundState[1][2]:
                                    attBallVel = [-1, -1]
                                else:
                                    attBallVel = [-1, 1]
                            elif attBallVel == [1, 1]:
                                # going bot right
                                if surroundState[2][1] and (not surroundState[1][2]):
                                    attBallVel = [1, -1]
                                elif (not surroundState[2][1]) and surroundState[1][2]:
                                    attBallVel = [-1, 1]
                                else:
                                    attBallVel = [-1, -1]
                            elif attBallVel == [-1, 1]:
                                # going bot left
                                if surroundState[1][0] and (not surroundState[2][1]):
                                    attBallVel = [1, 11]
                                elif (not surroundState[1][0]) and surroundState[2][1]:
                                    attBallVel = [-1, -1]
                                else:
                                    attBallVel = [1, -1]
                            else:
                                # going top left
                                if surroundState[0][1] and (not surroundState[1][0]):
                                    attBallVel = [-1, 1]
                                elif (not surroundState[0][1]) and surroundState[1][0]:
                                    attBallVel = [1, -1]
                                else:
                                    attBallVel = [1, 1]

                            attStage.changeColor([x, y], None)
            
            offset(attBall, attBallVel)

            if attBall.curr_pos[0] in [0,19]:
                attBallVel[0] *= -1
            
            if (attBall.curr_pos[1] == 37) and (attBall.curr_pos[0] >= attPaddle.curr_pos[0]) and (attBall.curr_pos[0] <= (attPaddle.curr_pos[0] + len(attPaddle.pixelArr[0])-1)):
                attBallVel[1] *= -1
            
            if attBall.curr_pos[1] == 0:
                attBallVel[1] *= -1
            
            if attBall.curr_pos[1] >= 38:
                endGame()
            
            objArr.extend([
                attBall, attPaddle, attStage
            ])
        
        updateScoreHeader()
    else:
        if displayScore:
            objArr.clear()

            # display score here
            print("SCORE")

            displayScore = False
        else:
            counter += deltaTime

            if counter >= 5:
                gameChoice = None
                callHome = True
                print("OVER :(")

def game5():

    def countDown(num):

        # A demo count down characters have been made, can be changed as per needs

        global objArr

        num = int(num)

        if (num > 3) or (num < 0):
            raise Exception("time out of range")
        
        objArr.clear()

        if num == 3:
            countObj = txtObj("3",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 2:
            countObj = txtObj("2",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        elif num == 1:
            countObj = txtObj("1",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        else:
            countObj = txtObj("GO",[8,17],"#ffffff",1,False,False)
            objArr.append(countObj)
        

    # variable access
    global objArr, deltaTime, once, beginTimer, counter, beginGame, displayScore
    global gameChoice, callHome, titleCounter, titleDisplayed, debugCounter
    global leftColor, rightColor, scoreLeft, scoreRight, healthLeft, healthRight

    global bul1, bul2, bul3, obj2, obj3, obj4, obj5, obj6, heart1, heart2, heart3, life, gameEnd, gameFlag2, endflag
    global bs1, Mon1, Mon2, Mon3, line, Space, Invader, backg, Scoreobj, gameStart, gameFlag, count, score, flagc, GameOver1, GameOver2
    gameFlag = 1
    count = 0
    countm = 0
    
    if once:
        if not titleDisplayed:
            print("game 5 now playing")
            # Game initialization
            objArr.clear()
            once = True


            titleDisplayed = True
        else:
            # titleCounter += deltaTime
            # if titleCounter >= 1:
            once = False
            beginTimer = True
            gameStart = time.time()
            gameFlag2 = 1
            endflag = 1
        obj2 = object({  #bullet
        "#ff8a05": [[0,2]], #Orange1
        "#ff3b05": [[0,1]], #Orange2
        "#7a0000": [[0,0]] #Red]
        },
        {
            "z_value": 4,
            "pos": [15,-15],
            "collision" : True
        })
        obj3 = object({  #bullet
            "#ff8a05": [[0,2]], #Orange1
            "#ff3b05": [[0,1]], #Orange2
            "#7a0000": [[0,0]] #Red]
            },
            {
                "z_value": 4,
                "pos": [9,9],
                "collision" : True
            })
        obj4 = object({  #bullet
            "#ff8a05": [[0,2]], #Orange1
            "#ff3b05": [[0,1]], #Orange2
            "#7a0000": [[0,0]] #Red]
            },
            {
                "z_value": 4,
                "pos": [4,2],
                "collision" : True
            })
        obj5 = object({  #bullet
            "#ff8a05": [[0,2]], #Orange1
            "#ff3b05": [[0,1]], #Orange2
            "#7a0000": [[0,0]] #Red]
            },
            {
                "z_value": 4,
                "pos": [8,-7],
                "collision" : True
            })
        obj6 = object({  #bullet
            "#ff8a05": [[0,2]], #Orange1
            "#ff3b05": [[0,1]], #Orange2
            "#7a0000": [[0,0]] #Red]
            },
            {
                "z_value": 4,
                "pos": [17, 0],
                "collision" : True
            })

        bul1 = object({  #bullet
            "#028000": [[0,-1]],
            "#0eff0a": [[0,0]] #Bullet
            },
            {
                "z_value": 3,
                "pos": [bs1.curr_pos[0],bs1.curr_pos[1] -3],
                "collision" : True
            })
        bul2 = object({  #bullet
            "#028000": [[0,-1]],
            "#0eff0a": [[0,0]] #Bullet
            },
            {
                "z_value": 3,
                "pos": [bs1.curr_pos[0],bs1.curr_pos[1] +4],
                "collision" : True
            })
        bul3 = object({  #bullet
            "#028000": [[0,-1]],
            "#0eff0a": [[0,0]] #Bullet
            },
            {
                "z_value": 3,
                "pos": [bs1.curr_pos[0],bs1.curr_pos[1] +11],
                "collision" : True
            })
        heart1  = object({  #heart
            "#f2022a": [[-1, -1], [1, -1] ],
            "#a32603": [[1, 0], [0, 1]],
            "#f777aa": [[0, 0], [-1, 0]]
            },
            {
                "z_value": 6,
                "pos": [9, 2],
                "collision" : True
            })
        heart2  = object({  #heart
            "#f2022a": [[-1, -1], [1, -1] ],
            "#a32603": [[1, 0], [0, 1]],
            "#f777aa": [[0, 0], [-1, 0]]
            },
            {
                "z_value": 6,
                "pos": [13, 2],
                "collision" : True
            })
        heart3  = object({  #heart
            "#f2022a": [[-1, -1], [1, -1] ],
            "#a32603": [[1, 0], [0, 1]],
            "#f777aa": [[0, 0], [-1, 0]]
            },
            {
                "z_value": 6,
                "pos": [17, 2],
                "collision" : True
            })
        Mon1  = object({  #design
            "#78d7ff": [[0,0], [-1,0], [-2,0], [-3,0], [1, 0], [2,0], [3,0],[0,-1], [1, -1], [2, -1], [-1,-1], [-2,-1],
                        [-2,-2], [1,-2], [-3,-3], [0,-3], [0,1], [-3,1], [-4,1], [3,1], [0,2],[-1,2], [-2,2], [-3,2], [1,2], [2,2], [3,2], [4,2],
                            [-2,3], [1,3], [4,3], [-4,1], [-6,1], [-7,1], [-9,1], [-10,1],
                            [0,4], [-3,4], [-5,4], [-7,4], [-9, 4], [3,4]  ],
            "#f0c297": [[-2,1], [1,1]],
            "#1a466b": [[-1,1], [2,1]]
            },
            {
                "z_value": 3,
                "pos": [-35, 21],
                "collision" : False
            })
        Mon2  = object({  #design
            "#3dff6e": [[0,0], [-3,0], [3,0], [0,-1], [-1,-1], [-2,-1], [-3,-1], [1,-1], [2,-1], [3,-1], [-1,-2], [-2,-2], [1,-2], [2,-2],
                        [-1,-3], [1,-3], [0,1], [-1,1], [-2,1], [-3,1], [-4,1], [1,1], [2,1], [3,1], [4,1], [-2,2], [2,2],
                        [-4,2], [4,2], [-4,3], [4,3], [-1,3], [1,3], [6,1], [7,1], [6,3], [8,3]],
            "#0e0f2c": [[-2,0], [1,0]],
            "#78d7ff": [[-1,0], [2,0]]
            },
            {
                "z_value": 3,
                "pos": [55, 10],
                "collision" : False
            })
        Mon3  = object({  #design
            "#f5a15d": [[0,0], [-2,0], [2,0], [0,1], [-1,1], [-2,1], [1,1], [2,1], [0,-1], [-1,-1], [-2,-1], [1,-1], [2,-1], [-4,-1], [4,-1], [-2,-2], [2, -2], 
                        [0,-3], [-4,-3], [4,-3], [0,-4], [-2,-4], [2,-4], [-2,-5], [2,-5], [-4,-5], [4,-5], [-4,-6], [4,-6], [-2,-7], [2,-7], [-4,-8], [4,-8]],
            "#c6d831": [[0,2], [-1,2], [1,2], [0,3], [-3,0], [3,0], [-3,-1], [3,-1], [-3,-2], [3,-2], [-4,-2], [4,-2], [-1,-4], [1,-4]],
            "#401102": [[-1,0], [1,0]]
            },
            {
                "z_value": 3,
                "pos": [9, -50],
                "collision" : False
            })
    
    elif beginGame:

        def endGame():
            global beginGame, displayScore, counter
            # Call this function to end game
            beginGame = False
            displayScore = True
            counter = 0
            gameStart = time.time()
        
        objArr.clear()
        
    elif(currTime-gameStart <5):
        if(gameFlag == 1):
            gameFlag = 2
            objArr.append(Mon1)
            objArr.append(Mon2)
            objArr.append(Mon3)
            objArr.append(Space)
            objArr.append(Invader)
            objArr.append(backgro5)
            objArr.append(backg)
            objArr.append(line)

        offset(Mon1, [1,0])    
        offset(Mon2, [-1,0]) 
        offset(Mon3, [0,2])
        offset(Space, [0,1])
        offset(Invader, [0,1])
        print(currTime-gameStart)
        print(gameFlag)
    elif(currTime-gameStart >=5 and currTime-gameStart<6):
        if (gameFlag2 == 1):
            gameFlag2 = 0
            objArr.append(obj2)
            print("ho gaya bhai")
            objArr.append(bs1)
            objArr.append(obj3)
            objArr.append(obj4)
            objArr.append(obj5)
            objArr.append(obj6)
            objArr.append(line)
            objArr.append(bul1)
            objArr.append(bul2)
            objArr.append(bul3)
            objArr.append(heart1)
            objArr.append(heart2)
            objArr.append(heart3)
            objArr.append(backgro5)
            objArr.append(Scoreobj)
            
            objArr.append(backg)
    elif (life>0):
        gameEnd = time.time()
        # CODE IN HERE RUNS ONCE PER FRAME
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        
           
        offset(obj2, [0,1])
        offset(obj3, [0,1])
        offset(obj4, [0,1])
        offset(obj5, [0,1])
        offset(obj6, [0,1])
        offset(bul1, [0,-6])
        offset(bul2, [0,-6])
        offset(bul3, [0,-6])
        countm +=1
            
        
        if flagc ==1 :
            flagc = 0
            life-=1
            print(life)
            
            if (life ==2):
                objArr.pop(objArr.index(heart1))
                
            if (life ==1):
                objArr.pop(objArr.index(heart2))
            if (life == 0):
                objArr.pop(objArr.index(heart3))
        

            
        if getKeyState("A"):
            offset(bs1, [-1,0])
        if getKeyState("D"):
            offset(bs1, [1,0])
        objArr.pop(objArr.index(Scoreobj))
        Scoreobj = txtObj(str(score), [1, 0], "#f59905", 6, True)
        objArr.append(Scoreobj)
        #↓↓↓↓↓↓↓↓↓↓↓RESETS BULLETS↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        if obj2.curr_pos[1] >= 40:
            offset(obj2, [0, -36])
            ran = random.randint(0,10)
            if obj2.curr_pos[0]<=10:
                
                offset(obj2,[ran, 0])
            else: offset(obj2,[-ran,0])
        if obj3.curr_pos[1] >= 40:
            offset(obj3, [0, -36])
            ran = random.randint(0,10)
            if obj3.curr_pos[0]<=10:
                
                offset(obj3,[ran, 0])
            else: offset(obj3,[-ran,0])
        if obj4.curr_pos[1] >= 40:
            offset(obj4, [0, -36])
            ran = random.randint(0,10)
            if obj4.curr_pos[0]<=10:
                
                offset(obj4,[ran, 0])
            else: offset(obj4,[-ran,0])
        if obj5.curr_pos[1] >= 40:
            offset(obj5, [0, -36])
            ran = random.randint(0,10)
            if obj5.curr_pos[0]<=10:
                
                offset(obj5,[ran, 0])
            else: offset(obj5,[-ran,0])
        if obj6.curr_pos[1] >= 40:
            offset(obj6, [0, -36])
            ran = random.randint(0,10)
            if obj6.curr_pos[0]<=10:
                
                offset(obj6,[ran, 0])
            else: offset(obj6,[-ran,0])
        if bul1.curr_pos[1] <=4:
            offset(bul1, [bs1.curr_pos[0]-bul1.curr_pos[0],bs1.curr_pos[1]-bul1.curr_pos[1]-3])
        if bul2.curr_pos[1] <=4:
            offset(bul2, [bs1.curr_pos[0]-bul2.curr_pos[0],bs1.curr_pos[1]-bul2.curr_pos[1]-3])
        if bul3.curr_pos[1] <=4:
            offset(bul3, [bs1.curr_pos[0]-bul3.curr_pos[0],bs1.curr_pos[1]-bul3.curr_pos[1]-3])
        # ↑↑↑↑↑↑↑↑↑↑↑RESETS BULLETS↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ 
            
         # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓COLLISION↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        ran = random.randint(0,10)
        if (bs1.curr_pos[0] == obj2.curr_pos[0]):
            if(bs1.curr_pos[1]-obj2.curr_pos[1]<=5 and bs1.curr_pos[1]-obj2.curr_pos[1]>=0 ):
                offset(obj2, [0, -obj2.curr_pos[1]])
                ran = random.randint(0,10)
                if obj2.curr_pos[0]<=10:
                    
                    offset(obj2,[ran, 0])
                else: offset(obj2,[-ran,0])
                flagc =1
        if (bs1.curr_pos[0] == obj3.curr_pos[0]):
            if(bs1.curr_pos[1]-obj3.curr_pos[1]<=5 and bs1.curr_pos[1]-obj3.curr_pos[1]>=0 ):
                offset(obj3, [0, -obj3.curr_pos[1]])
                if obj3.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj3,[ran, 0])
                else: offset(obj3,[-ran,0])
                flagc =1
        if (bs1.curr_pos[0] == obj4.curr_pos[0]):
            if(bs1.curr_pos[1]-obj4.curr_pos[1]<=5 and bs1.curr_pos[1]-obj4.curr_pos[1]>=0 ):
                offset(obj4, [0, -obj4.curr_pos[1]])
                if obj4.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj4,[ran, 0])
                else: offset(obj4,[-ran,0])
                flagc =1
        if (bs1.curr_pos[0] == obj5.curr_pos[0]):
            if(bs1.curr_pos[1]-obj5.curr_pos[1]<=5 and bs1.curr_pos[1]-obj5.curr_pos[1]>=0 ):
                offset(obj5, [0, -obj5.curr_pos[1]])
                if obj5.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj5,[ran, 0])
                else: offset(obj5,[-ran,0])
                flagc =1
        if (bs1.curr_pos[0] == obj6.curr_pos[0]):
            if(bs1.curr_pos[1]-obj6.curr_pos[1]<=5 and bs1.curr_pos[1]-obj6.curr_pos[1]>=0 ):
                offset(obj6, [0, -obj6.curr_pos[1]])
                if obj6.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj6,[ran, 0])
                else: offset(obj6,[-ran,0])
                flagc =1
        
        if (abs(bs1.curr_pos[0]-obj2.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj2.curr_pos[1]<=3 and bs1.curr_pos[1]-obj2.curr_pos[1]>=0 ):
                offset(obj2, [0, -obj2.curr_pos[1]])
                if obj2.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj2,[ran, 0])
                else: offset(obj2,[-ran,0])
                flagc =1
                print(flagc)
        if (abs(bs1.curr_pos[0]-obj3.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj3.curr_pos[1]<=3 and bs1.curr_pos[1]-obj3.curr_pos[1]>=0 ):
                offset(obj3, [0, -obj3.curr_pos[1]])
                if obj3.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj3,[ran, 0])
                else: offset(obj3,[-ran,0])
                flagc =1
        if (abs(bs1.curr_pos[0]-obj4.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj4.curr_pos[1]<=3 and bs1.curr_pos[1]-obj4.curr_pos[1]>=0 ):
                offset(obj4, [0, -obj4.curr_pos[1]])
                if obj4.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj4,[ran, 0])
                else: offset(obj4,[-ran,0])
                flagc =1
        if (abs(bs1.curr_pos[0]-obj5.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj5.curr_pos[1]<=3 and bs1.curr_pos[1]-obj5.curr_pos[1]>=0 ):
                offset(obj5, [0, -obj5.curr_pos[1]])
                if obj5.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj5,[ran, 0])
                else: offset(obj5,[-ran,0])
                flagc =1
        if (abs(bs1.curr_pos[0]-obj6.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj6.curr_pos[1]<=3 and bs1.curr_pos[1]-obj6.curr_pos[1]>=0 ):
                offset(obj6, [0, -obj6.curr_pos[1]])
                if obj6.curr_pos[0]<=10:
                    ran = random.randint(0,10)
                    offset(obj6,[ran, 0])
                else: offset(obj6,[-ran,0])
                flagc =1
        
        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑COLLISION↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓SHOT DOWN↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        ran = random.randint(0,10)
        if(bul1.curr_pos[1]-obj2.curr_pos[1]>=0 and bul1.curr_pos[1]-obj2.curr_pos[1]<6 and bul1.curr_pos[0]==obj2.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul1, [bs1.curr_pos[0]-bul1.curr_pos[0],bs1.curr_pos[1]-bul1.curr_pos[1]-3])
            offset(obj2, [0, -obj2.curr_pos[1]])
            if obj2.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj2,[ran, 0])
            else: offset(obj2,[-ran,0])
        if(bul1.curr_pos[1]-obj3.curr_pos[1]>=0 and bul1.curr_pos[1]-obj3.curr_pos[1]<6 and bul1.curr_pos[0]==obj3.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul1, [bs1.curr_pos[0]-bul1.curr_pos[0],bs1.curr_pos[1]-bul1.curr_pos[1]-3])
            offset(obj3, [0, -obj3.curr_pos[1]])
            if obj3.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj3,[ran, 0])
            else: offset(obj3,[-ran,0])
        if(bul1.curr_pos[1]-obj4.curr_pos[1]>=0 and bul1.curr_pos[1]-obj4.curr_pos[1]<6 and bul1.curr_pos[0]==obj4.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul1, [bs1.curr_pos[0]-bul1.curr_pos[0],bs1.curr_pos[1]-bul1.curr_pos[1]-3])
            offset(obj4, [0, -obj4.curr_pos[1]])
            if obj4.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj4,[ran, 0])
            else: offset(obj4,[-ran,0])
        if(bul1.curr_pos[1]-obj5.curr_pos[1]>=0 and bul1.curr_pos[1]-obj5.curr_pos[1]<6 and bul1.curr_pos[0]==obj5.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul1, [bs1.curr_pos[0]-bul1.curr_pos[0],bs1.curr_pos[1]-bul1.curr_pos[1]-3])
            offset(obj5, [0, -obj5.curr_pos[1]])
            if obj5.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj5,[ran, 0])
            else: offset(obj5,[-ran,0])
        if(bul1.curr_pos[1]-obj6.curr_pos[1]>=0 and bul1.curr_pos[1]-obj6.curr_pos[1]<6 and bul1.curr_pos[0]==obj6.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul1, [bs1.curr_pos[0]-bul1.curr_pos[0],bs1.curr_pos[1]-bul1.curr_pos[1]-3])
            offset(obj6, [0, -obj6.curr_pos[1]])
            if obj6.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj6,[ran, 0])
            else: offset(obj6,[-ran,0])
        if(bul2.curr_pos[1]-obj2.curr_pos[1]>=0 and bul2.curr_pos[1]-obj2.curr_pos[1]<6 and bul2.curr_pos[0]==obj2.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul2, [bs1.curr_pos[0]-bul2.curr_pos[0],bs1.curr_pos[1]-bul2.curr_pos[1]-3])
            offset(obj2, [0, -obj2.curr_pos[1]])
            if obj2.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj2,[ran, 0])
            else: offset(obj2,[-ran,0])
        if(bul2.curr_pos[1]-obj3.curr_pos[1]>=0 and bul2.curr_pos[1]-obj3.curr_pos[1]<6 and bul2.curr_pos[0]==obj3.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul2, [bs1.curr_pos[0]-bul2.curr_pos[0],bs1.curr_pos[1]-bul2.curr_pos[1]-3])
            offset(obj3, [0, -obj3.curr_pos[1]])
            if obj3.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj3,[ran, 0])
            else: offset(obj3,[-ran,0])
        if(bul2.curr_pos[1]-obj4.curr_pos[1]>=0 and bul2.curr_pos[1]-obj4.curr_pos[1]<6 and bul2.curr_pos[0]==obj4.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul2, [bs1.curr_pos[0]-bul2.curr_pos[0],bs1.curr_pos[1]-bul2.curr_pos[1]-3])
            offset(obj4, [0, -obj4.curr_pos[1]])
            if obj4.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj4,[ran, 0])
            else: offset(obj4,[-ran,0])
        if(bul2.curr_pos[1]-obj5.curr_pos[1]>=0 and bul2.curr_pos[1]-obj5.curr_pos[1]<6 and bul2.curr_pos[0]==obj5.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul2, [bs1.curr_pos[0]-bul2.curr_pos[0],bs1.curr_pos[1]-bul2.curr_pos[1]-3])
            offset(obj5, [0,-obj5.curr_pos[1]])
            if obj5.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj5,[ran, 0])
            else: offset(obj5,[-ran,0])
        if(bul2.curr_pos[1]-obj6.curr_pos[1]>=0 and bul2.curr_pos[1]-obj6.curr_pos[1]<6 and bul2.curr_pos[0]==obj6.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul2, [bs1.curr_pos[0]-bul2.curr_pos[0],bs1.curr_pos[1]-bul2.curr_pos[1]-3])
            offset(obj6, [0, -obj6.curr_pos[1]])
            if obj6.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj6,[ran, 0])
            else: offset(obj6,[-ran,0])
        if(bul3.curr_pos[1]-obj2.curr_pos[1]>=0 and bul3.curr_pos[1]-obj2.curr_pos[1]<6 and bul3.curr_pos[0]==obj2.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul3, [bs1.curr_pos[0]-bul3.curr_pos[0],bs1.curr_pos[1]-bul3.curr_pos[1]-3])
            offset(obj2, [0, -obj2.curr_pos[1]])
            if obj2.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj2,[ran, 0])
            else: offset(obj2,[-ran,0])
        if(bul3.curr_pos[1]-obj3.curr_pos[1]>=0 and bul3.curr_pos[1]-obj3.curr_pos[1]<6 and bul3.curr_pos[0]==obj3.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul3, [bs1.curr_pos[0]-bul3.curr_pos[0],bs1.curr_pos[1]-bul3.curr_pos[1]-3])
            offset(obj3, [0, -obj3.curr_pos[1]])
            if obj3.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj3,[ran, 0])
            else: offset(obj3,[-ran,0])
        if(bul3.curr_pos[1]-obj4.curr_pos[1]>=0 and bul3.curr_pos[1]-obj4.curr_pos[1]<6 and bul3.curr_pos[0]==obj4.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul3, [bs1.curr_pos[0]-bul3.curr_pos[0],bs1.curr_pos[1]-bul3.curr_pos[1]-3])
            offset(obj4, [0, -obj4.curr_pos[1]])
            if obj4.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj4,[ran, 0])
            else: offset(obj4,[-ran,0])
        if(bul3.curr_pos[1]-obj5.curr_pos[1]>=0 and bul3.curr_pos[1]-obj5.curr_pos[1]<6 and bul3.curr_pos[0]==obj5.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul3, [bs1.curr_pos[0]-bul3.curr_pos[0],bs1.curr_pos[1]-bul3.curr_pos[1]-3])
            offset(obj5, [0, -obj5.curr_pos[1]])
            if obj5.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj5,[ran, 0])
            else: offset(obj5,[-ran,0])
        if(bul3.curr_pos[1]-obj6.curr_pos[1]>=0 and bul3.curr_pos[1]-obj6.curr_pos[1]<6 and bul3.curr_pos[0]==obj6.curr_pos[0]) :
            score+=1
            scoreflag = 1
            offset(bul3, [bs1.curr_pos[0]-bul3.curr_pos[0],bs1.curr_pos[1]-bul3.curr_pos[1]-3])
            offset(obj6, [0, -obj6.curr_pos[1]])
            if obj6.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj6,[ran, 0])
            else: offset(obj6,[-ran,0])
        

    elif(currTime-gameEnd<2 and currTime>gameEnd):
        if(endflag==1):
            endflag=0
            objArr.pop(objArr.index(bul1))
            objArr.pop(objArr.index(bul2))
            objArr.pop(objArr.index(bul3))
            objArr.pop(objArr.index(obj2))
            objArr.pop(objArr.index(obj3))
            objArr.pop(objArr.index(obj4))
            objArr.pop(objArr.index(obj5))
            objArr.pop(objArr.index(obj6))
            objArr.pop(objArr.index(Scoreobj))
            objArr.pop(objArr.index(bs1))
            bs2 = object({ #battleship
            "#fa753c": [[0,-1], [1,-1], [1,-2]], #red
            "#d4a50b": [[0,1]], #grey
            "#6e0202": [[0,0]], #og
            "#eb6f02": [[-1,0],[1,0]], #dark blue
            "#852300": [[-2,0],[2,0],[-1,-1],[1,0]] #boosters
            },
            {
                "z_value": 5,
                "pos": [10,39],
                "collision" : True,
                "stayInFrame": True
            })
            GameOver1 = txtObj("GAME", [1, 14], "#bc3ff2", 2, False)
            GameOver2 = txtObj("OVER", [3, 20], "#bc3ff2", 2, False)
            objArr.append(bs2)
            
            objArr.append(GameOver1)
            objArr.append(GameOver2)
        offset(GameOver1, [1,0])
        offset(GameOver2, [-1,0])
            
    else:
        if(endflag == 0):
            endflag = 1
            Scoreobj = txtObj(str(score), [8, 22], "#bc3ff2", 6, True)
            EndScore = txtObj("SCORE", [0, 16], "#bc3ff2", 2, False)
            objArr.pop(objArr.index(GameOver1))
            objArr.pop(objArr.index(GameOver2))
            objArr.append(Scoreobj)
            objArr.append(EndScore)

            counter = 0
        
        counter += deltaTime

        if counter >= 2:
            gameChoice = None
            callHome = True
            print("OVER :(")

        updateScoreHeader()

def game6():

    with open('disp.json', 'r') as file:
        data = json.load(file)
    # print(type(data))
    sadness = object(data, {
                "z_value": 5,
                "pos": [0,0],
                "collision" : True,
                "stayInFrame": True
            })

    objArr.append(sadness)

    
   
def gameFrame():

    global once, beginTimer, counter, beginGame, displayScore
    global targetDt, frameTime, deltaTime

    frameTime += deltaTime

    if frameTime >= targetDt:
        frameTime = 0

        if callHome:
            home()
        else:
            if gameChoice == 1:
                game1()
            elif gameChoice == 2:
                game2()
            elif gameChoice == 3:
                game3()
            elif gameChoice == 4:
                game4()
            elif gameChoice == 5:
                game5()
            elif gameChoice == 6:
                game6()
            else:
                pass


# ================================================
# DO NOT MESS FROM HERE ON
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
parth = 0
def renderFrame(cv, side):
    global objArr, mainMatrix, parth
    # make LED MATRIX with default color
    mainMatrix = []

    row_temp = []
    for i in range(20):
        row_temp.append(background)
    for i in range(40):
        mainMatrix.append(row_temp.copy())
    
    # arrange objects wrt z_values
    orderedArray = [] # the array that shall store the objectss in z-value order

    counter = 0
    retake = False
    while len(objArr) > 0:
        for obj in objArr:
            if obj.zVal == counter:
                orderedArray.append(obj)
                objArr.remove(obj)
                retake = True
        if retake:
            retake = False
        else:
            counter += 1

    objArr = orderedArray.copy()
    orderedArray.clear()
        
    # iterating through all objects and updating the mainMatrix grid
    for obj in objArr:
        # get the pixelArr
        pixelArr = obj.pixelArr
        # position of origin on screen
        pos = obj.curr_pos
        # making the needed squares on tkinter window
        # iterating through all pixels of the pixelArray
        for r in range(len(pixelArr)):
            for c in range(len(pixelArr[r])):
                onmainMatrixPos_x = c - obj.bound_origin[0] + obj.curr_pos[0]
                onmainMatrixPos_y = r - obj.bound_origin[1] + obj.curr_pos[1]
                if (onmainMatrixPos_x >= 0) and (onmainMatrixPos_x <= 19):
                    if (onmainMatrixPos_y >= 0) and (onmainMatrixPos_y <= 39):
                        if pixelArr[r][c] is not None:
                            mainMatrix[onmainMatrixPos_y][onmainMatrixPos_x] = pixelArr[r][c]
    
    colorArr = ['#021ed4', '#397b44', '#75D9A0', '#FA7036', '#0ea3e8', '#b6d53c', '#cfc6b8', '#4acc3b', '#f002e8', '#f5f5f5', '#78d7ff', '#d4514a', '#f47e1b', '#f1b5cb', '#0cb5f2', '#3dff6e', '#0444ba', '#7b1ff2', '#6e0202', '#FFE300', '#f777aa', '#ffaeb6', '#005285', '#401102', '#386641', '#e28df7', '#00ff00', '#9effae', '#f5f75e', '#0af7ef', '#f4b41b', '#f59905', '#ba5604', '#E8E8E8', '#ff3b05', '#28ccdf', '#bc4749', '#a93b3b', '#eb6f02', '#FFA500', '#d13408', '#D17FD6', '#032057', '#e6482e', '#16db93', '#ebbea8', '#92fc65', '#f0c297', '#ff0505', '#d4a50b', '#631111', '#81b29a', '#930ddb', '#9b6a6c', '#ffffff', '#367beb', '#39314b', '#3978a8', '#205907', '#bc3ff2', '#8e478c', '#c6d831', '#444444', '#583bcc', '#1a466b', '#302c2e', '#bd1411', '#f5a15d', '#f2022a', '#a7c957', '#dddddd', '#eb9e34', '#0e0f2c', '#ffff00', '#0eff0a', '#222222', '#fa753c', '#bd8111', '#013220', '#EB2226', '#050101', '#394778', '#6a994e', '#e2a0ff', '#ff8a05', '#852300', '#e94f37', '#ff0000', '#3f3cfa', '#4ddb0f', '#71aa34', '#7a0000', '#f4f1de', '#000000', '#a32603', '#db2525', '#080cd1', '#028000', '#bf0fb6', '#eea160', '#034d04', '#69DFDB', '#7d7071']
                            
    # COLUMN WISE mainMatrix
    colMat = []

    for colNum in range(20):
        firstTime = True
        for rowNum in range(40):
            if firstTime:
                #colMat.append([chr(colorArr.index(mainMatrix[rowNum][colNum]) + 1)])
                colMat.append([mainMatrix[rowNum][colNum]])
                firstTime = False
            else:
                #colMat[colNum].append(chr(colorArr.index(mainMatrix[rowNum][colNum]) + 1))
                colMat[colNum].append(mainMatrix[rowNum][colNum])
    
    
    #z = input(" : ")
    
    # this column mainMatrix stores data column wise as is required by the row-wise arrangement of the pixel
    # def serialPrin(byte):
    #     pass

    # colorArr = []

    # tCount = 0
    # tSum = 0

    # for col in colMat:
    #     for pix in col:

    #         i = colorArr.index(pix)

    #         serialPrin(255)
    #         serialPrin(i)

    #         tCount += 1
    #         tSum += i

    #         if tCount == 10:
    #             for j in range(3):
                    
    #                 rem = tSum % 245
    #                 quo = int((tSum - rem) / 245)

    #                 serialPrin(254)
    #                 serialPrin(quo)
    #                 serialPrin(rem)
                
    #             tCount = 0
    #             tSum = 0
    


    # VISUAL DEBUG
    # painting the tkinter output screen as per mainMatrix array
    cv.delete("all") # clear screen
    for r in range(40):
        for c in range(20):
            Xi = c*side + 10
            Xf = c*side + side + 10
            Yi = r*side + 10
            Yf = r*side + side + 10
            temp = cv.create_rectangle(Xi, Yi, Xf, Yf, fill=mainMatrix[r][c])

    try:
        ser = serial.Serial(baudrate=38400, timeout=1, port='/dev/ttyUSB0')  # Adjust port as needed
    except Exception as e:
        print('Port open error:', e)
        exit(1)
    
    try:
         for inner_array in colMat:
             for string in inner_array:
                 #print(string)
                 ser.write(string.encode('utf8'))  # Send each string followed by a newline
             ser.write("\n".encode('utf8'))
             #print(ser.read())
            
    except Exception as e:
         print('Error sending data:', e)
         ser.close()   
         exit(1)

    ser.close()


# main loop of the game will run every frame
def nxtFrame(root, cv, sc):
    global end
    global currTime
    global timeGone
    global deltaTime

    if not end:
        gameFrame()

        renderFrame(cv, sc)

        rT = time.time()
        deltaTime = rT - currTime
        currTime = rT
        timeGone += deltaTime
        # print(timeGone, deltaTime)

        # RECALL the nxt frame function to
        root.after(35, nxtFrame, root, cv, sc)
    else:
        # tk mainloop will end now
        pass


# beginning tkinter output window
# sc = int(input("ENTER cell size for SCREEN OUTPUT : ")) * 2
sc = 20 # DEBUG


# declaring basic window
root = tk.Tk()
root.title("LED MATRIX")
root.geometry(str(20*sc+20)+"x"+str(40*sc+20))

cv = tk.Canvas(root, width=20*sc+20, height=40*sc+20)
cv.pack()

# cv.create_rectangle(0, 0, 420, 820, fill="#ff0000", outline="black")

# will start the frame by frame stuff 35ms delay shall create an almost 30FPS scenario
root.after(1, nxtFrame, root, cv, sc)

# Tk WINDOW
root.mainloop()
