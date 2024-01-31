import tkinter as tk
import keyboard # for getting key inputs
import time
import random

# =============================================
# IMPORT ANY LIBRARY YOU WANT HERE
# =============================================
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

# import

# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

# SOME ASSUMPTIONS
# X values are the column numbers starting from 0 (LEFT) to 19 (RIGHT)
# Y values are the row numbers starting from 0 (TOP) to 39 (BOTTOM)
background = "#1f0214" # default color of the empty space change if needed

class object:
    # This class consists of one object (i.e. group of colored pixels)
    # the object acts as a incompressible / indestructible entity that can translate and rotate in space
    # the object structure is defined as follows
    # assume the object's origin to be at the origin of cartesian system then make a dictionary as follows
    # {
    #   "hexValueOfColor" : [(x1,y1),(x2,y2),(x3,y3)], 
    #   "hexValueOfColor" : [(x1,y1),(x2,y2),(x3,y3)], 
    #   "hexValueOfColor" : [(x1,y1),(x2,y2),(x3,y3)],
    #   ...
    # }
    # There can be many pixels of same color thus the above coloring system is taken
    # color of indivisual pixel can be changed lateron using the function provided in this class [not recommended though
    # considering the simplicity of our display aka LED MATRIX]
    # 'data' is a dictionary consisting of the following
    # {
    #   "z_value" : int,
    #   "pos" : [int, int],
    #   "stayInFrame" : True
    # }
    # 'z_value' : indicates the position of the object in z axis, higher the value further it is infront of the LED MATRIX,
    # thus 0 is at the back and 10 is infront if in any scenario two objects overlap z_value will decide which will be 
    # displayed infront
    # 'pos' : it represents the (X,Y) coordinate of the origin of the object on the LED MATRIX
    # 'stayInFrame' : a basic system that prevent the object from going out of bound 
    # 'collision' : a basic system that prevent the object from going out of bound 

    # OBJECT VARIABLES
    curr_pos = [0,0] # default value
    pixelArr = [] # consists of the hexadecial values of the pixels relative to origin ROW-WISE (top row first)
    bound_origin = [0,0] # the origin wrt the bounding box
    zVal = 0 # the location of object outward from the plane (Z position)
    frameCollision = False # turned True when bound collision is enabled
    collision = False # turned True when collision is enabled

    # other variables
    topPad = 0
    botPad = 0
    lefPad = 0
    rigPad = 0
    minY = 0
    maxY = 0
    minX = 0
    maxX = 0

    def getBoundingBox(self, arr):
        self.minY = None
        self.maxY = None
        self.minX = None
        self.maxX = None

        firstTime = True

        for key in arr.keys():
            for coord in arr[key]:
                
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
        
        return [self.maxX-self.minX+1, self.maxY-self.minY+1]
    
    def calcPadding(self):
        self.lefPad = self.bound_origin[0]
        self.rigPad = len(self.pixelArr[0]) - self.bound_origin[0] - 1
        self.topPad = self.bound_origin[1]
        self.botPad = len(self.pixelArr) - self.bound_origin[1] - 1

    def __init__(self, obj, data):
        # here 'obj' holds the dictionary of colored pixels thus defining the object
        # 'data' consists of other data as was stated above, these values are used to define the behaviour of this object
        # making the blank pixel array

        size = self.getBoundingBox(obj) # getting order of matrix

        self.pixelArr = []
        # making one row
        row_temp = []
        for i in range(size[0]):
            row_temp.append(None)
        # adding these rows in pixel array to create the blank array
        for i in range(size[1]):
            self.pixelArr.append(row_temp.copy())

        # getting midpoint of the object and updating bound origin
        boundX = 0
        boundY = 0

        if self.minX < 0:
            boundX = -self.minX
        else:
            boundX = 0
        
        if self.minY < 0:
            boundY = -self.minY
        else:
            boundY = 0
        
        self.bound_origin = [boundX, boundY]
        
        # coloring apropriate pixels
        #   iterating through the dictionary and coloring the pixels
        for k in obj.keys():
            for coord in obj[k]:
                # here k stores the hexadecimal value of the color and coord are the relative coordinated of pixels
                arrCoord_X = self.bound_origin[0] + coord[0]
                arrCoord_Y = self.bound_origin[1] + coord[1]
                self.pixelArr[arrCoord_Y][arrCoord_X] = k

        self.calcPadding() # calculate padding
        
        # assigning other variables
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

# this functions is used to check collisions with the objects already present in objArr
def checkOverlap(obj, newPos):
    global objArr
    isOverLap = False
    for ob in objArr:
        if ob.collision and (ob != obj) and (ob.zVal == obj.zVal):
            for y in range(len(ob.pixelArr)):
                for x in range(len(ob.pixelArr[y])):
                    if ob.pixelArr[y][x] is not None:
                        coordX = x + ob.bound_origin[0] + ob.curr_pos[0]
                        coordY = y + ob.bound_origin[1] + ob.curr_pos[1]

                        for yN in range(len(obj.pixelArr)):
                            for xN in range(len(obj.pixelArr[yN])):
                                if obj.pixelArr[yN][xN] is not None:
                                    coordNX = xN - obj.bound_origin[0] + newPos[0]
                                    coordNY = yN - obj.bound_origin[1] + newPos[1]

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
    # once you have created an object you must add it to the "objArr" list, only the objects in this list shall be rendered
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
    global countm
    global flagc
    global bs1
    global obj2
    global obj3
    global obj4
    global obj5
    global obj6

    global objArr 

    global bul1
    global bul2
    global bul3   

    global ran
    global Index
    global life

    global heart1
    global heart2
    global heart3

    global gameStart

    global Mon1
    global Mon2
    global Mon3

    global Space
    global Invader

    global GameFlag
    global line
    global line1
    global line2
    global line3

    global bul1
    global bul2
    global bul3

    global heart1
    global heart2
    global heart3 
    
    global backg
    global back1
    global back2
    global back3
    global back4
    global back5
    global back6
    global back7
    global back8
    global back9
    global back10
    global back11
    global back12
    global back13
    global back14
    global back15
    global back16
    global back17
    global back18
    global back19
    global back20
    global back21
    global back22
    global back23
    global back24
    global back25
    global back25
    global back26
    global back27
    global back28
    global back29
    global back30
    global back31
    global back32
    global back33
    global back34

    global Ga3
    global Ga2
    global Ga1
    global Gf3
    global Gf2
    global Gf1
    global Gf0

    global score
    global Scoreobj
    global scoreflag
    global endflag
    global gameEnd

    global GameOver1
    global GameOver2


   
    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    if once:

        # CODE IN HERE RUNS ONCE PER GAME
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        once = False
        
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
                "z_value": 2,
                "pos": [-35, 29],
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
                "z_value": 2,
                "pos": [55, 21],
                "collision" : False
            })
        Mon3  = object({  #design
            "#f5a15d": [[0,0], [-2,0], [2,0], [0,1], [-1,1], [-2,1], [1,1], [2,1], [0,-1], [-1,-1], [-2,-1], [1,-1], [2,-1], [-4,-1], [4,-1], [-2,-2], [2, -2], 
                        [0,-3], [-4,-3], [4,-3], [0,-4], [-2,-4], [2,-4], [-2,-5], [2,-5], [-4,-5], [4,-5], [-4,-6], [4,-6], [-2,-7], [2,-7], [-4,-8], [4,-8]],
            "#c6d831": [[0,2], [-1,2], [1,2], [0,3], [-3,0], [3,0], [-3,-1], [3,-1], [-3,-2], [3,-2], [-4,-2], [4,-2], [-1,-4], [1,-4]],
            "#401102": [[-1,0], [1,0]]
            },
            {
                "z_value": 2,
                "pos": [9, -50],
                "collision" : False
            })
        line = lineObj([0,5],[20,5], "#7a0000", 1, True)
        # line1 = txtObj("G",[1,6],"#c6d831",2,True)
        # line2 = txtObj("R",[1,12],"#c6d831",2,True)
        # line3 = txtObj("C",[1,18],"#c6d831",2,True)
        Space = txtObj("SPACE", [0,-8], "#f002e8", 2, False)
        Invader = txtObj("NVDR", [2,-2], "#f002e8", 2, False)

        #I just have too much time at this point
        backg = rectangleObj([0,0], [20,4], "#290023", 5, True)
        back1 = rectangleObj([0,6], [20,6], "#8002bf", 1, True)
        back2 = rectangleObj([0,7], [20,7], "#7d02bf", 1, True)
        back3 = rectangleObj([0,8], [20,8], "#7702bf", 1, True)
        back4 = rectangleObj([0,9], [20,9], "#7002bf", 1, True)
        back5 = rectangleObj([0,10], [20,10], "#6a02bf", 1, True)
        back6 = rectangleObj([0,11], [20,11], "#6402bf", 1, True)
        back7 = rectangleObj([0,12], [20,12], "#5d02bf", 1, True)
        back8 = rectangleObj([0,13], [20,13], "#5702bf", 1, True)
        back9 = rectangleObj([0,14], [20,14], "#5102bf", 1, True)
        back10 = rectangleObj([0,15], [20,15], "#4a02bf", 1, True)
        back11 = rectangleObj([0,16], [20,16], "#4402bf", 1, True)
        back12 = rectangleObj([0,17], [20,17], "#3e02bf", 1, True)
        back13 = rectangleObj([0,18], [20,18], "#3802bf", 1, True)
        back14 = rectangleObj([0,19], [20,19], "#3102bf", 1, True)
        back15 = rectangleObj([0,20], [20,20], "#0802bf", 1, True)
        back16 = rectangleObj([0,21], [20,21], "#0202bf", 1, True)
        back17 = rectangleObj([0,22], [20,22], "#0208bf", 1, True)
        back18 = rectangleObj([0,23], [20,23], "#020fbf", 1, True)
        back19 = rectangleObj([0,24], [20,24], "#0215bf", 1, True)
        back20 = rectangleObj([0,25], [20,25], "#021bbf", 1, True)
        back21 = rectangleObj([0,26], [20,26], "#0221bf", 1, True)
        back22 = rectangleObj([0,27], [20,27], "#0228bf", 1, True)
        back23 = rectangleObj([0,28], [20,28], "#023bbf", 1, True)
        back24 = rectangleObj([0,29], [20,29], "#0247bf", 1, True)
        back25 = rectangleObj([0,30], [20,30], "#0254bf", 1, True)
        back26 = rectangleObj([0,31], [20,31], "#0260bf", 1, True)
        back27 = rectangleObj([0,32], [20,32], "#026abf", 1, True)
        back28 = rectangleObj([0,33], [20,33], "#0273bf", 1, True)
        back29 = rectangleObj([0,34], [20,34], "#027dbf", 1, True)
        back30 = rectangleObj([0,35], [20,35], "#0286bf", 1, True)
        back31 = rectangleObj([0,36], [20,36], "#028dbf", 1, True)
        back32 = rectangleObj([0,37], [20,37], "#0299bf", 1, True)
        back33 = rectangleObj([0,38], [20,38], "#02a3bf", 1, True)
        back34 = rectangleObj([0,39], [20,39], "#02b2bf", 1, True)
       #Why did i do that? i dont know.. I just dont know
        

        Ga3 = txtObj("3", [8, 18], "#020d59", 2, False)
        Ga2 = txtObj("2", [8, 18], "#020d59", 2, False)
        Ga1 = txtObj("1", [9, 18], "#020d59", 2, False)
        Scoreobj = txtObj(str(score), [1, 0], "#f59905", 6, True)
        
        # for x in line.pixelArr:
        #     print(x)
       
        objArr.append(Mon1)
        objArr.append(Mon2)
        objArr.append(Mon3)
        objArr.append(Space)
        objArr.append(Invader)
        
        
        
        
        
        Index = len(objArr)-1
        gameStart = time.time()

        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑ 
    elif(currTime-gameStart <3):
        offset(Mon1, [1,0])    
        offset(Mon2, [-1,0]) 
        offset(Mon3, [0,2])
        offset(Space, [0,1])
        offset(Invader, [0,1])
    elif(currTime-gameStart >=3 and currTime-gameStart<4):
        if (GameFlag ==1):
            GameFlag = 0
            objArr.append(obj2)
            objArr.append(bs1)
            objArr.append(obj3)
            objArr.append(obj4)
            objArr.append(obj5)
            objArr.append(obj6)
            # objArr.append(line1)
            # objArr.append(line2)
            # objArr.append(line3)
            objArr.append(line)
            objArr.append(bul1)
            objArr.append(bul2)
            objArr.append(bul3)
            objArr.append(heart1)
            objArr.append(heart2)
            objArr.append(heart3)
            objArr.append(backg)
            objArr.append(back1)
            objArr.append(back2)
            objArr.append(back3)
            objArr.append(back4)
            objArr.append(back5)
            objArr.append(back6)
            objArr.append(back7)
            objArr.append(back8)
            objArr.append(back9)
            objArr.append(back10)
            objArr.append(back11)
            objArr.append(back12)
            objArr.append(back13)
            objArr.append(back14)
            objArr.append(back15)
            objArr.append(back16)
            objArr.append(back17)
            objArr.append(back18)
            objArr.append(back19)
            objArr.append(back20)
            objArr.append(back21)
            objArr.append(back22)
            objArr.append(back23)
            objArr.append(back24)
            objArr.append(back25)
            objArr.append(back26)
            objArr.append(back27)
            objArr.append(back28)
            objArr.append(back29)
            objArr.append(back30)
            objArr.append(back31)
            objArr.append(back32)
            objArr.append(back33)
            objArr.append(back34)
            objArr.append(Scoreobj)
    elif(currTime-gameStart>=4 and currTime-gameStart<5):
        if(Gf3 == 1):
            Gf3 = 0
            objArr.append(Ga3)
    elif(currTime-gameStart>=5 and currTime-gameStart<6):
        if(Gf2 == 1):
            Gf2 = 0
            objArr.pop(objArr.index(Ga3))
            objArr.append(Ga2)
    elif(currTime-gameStart>=6 and currTime-gameStart<7):
        if(Gf1 == 1):
            Gf1 = 0
            objArr.pop(objArr.index(Ga2))
            objArr.append(Ga1)
    elif(currTime-gameStart>=7 and currTime-gameStart<8):
        if(Gf0 == 1):
            Gf0 = 0
            objArr.pop(objArr.index(Ga1))




    elif (life>0):
        gameEnd = time.time()
        # CODE IN HERE RUNS ONCE PER FRAME
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        count += 1
        if count == 3:
            count = 0
            # offset(obj1, [-1,0])
            offset(obj2, [0,1])
            offset(obj3, [0,1])
            offset(obj4, [0,1])
            offset(obj5, [0,1])
            offset(obj6, [0,1])
            offset(bul1, [0,-6])
            offset(bul2, [0,-6])
            offset(bul3, [0,-6])
            countm +=1
            
        if countm ==5:
            countm = 0
            if flagc ==1 :
                flagc = 0
                life-=1
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
            if obj2.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj2,[ran, 0])
            else: offset(obj2,[-ran,0])
        if obj3.curr_pos[1] >= 40:
            offset(obj3, [0, -36])
            if obj3.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj3,[ran, 0])
            else: offset(obj3,[-ran,0])
        if obj4.curr_pos[1] >= 40:
            offset(obj4, [0, -36])
            if obj4.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj4,[ran, 0])
            else: offset(obj4,[-ran,0])
        if obj5.curr_pos[1] >= 40:
            offset(obj5, [0, -36])
            if obj5.curr_pos[0]<=10:
                ran = random.randint(0,10)
                offset(obj5,[ran, 0])
            else: offset(obj5,[-ran,0])
        if obj6.curr_pos[1] >= 40:
            offset(obj6, [0, -36])
            if obj6.curr_pos[0]<=10:
                ran = random.randint(0,10)
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
        if (bs1.curr_pos[0] == obj2.curr_pos[0]):
            if(bs1.curr_pos[1]-obj2.curr_pos[1]<=5 and bs1.curr_pos[1]-obj2.curr_pos[1]>=0 ):
                flagc =1
        if (bs1.curr_pos[0] == obj3.curr_pos[0]):
            if(bs1.curr_pos[1]-obj3.curr_pos[1]<=5 and bs1.curr_pos[1]-obj3.curr_pos[1]>=0 ):
                flagc =1
        if (bs1.curr_pos[0] == obj4.curr_pos[0]):
            if(bs1.curr_pos[1]-obj4.curr_pos[1]<=5 and bs1.curr_pos[1]-obj4.curr_pos[1]>=0 ):
                flagc =1
        if (bs1.curr_pos[0] == obj5.curr_pos[0]):
            if(bs1.curr_pos[1]-obj5.curr_pos[1]<=5 and bs1.curr_pos[1]-obj5.curr_pos[1]>=0 ):
                flagc =1
        if (bs1.curr_pos[0] == obj6.curr_pos[0]):
            if(bs1.curr_pos[1]-obj6.curr_pos[1]<=5 and bs1.curr_pos[1]-obj6.curr_pos[1]>=0 ):
                flagc =1
        
        if (abs(bs1.curr_pos[0]-obj2.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj2.curr_pos[1]<=3 and bs1.curr_pos[1]-obj2.curr_pos[1]>=0 ):
                flagc =1
        if (abs(bs1.curr_pos[0]-obj3.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj3.curr_pos[1]<=3 and bs1.curr_pos[1]-obj3.curr_pos[1]>=0 ):
                flagc =1
        if (abs(bs1.curr_pos[0]-obj4.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj4.curr_pos[1]<=3 and bs1.curr_pos[1]-obj4.curr_pos[1]>=0 ):
                flagc =1
        if (abs(bs1.curr_pos[0]-obj5.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj5.curr_pos[1]<=3 and bs1.curr_pos[1]-obj5.curr_pos[1]>=0 ):
                flagc =1
        if (abs(bs1.curr_pos[0]-obj6.curr_pos[0]))==1:
            if(bs1.curr_pos[1]-obj6.curr_pos[1]<=3 and bs1.curr_pos[1]-obj6.curr_pos[1]>=0 ):
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
        

    elif(currTime-gameEnd<3 and currTime>gameEnd):
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
        offset(GameOver1, [0,-1])
        offset(GameOver2, [0,1])
            
    else:
        if(endflag == 0):
            endflag = 1
            Scoreobj = txtObj(str(score), [8, 22], "#bc3ff2", 6, True)
            EndScore = txtObj("SCORE", [0, 16], "#bc3ff2", 2, False)
            objArr.pop(objArr.index(GameOver1))
            objArr.pop(objArr.index(GameOver2))
            objArr.append(Scoreobj)
            objArr.append(EndScore)

             #↑↑↑↑↑↑↑↑↑↑↑↑SHOT DOWN↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
        

        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

# ================================================
# DO NOT MESS FROM HERE ON
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

def renderFrame(cv, side):
    global objArr
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
root.after(35, nxtFrame, root, cv, sc)

# Tk WINDOW
root.mainloop()
