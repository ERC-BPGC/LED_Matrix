import tkinter as tk
import keyboard # for getting key inputs
import time
import random
import numpy as np
# =============================================
# IMPORT ANY LIBRARY YOU WANT HERE
# =============================================
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

# import

# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

# SOME ASSUMPTIONS
# X values are the column numbers starting from 0 (LEFT) to 19 (RIGHT)
# Y values are the row numbers starting from 0 (TOP) to 39 (BOTTOM)
background = "#222222" # default color of the empty space change if needed
TETROMINOS = [
        [[0, 0], [0, 1], [1, 0], [1,1]], # O
        [[0, 0], [0, 1], [1, 1], [2,1]], # L
        [[0, 1], [1, 1], [2, 1], [2,0]], # J 
        [[0, 1], [1, 0], [1, 1], [2,0]], # Z
        [[0, 0], [1, 0], [-1, 0], [0,1]], # T
        [[0, 0], [0, 1], [1, 1], [2,1]], # S
        [[0, 1], [1, 1], [2, 1], [3,1]], # I
    ]
COLORS = [
    "#75D9A0",   #Light Green
    "#FFE300",   #Yellow
    "#D17FD6",   #Purple
    "#EB2226",   #Red
    "#69DFDB",   #Cyan
    "#FA7036",   #Orange
    "#E8E8E8"    #Light Gray
    ]

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

def has_collided_with_bottom(obj):
    # Check if the object's bounding box extends beyond the bottom of the screen
    if obj.curr_pos[1] + obj.botPad >= 39:
        return True
    else:
        return False
    
def collided_with_bottom(obj):
    return checkOverlap(obj_playing, [obj.curr_pos[0], obj.curr_pos[1]+1])
# def obj_collided_with_ground(obj):
#     temp = tuple(obj.curr_pos)
#     offset(obj,[0,1])
#     if temp[0] == obj.curr_pos[0] and temp[1] == obj.curr_pos[1]:
#         return True
#     else:
#         offset(obj,[0,-1])
#         return False

def createTetromino():
    global shape_color, shape_playing
    shape_color = random.randint(0,6)
    shape_playing = list(tuple(TETROMINOS[random.randint(0,6)]))

    obj = object({
        COLORS[shape_color]: shape_playing
    },
    {
        "z_value": 4,
        "pos": [9,4],
        "collision": True,
        "stayInFrame": True,
        "rotation": True
    })
    return obj

def updateGame():
    global obj_playing, playing, shape_playing, shape_color, filled_pixels, Game_Over

    
    if (has_collided_with_bottom(obj_playing) or collided_with_bottom(obj_playing))and not Game_Over:
        # If collision with bottom, spawn a new tetromino
        temp = obj_playing.curr_pos
        objArr.remove(obj_playing)
        for item in shape_playing:
            obj3.changeColor([item[0]+temp[0],item[1]+temp[1]],COLORS[shape_color])
        while checkLineFull(getMatrix()) :
            i = line_filled
            while i>=6:
                for j in range(0,20):
                    if i ==6:
                        obj3.changeColor([j,i],None)
                    elif filled_pixels[i-1][j] not in COLORS:
                        obj3.changeColor([j,i],None)
                    else:
                        obj3.changeColor([j,i],filled_pixels[i-1][j])
                i -=1
        shape_playing = TETROMINOS[random.randint(0,6)]
        newTetromino = createTetromino()
        playing = True
        obj_playing = newTetromino
        objArr.append(newTetromino)
        temp2 = obj_playing.curr_pos
        offset(obj_playing,[0,1])
        if temp2 == obj_playing.curr_pos:
            Game_Over = True
        return False

def getMatrix():
    global transformed_matrix
    global filled_pixels
    grid = []
        
    row_temp = []
    for i in range(20):
        row_temp.append(background)
    for i in range(40):
        grid.append(row_temp.copy())

    for obj in objArr:
        # get the pixelArr
        pixelArr = obj.pixelArr
        # position of origin on screen
        pos = obj.curr_pos
        # making the needed squares on tkinter window
        # iterating through all pixels of the pixelArray
        for r in range(len(pixelArr)):
            for c in range(len(pixelArr[r])):
                onMatrixPos_x = c - obj.bound_origin[0] + obj.curr_pos[0]
                onMatrixPos_y = r - obj.bound_origin[1] + obj.curr_pos[1]
                if (onMatrixPos_x >= 0) and (onMatrixPos_x <= 19):
                    if (onMatrixPos_y >= 0) and (onMatrixPos_y <= 39):
                        if pixelArr[r][c] is not None:
                            grid[onMatrixPos_y][onMatrixPos_x] = pixelArr[r][c]

    transformed_matrix = []
    filled_pixels = tuple(grid)
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

    
   



# this functions is used to check collisions with the objects already present in objArr
def checkOverlap(obj, newPos):
    global objArr
    isOverLap = False
    for ob in objArr:
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

def offset(obj, offset):

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

def rotate(obj, amt):
    # this function rotates the given 'obj' by 'amt'
    # amt +1 = CCW by 90 degree ; +2 = CCW by 180 degree
    # amt -1 = CW  by 90 degree ; -2 = CW  by 180 degree
    if amt ==-1:
        for i in shape_playing:
            shape_playing[shape_playing.index(i)] = [-i[1],i[0]]
    elif amt ==1:
        for i in shape_playing:
            shape_playing[shape_playing.index(i)] = [i[1],-i[0]]
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

        if checkOverlap(obj,obj.curr_pos):
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
        print("txt length exceeded X pixel limit for the text = " + txt)
        return None
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

# =================================================================================================
# =================================================================================================

# define your games cross-frame variables here, these variables can store data and carry it across frames
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
count = 0
obj1 = None
obj2 = None
obj3 = None
shape_color = 0
line_filled = 0
Last_Empty_Line = 0
Game_Over = False
filled_pixels =[]
# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

def gameFrame(): # MAKE YOUR GAME IN THIS FUNCTIONS (will be called every frame)
    
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
    #   "collision" : True
    # }
    # 'z_value' : indicates the position of the object in z axis, higher the value further it is infront of the LED MATRIX,
    # thus 0 is at the back and 10 is infront if in any scenario two objects overlap z_value will decide which will be 
    # displayed infront
    # 'pos' : it represents the (X,Y) coordinate of the origin of the object on the LED MATRIX
    # 'stayInFrame' : a basic system that prevent the object from going out of bound 
    # 'collision' : a basic system that prevent the object from colliding with other objects
    # objects will collide only if offset() function is used and both the objects have "collision" set to True also both should
    # share the same layer (i.e. they have same zVal)
    # 
    # once you have created an object you must add it to the "objArr" list, only the objects in this list shall be rendered1
    # also the collision will be checked against the objects currently present in this list
    # if an object is spawned on top of another object such that both are COLLIDING it will disable both of them from moving
    # at all ... you'll have to kill the objects in such a scenario
    # to KILL an object just remove it from the "objArr" list
    # 
    # to move an object by (X,Y) units use offset function, remember this function takes input of the offset not the final position
    # to use the function follow this syntax
    # offset(object, [X,Y])
    # object = to the object that you want to move and [X,Y] is the offset vector
    #
    # if at some point you want to access the list of all pixels alongwith the colors just access the "matrix" variable you will need
    # to call it via global keyword "global matrix"
    #
    # to change the background color you may access the global "background" variable and change the color
    #
    # object.pixelArr will give you the relative matrix of the pixels of the particular matrix ... Access it but dont try to change it
    #
    # to change color of the pixels you may use "object.changeColor()" function in order to use this function you need to know the
    # location of the pixel the location should be same as you used while defining the object... use the following syntax
    # object.changeColor([X,Y], color)
    # color = HEX VALUE of the color you want to change it to
    #
    # you may make a pixel invisible by setting its color value to None instead of hex value
    # by accessing pixelArr you will find out that each object has a rectangular pixelArr and many of the pixels are set to be invisible
    # you may bring them to life by setting them to some colorValue
    #
    # WARNING : if you try to access pixel that does not exist in pixelArr you will get errors
    # WARNING : making pixels visible / invisible wont change their collision behaviour... this can be used to create sort of invisible
    # maze like structure (imaginations are on you!!)
    #
    # ========
    # txtObj
    # ======== 
    #
    # to write text use txtObj it is capable of writing the following characters
    #
    # 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ +-*/
    #
    # all of these characters are 5 pixel high and 3 pixel wide 
    # except "1" which is 2 pixel wide
    # M,W,Q which are 6 pixel wide each
    # and N which is 4 pixel wide
    #
    # SYNTAX: obj = txtObj(txt, cursor, fill, zValue, stayInFrame)
    # txt = string text
    # cursor = location of the top left corner of the text
    # fill = color of the text
    # zValue, stayInFrame = as explained above
    #
    # WARNING : if the text overflows on the X axis an error will be displayed !! 
    #
    # ========
    # lineObj
    # ========
    #
    # make line from one point to another
    # diagonal lines wont look good if not 45 degrees as pixel count is low
    # 
    # SYNTAX: obj = lineObj(C1, C2, fill, zValue, stayInFrame)
    # C1 = [X,Y] = position of point 1
    # C2 = [X,Y] = position of point 2
    # fill, zValue, stayInFrame = as explained above
    #
    # ==============
    # rectangleObj
    # ==============
    #
    # makes a rectangle where the opposite points of the same diagonal are specified
    # SYNTAX: obj = rectangleObj(C1, C2, fill, zValue, stayInFrame)
    # C1, C2 = position of the two opposite diagonal points
    # fill, zValue, stayInFrame = as eplained above
    #
    # each of the lineObj, rectangleObj and txtObj return the object which shall be stored in a variable and then added to the "objArr"
    # to render it to the screen
    #
    # again individual colors can be changed by treating these objects like normal objects ... through understanding of their
    # pixelArr might be needed (rectangleObj is simpler while txtObj, lineObj return much more complex array of pixels)
    #
    # to take keyboard keyDown Input use the following syntax
    # z = getKeyState("<KEY NAME>")
    # z will be True while the key is held down and False otherwise
    # this input is highly sensitive in order to decrease the senstivity you will have to do it yourself one of the ways i suggest is:
    # keep some constant value "k" and if the key is held down constantly for "k" frames you may register the input
    # higher the "k" the longer it will take to register the click and thus lower the senstivity 
    # 
    # See the following demo project to understand better everything inside the "if once:" block will run exactly once per game while
    # in the "else:" block it will run once per frame
    # it is advised to create the initial objects in the "if once:" block and put the actual game logic in the "else:" block
    # although you may go however you feel like
    #
    # WARNING : dont mess with with anything outside the region intended for your use 

    # get your cross frame variables in this function using 'global' keyword HERE
    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

    global once
    global count
    global obj1
    global obj2
    global obj3
    global obj_playing
    global matrix
    global shape_color
    global shape_playing
    global line_filled
    global Last_Empty_Line
    global filled_pixels
    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    if once:
        # CODE IN HERE RUNS ONCE PER GAME
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        once = False
        gameover = False
        obj1 = object({
            "#00ff00": [[-1,0],[1,0],[0,1],[0,2]],
            "#ffffff": [[0,0]]
            },
            {
                "z_value": 4,
                "pos": [11,25],
                "collision" : True,
                "stayInFrame": True
            })
        obj2 = object({
            "#00ffff": [[1,0],[2,0],[0,1],[0,2]],
            "#ff0000": [[0,0]]
            },
            {
                "z_value": 4,
                "pos": [5,30],
                "collision" : True
            })
        obj_I = object({
            "#75D9A0": [[0,0],[0,1],[0,2],[0,3]]
        },
        {
            "z_value": 4,
            "pos": [4, 12],
            "collision" : True,
            "stayInFrame": True,
            "rotation": True
        })
        obj_O = object({
            "#FFE300": [[0,0],[0,1],[1,0],[1,1]]
        },
        {
            "z_value": 4,
            "pos": [4,4],
            "collision": True,
            "stayInFrame": True,
            "rotation": True
        })
        obj_L = object({
            "#D17FD6": [[0,0],[0,1],[0,2],[1,2]]
        },
        {
            "z_value": 4,
            "pos": [8,4],
            "collision": True,
            "stayInFrame": True,
            "rotation": True
        })
        obj_J = object({
            "#EB2226": [[1,0],[1,1],[1,2],[0,2]]
        },
        {
            "z_value": 4,
            "pos": [8,16],
            "collision": True,
            "stayInFrame": True,
            "rotation": True
        })
        obj_Z = object({
            "#69DFDB": [[0,0],[1,0],[1,1],[2,1]]
        },
        {
            "z_value": 4,
            "pos": [16,12],
            "collision": True,
            "stayInFrame": True,
            "rotation": True
        })
        obj_T = object({
            "#FA7036": [[0,2],[1,1],[1,2],[2,2]]
        },
        {
            "z_value": 4,
            "pos": [16,8],
            "collision": True,
            "stayInFrame": True,
            "rotation": True
        })
        obj_S = object({
            "#E8E8E8": [[0,1],[1,0],[1,1],[2,0]]
        },
        {
            "z_value": 4,
            "pos": [16,4],
            "collision": True,
            "stayInFrame": True,
            "rotation": True
        })
        obj3 = rectangleObj([0,0],[19,39], fill=None,zValue=4,stayInFrame=True, collision=True)
        # obj_playing = tetrominos[random.randint(0,6)]
        obj_playing = createTetromino()
        objArr.append(obj3)
        objArr.append(obj_playing)

        # objNew = tetrominos[random.randint(0,6)]
        # objArr.append(objNew)
        
        # line1 = txtObj("BY",[0,4],"#ffffff",10,True)
        # line2 = txtObj("AYUSH",[0,8],"#ffffff",10,True)
        # line3 = txtObj("YADAV",[0,12],"#ffffff",10,True)
        # for x in line.pixelArr:
        #     print(x)
        # objArr.append(obj2)
        # objArr.append(obj1)
        
        # objArr.append(line1)
        # objArr.append(line2)
        # objArr.append(line3)

        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ 
        # CODE IN HERE RUNS ONCE PER FRAME
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

            


                
    else:

        # print(len(objArr))
                
        if getKeyState('a') and not Game_Over:
            offset(obj_playing, [-1,0])
        if getKeyState('d') and not Game_Over:
            offset(obj_playing, [1,0])
        if getKeyState('s') and not Game_Over:
            offset(obj_playing, [0,1])
        if getKeyState('right') and not Game_Over:
            rotate(obj_playing, -1)
        if getKeyState('Left') and not Game_Over:
            rotate(obj_playing,1)
        updateGame()
        offset(obj_playing, [0,1])
        



# ================================================
# DO NOT MESS FROM HERE ON
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

def renderFrame(cv, side):
    global objArr, matrix
    # make LED MATRIX with default color
    matrix = []
    
    row_temp = []
    for i in range(20):
        row_temp.append(background)
    for i in range(40):
        matrix.append(row_temp.copy())
    
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
        
    # iterating through all objects and updating the matrix grid
    for obj in objArr:
        # get the pixelArr
        pixelArr = obj.pixelArr
        # position of origin on screen
        pos = obj.curr_pos
        # making the needed squares on tkinter window
        # iterating through all pixels of the pixelArray
        for r in range(len(pixelArr)):
            for c in range(len(pixelArr[r])):
                onMatrixPos_x = c - obj.bound_origin[0] + obj.curr_pos[0]
                onMatrixPos_y = r - obj.bound_origin[1] + obj.curr_pos[1]
                if (onMatrixPos_x >= 0) and (onMatrixPos_x <= 19):
                    if (onMatrixPos_y >= 0) and (onMatrixPos_y <= 39):
                        if pixelArr[r][c] is not None:
                            matrix[onMatrixPos_y][onMatrixPos_x] = pixelArr[r][c]
    # for x in matrix:
    #     print(x)
    # z = int(input(""))

    # painting the tkinter output screen as per matrix array
    cv.delete("all") # clear screen
    for r in range(40):
        for c in range(20):
            Xi = c*side + 10
            Xf = c*side + side + 10
            Yi = r*side + 10
            Yf = r*side + side + 10
            temp = cv.create_rectangle(Xi, Yi, Xf, Yf, fill=matrix[r][c])
    # print(matrix)


# main loop of the game will run every frame
def nxtFrame(root, cv, sc):
    global end
    global currTime
    global timeGone

    if not end:
        gameFrame()

        renderFrame(cv, sc)

        rT = time.time()
        deltaTime = rT - currTime
        currTime = rT
        timeGone += deltaTime
        # print(timeGone, deltaTime)

        # RECALL the nxt frame function to
        root.after(100, nxtFrame, root, cv, sc)
    else:
        # tk mainloop will end now
        pass


# beginning tkinter output window
# sc = int(input("ENTER cell size for SCREEN OUTPUT : ")) * 2
sc = 14 # DEBUG

# declaring basic window
root = tk.Tk()
root.title("TETRIS")
root.geometry(str(20*sc+20)+"x"+str(40*sc+20))

cv = tk.Canvas(root, width=20*sc+20, height=40*sc+20)
cv.pack()

# cv.create_rectangle(0, 0, 420, 820, fill="#ff0000", outline="black")

# will start the frame by frame stuff 35ms delay shall create an almost 30FPS scenario
root.after(10, nxtFrame, root, cv, sc)

# Tk WINDOW
root.mainloop()
#######BUGS#########
# block can pass thru screen at boundaries durinng rotate
