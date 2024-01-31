import tkinter as tk
import keyboard # for getting key inputs
import time
import random
import math
# =============================================
# IMPORT ANY LIBRARY YOU WANT HERE
# =============================================
# ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

# import

# ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

# SOME ASSUMPTIONS
# X values are the column numbers starting from 0 (LEFT) to 19 (RIGHT)
# Y values are the row numbers starting from 0 (TOP) to 39 (BOTTOM)
background = "#000000" # default color of the empty space change if needed

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
                for c in range(abs(dY)):
                    j = [j[0], j[1] + Ydir]
                    pointArr.append(j)
    
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
game_time = 10
targets_hit = []
targets_missed = []
target_timer = 4
game_start_time = 0
target_spawn_time = 0
game_over = None
crosshair = None
target = None
obj3 = None
hit_animation =None
endscreenline1 = None
score = 0
startscreen = True
endscreen = True
speedupgame=2 #speed up game every n successful hits 
score_addr = 50
score_subtr = 25

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
    global crosshair
    global target
    global obj3
    global objArr
    global targets_hit
    global targets_missed
    global target_timer
    global game_start_time
    global game_time
    global target_spawn_time
    global game_over
    global speedupgame
    global score
    global score_addr
    global score_subtr
    global endscreen
    global startscreen      
    global endscreenline1

    def reColor(o):
        pA = o.pixelArr
        for y in range(len(pA)):
            for x in range(len(y)):
                if pA[y][x] is not None:
                    o.pixelArr[y][x] = "new color"
    

    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    if once:

        # CODE IN HERE RUNS ONCE PER GAME
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        once = False
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
            "#ff0000": [[1,0],[1,1],[0,1],[0,-1],[-1,-1],[1,-1],[-1,1],[-1,0]],
            "#ffff00": [[0,0]]
            },
            {
                "z_value": 1,
                "pos": [random.randint(1,18),random.randint(4,38)],
                "collision" : True
            })
        obj3 = rectangleObj([0,0],[19,39], fill=None,zValue=3,stayInFrame=True, collision=True)
        # obj3 = object({
        #     "#ff0000": [[1,0],[1,1],[0,1],[0,-1],[-1,-1],[1,-1],[-1,1],[-1,0]],
        #     None: [[0,0]]
        #     },
        #     {
        #         "z_value": 4,
        #         "pos": [random.randint(1,18),random.randint(4,38)],
        #         "collision" : True
        #     })

        objArr.append(crosshair)
        objArr.append(target)
        objArr.append(obj3)
        # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑  
        game_start_time = time.time()
        target_spawn_time = time.time()      
    else:
        # CODE IN HERE RUNS ONCE PER FRAME
        # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
        count += 1
        if startscreen:
            print("welcome")
            startscreen = False
        if not game_over and not startscreen:
            game_over = bool(game_time <= (currTime - game_start_time))
            if count == 35:
                count = 0
                # if targets_hit>10:
                #     offset(target, [0,0])#useful if i want moving targets
                print(len(targets_hit),len(targets_missed))
            if getKeyState("A") and not game_over:
                offset(crosshair, [-1,0])
            if getKeyState("D") and not game_over:
                offset(crosshair, [1,0])
            if getKeyState("W") and not game_over:
                offset(crosshair, [0,-1])
            if getKeyState("S") and not game_over:
                offset(crosshair, [0,1])
            if (crosshair.curr_pos == target.curr_pos) and getKeyState(" ") and not game_over :
                targets_hit.append(target.curr_pos)
                score += score_addr
                game_time +=2
                speedupgame -= 1
                print("HIT\nScore:",score)
                target.curr_pos = [random.randint(1,18),random.randint(4,38)]
                if speedupgame == 0:
                    speedupgame = 2
                    if score_addr<100:
                        score_addr += 25                    
                    if target_timer >1:
                        target_timer -= 0.5
                    if (score_subtr-10)>0:
                        score_subtr -=10
                    else:
                        score_subtr = 0
                if speedupgame == 5:
                    speedupgame = 2
                    if target_timer <2.5:
                        target_timer += 0.25
                    if (score_subtr+10)<40:
                        score_subtr +=10 
                    else:
                        score_subtr = 40

                target_spawn_time = time.time()
            if target_timer <=(time.time() - target_spawn_time) and not game_over:
                print("MISS")
                targets_missed.append(target.curr_pos)
                score -= score_subtr
                target.curr_pos = [random.randint(1,18),random.randint(4,38)]
                target_spawn_time = time.time()
                speedupgame +=1 
        else: 
            if count ==40:
                count =0
                print(score)
            if endscreen:
                endscreen = False
                objArr.remove(crosshair)
                objArr.remove(target)
                print(targets_hit)

                for i in targets_hit:
                    obj3.changeColor(i, "#00ff00")
                for i in targets_missed:
                    print(i)
                    if i in targets_hit:
                        obj3.changeColor(i,"#FFA500")
                    else:
                        obj3.changeColor(i,"#ff0000")

                #objArr.append(endscreenline1)

        # if  game_time <= (currTime - game_start_time):
                
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
