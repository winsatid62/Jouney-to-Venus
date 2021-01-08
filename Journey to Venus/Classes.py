# Jittipat Shobbakbun
# 01/08/2021
# Classes.py

import time
import curses
import math

class my_stdscr:
    '''my own class for display'''
    def __init__(self, stdscr, screenWidth, screenHeight):
        self.stdscr = stdscr
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

    def setScreenWidth(self, screenWidth):
        '''sets screen width of the window'''
        self.screenWidth = screenWidth

    def setScreenHeight(self, screenHeight):
        '''sets screen height of the window'''
        self.screenHeight = screenHeight

    def get_stdscr(self):
        '''gets the main window'''
        return self.stdscr

    # original functions
    def nodelay(self, flag):
        self.stdscr.nodelay(flag)

    def erase(self):
        self.stdscr.erase()

    def addstr(self, *args):
        self.stdscr.addstr(*args)

    def noutrefresh(self):
        self.stdscr.noutrefresh()

    # custom functions
    def relativeAddtext(self, y, x, text):
        '''add text to the screen with relative position y,x instead of absolute position'''
        self.stdscr.addstr(math.floor(self.screenHeight*y), math.floor(self.screenWidth*x)-math.ceil(len(text)/2), str(text))
        return math.floor(self.screenHeight*y), math.floor(self.screenWidth*x)

    def hline(self, y, x, character, n):
        '''add a horizontal line of n character that start at row y colum x to screen stdscr'''
        for i in range(n):
            self.stdscr.addch(y,x+i,character)

class Thing:
    def __init__(self, name, flavor, flavor2):
        self.name = str(name)
        self.flavor = str(flavor)
        self.flavor2 = flavor2

    def __eq__(self,other):
        return self.name == other.name

    def __repr__(self):
        return self.name

    def getName(self):
        '''gets room's name'''
        return self.name

    def getFlavor(self):
        '''gets room's description'''
        return self.flavor

    def getFlavor2(self):
        '''gets room's detail description'''
        return self.flavor2

    def setName(self, name):
        '''sets room's name'''
        self.name = str(name)

    def setFlavor(self, flavor):
        '''sets room's description'''
        self.flavor = str(flavor)

    def setFlavor2(self, flavor):
        '''sets room's detail description'''
        self.flavor = str(flavor2)

    # Commands
    def look(self):
        '''return room's respond to LOOK command'''
        return self.flavor

    def inspect(self):
        '''return room's respond to INSPECT command'''
        return self.flavor2

class MapNode(Thing):
    def __init__(self, name, flavor, flavor2, firstImpression = None):
        super().__init__(name, flavor, flavor2)
        self.objectList = []
        self.firstImpression = firstImpression
        self.explored = False

    def addObject(self, *args):
        '''add multiple objects to the node'''
        for object in args:
            self.objectList.append(object)

    def setFirstImpression(self, firstImpression):
        '''sets the node's first impression (OPTIONAL FEATURE)'''
        self.firstImpression = firstImpression

    def getFirstImpression(self):
        '''gets the node's first impression (OPTIONAL FEATURE)'''
        return self.firstImpression

    # commands
    def look(self):
        if self.explored == False:
            return self.firstImpression
        else:
            return self.flavor

class Module(Thing):
    '''class for ship modules'''
    def __init__(self, name, flavor, flavor2, loc, ship = None, isRing = False):
        super().__init__(name, flavor)
        self.loc = loc
        self.isRing = isRing
        if isRing:
            self.ringModules = {"U":None, "D":None, "L":None, "R":None}
        else:
            self.objectList = []
        if ship != None:
            self.ship = ship
            if loc > len(ship)-1:
                for i in range(loc):
                    if i > len(ship)-1:
                        ship.append(None)
                ship.append(self)
            else:
                ship[loc] = self
            if loc == 0:
                self.back = None
            else:
                self.back = ship[loc-1]
                self.back.front = self
            if len(ship) == loc+1:
                self.front = None
            else:
                self.front = ship[loc+1]
                self.front.back = self

    def __repr__(self):
        return str(self.name)

    def getFront(self):
        '''gets the module in front'''
        return self.front

    def getBack(self):
        '''gets the module in the back'''
        return self.back

    def getShip(self):
        '''gets the ship the module is in'''
        return self.ship

    def getLoc(self):
        '''gets the location(index) of the module'''
        return self.loc

    def getRingMod(self):
        '''gets the dictionary of modules in the ring'''
        if self.ring:
            return self.ringModules
        else:
            return None

    def setRingModules(self):
        '''gets the name of the module'''
        return

    def printShip(self):
        '''return a string of the ship the module is in'''
        text = ""
        for module in ship:
            text += str(module.getName(), end=" - ")
        return text

    def setLoc(self, loc):
        '''sets the location of the module (replace original location with ship[loc])'''
        if loc != self.loc:
            if loc > len(self.ship)-1:
                self.loc = loc
                for i in range(loc):
                    if i > len(self.ship)-1:
                        self.ship.append(None)
                self.ship.append(self)
            else:
                ship[self.loc] = self.ship[loc]
                self.ship[loc] = self
                self.loc = loc
            if loc == 0:
                self.back = None
            else:
                self.back = ship[loc-1]
                self.back.front = self
            if len(ship) == loc+1:
                self.front = None
            else:
                self.front = ship[loc+1]
                self.front.back = self
            return True
        else:
            return False

    def addObject(self, object, location = ""):
        '''add object into the module and set its location'''
        self.objectList.append(object)
        if location != "":
            object.setLoc(str(location))

    def addObjects(self, *args):
        '''add multiple objects to the module'''
        for object in args:
            self.objectList.append(object)

class Object(Thing):
    '''a class for all objects'''

    def __init__(self, name, flavor, flavor2, location, hasInvent=False, hasResource = False):
        super().__init__(name, flavor, flavor2)
        self.hasInvent = hasInvent
        self.hasResource = hasResource
        self.loc = str(location)
        if hasInvent:
            self.inventory = []
        if hasResource:
            self.resourceNodes = {} #format> "name":ResourceNode

    def setLoc(self, location):
        self.loc = str(location)

    def getLoc(self):
        return self.loc

class Doors(Thing):
    '''a class for all doors'''

    def __init__(self, name, flavor, flavor2, locationIn, locationOut, roomIn, roomOut):
        super().__init__(name, flavor, flavor2)
        #The door connect two location so one room is deemed outside
        self.locIn = str(locationIn)
        self.locOut = str(locationOut)
        self.roomIn = roomIn
        self.roomOut = roomOut

    def setLocIn(self, location):
        '''sets the string discribe where the door located in the inside room'''
        self.locIn = str(locationIn)

    def getLocIn(self):
        '''sets the string discribe where the door located in the outside room'''
        return self.locIn

    def setLocOut(self, location):
        '''gets the string discribe where the door located in the inside room'''
        self.locOut = str(locationOut)

    def getLocOut(self):
        '''gets the string discribe where the door located in the outside room'''
        return self.locOut

    def getRoomIn(self):
        '''get the inside room'''
        return self.roomIn

    def getRoomOut(self):
        '''get the outside room'''
        return self.roomOut

class ResourceNode(Thing):
    '''a class for node to contain and tranfer resources'''

    def __init__(self, name, flavor, flavor2, type, capacity = 100, amount = 0, links = []):
        super().__init__(name, flavor)
        self.type = type
        self.capacity = capacity
        self.amount = amount
        self.links = links

    def link(self, other, type, maxFlow):
        '''
        links two ResourceNode together

        other : other ResourceNode to link with
        type  : the type of the linkage > "I"(input)
                                          "O"(output)
                                          "2"(two-way)
                                          "IP"(input pump)
                                          "OP"(output pump)
                                          "B"(Broken)
        '''
        if self.type == other.type:
            self.links.append([(other, type, maxFlow, False)])
        else:
            raise TypeError("Can not link ResourceNode with different type: {}({}) with {}({})".format(self.name, self.type, other.name, other.type))

    def removeResource(self, remove):
        '''remove a specified amount of resource from the node'''
        self.amount -= remove

    def addResource(self, add):
        '''add a specified amount of resource from the node'''
        self.amount += add

    def update(self):
        '''update the amount of resource in the node by calculate and update all links and linked nodes'''
        self.amount = max(0,min(self.amount, self.capacity))
        for link in self.links:
            if link[1] == "I":
                opp = "O"
                p1 = self.amount / self.capacity
                p2 = link[0].amount / link[0].capacity
                pDiff = p2-p1
                if pDiff <= 0:
                    pass
                else:
                    change =  min(self.capacity-self.amount, link[0].capacity-link[0].amount, link[2], link[2]*10*pDiff)
                    self.amount += change
                    link[0].amount -= change
                for link2 in link[0].links:
                    if link2[0].name == self.name and link2[1] == opp:
                        link2[3] = True
                        break
                link[3] = True
            elif link[1] == "O":
                opp = "I"
            elif link[1] == "2":
                opp = "2"
            elif link[1] == "IP":
                opp = "OP"
            elif link[1] == "OP":
                opp = "IP"
            else:
                opp = "B"

    def refresh(self):
        '''set updated tag to false'''
        for link in self.links:
            link[3] = False
            index = other.links.index[0]

class Slider():
    def __init__(self, min, max, interval, loop = False, startingPoint = None):
        if startingPoint == None:
            self.value = min
        else:
            self.value = startingPoint
        self.min = min
        self.max = max
        self.interval = interval
        self.loop = loop

    def increase(self, n = 1):
        '''increase the value by n interval'''
        checkValue = self.value + self.interval*n
        if checkValue > self.max:
            checkValue = self.min - self.interval + (checkValue-self.max)
        self.value = min(self.max, max(self.min, checkValue))

    def decrease(self, n =1):
        '''decrease the value by n interval'''
        checkValue = self.value - self.interval*n
        if checkValue < self.min:
            checkValue = self.max - self.interval + (self.min-checkValue)
        self.value = min(self.max, max(self.min, checkValue))

    def getValue(self):
        '''get the current value of the slider'''
        return self.value

    def setValue(self, value):
        '''set the current value of the slider'''
        self.value = value

class Timer():
    def __init__(self, stepper = False, stepInterval = None, start = False):
        self.timeDiff = 0
        if start == True:
            self.start = time.time()
            self.progressing = True
        else:
            self.progressing = False
        if stepper == True:
            self.stepper = True
            self.step = 0
            self.interval = stepInterval

    def start(self):
        '''start the timer (reset if it is counting)'''
        self.start = time.time()
        self.progressing = True

    def resume(self):
        '''continue the timer'''
        if not self.progressing:
            self.start = time.time()-(self.timeDiff)
            self.progressing = True

    def pause(self):
        '''pause the timer'''
        if self.progressing:
            self.stop = time.time()
            self.timeDiff = time.time() - self.start
            self.progressing = False

    def stepper(self, isOn):
        '''enable a stepper mode'''
        self.stepper = isOn

    def getTime(self):
        '''get the current time in seconds from starting the timer'''
        if self.progressing:
            return time.time() - self.start
        else:
            return self.timeDiff

    def getStep(self):
        '''return the current step'''
        if self.stepper:
            if self.progressing:
                return int((time.time() - self.start)//self.interval)
            else:
                return int(self.timeDiff//self.interval)
        else:
            return -1

    def getProgressing(self):
        '''return True if the timer is counting and False if not'''
        return self.progressing

class Person():
    def __init__(self, name, description, location, isControlling = False):
        self.name = name
        self.description = description
        self.recall = {}

        self.health = 100
        self.hunger = 100
        self.stress = 0

        self.inventory = []
        self.location = None
        self.isControlling = isControlling

    def control(self, flag):
        '''sets the control to the current character'''
        self.isControlling = flag

    def getControl(self):
        '''gets control state'''
        return self.isControlling

    def setRecall(self, dict):
        '''sets the dict for memory recall'''
        self.recall = list

    def getRecall(self):
        '''gets the recall dictionary'''
        return self.recall

    def addRecall(self, dict):
        '''adds an entry to the recall memory dictionary'''
        if type(dict) == type({}):
            self.recall += dict
        else:
            raise Exception("addRecall with not Dict")

    def setLoc(self, loc):
        '''sets current location'''
        self.location = loc

    def getLoc(self):
        '''gets current location'''
        return self.getLoc
