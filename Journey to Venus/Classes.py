# Jittipat Shobbakbun
# 01/11/2021
# Classes.py

import time
import curses
import math
import logging

def getStoryText(list, key):
    '''gets lines from "story.txt" with coresponding key'''
    start = list.index("[" + key + "-")
    end = list.index("-" + key + "]")
    texts = [list[i] for i in range(start+1,end)]
    return texts

def toDate(sec):
    '''take time in seconds after Jan 1, 2070 and return date in format {Y:, Mo:, D:, H:, Mi:, S:}'''
    y = sec//(365*60*60*24)+2070
    totalDays = 0
    mo = None
    for month, days in months.items():
        totalDays += days
        if (sec%(365*60*60*24))//(60*60*24) < totalDays:
            mo = month
            break
    d = (sec%(365*60*60*24))//(60*60*24)-(totalDays-months[mo])+1
    h = (sec%(60*60*24))//(60*60)
    mi = (sec%(60*60))//(60)
    s = sec%(60)//1
    return {"Y":int(y), "Mo":mo, "D":int(d), "H":int(h), "Mi":int(mi), "S":int(s)}

def modifyTime(sec, Y=0, Mo=0, D=0, H=0, Mi=0, S=0):
    '''add or subtract time in seconds in year, month, etc.'''
    totalDays = 0
    dayInTheMonth = 0
    for month, days in months.items():
        totalDays += days
        if (sec%(365*60*60*24))//(60*60*24) < totalDays:
            dayInTheMonth = days
            break
    sec += ((Y*(365*60*60*24)) + (Mo*dayInTheMonth*24*60*60) + (D*24*60*60) + (H*60*60) + (Mi*60) + S)
    return sec

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
        self.doorInList = []
        self.doorOutList = []
        self.firstImpression = firstImpression
        self.explored = False

    def addObject(self, *args):
        '''add multiple objects to the node'''
        for object in args:
            self.objectList.append(object)

    def getObjects(self):
        return self.objectList

    def addDoorIn(self, door):
        self.doorInList.append(door)

    def addDoorOut(self, door):
        self.doorOutList.append(door)

    def getDoors(self):
        return self.doorOutList + self.doorInList

    def setFirstImpression(self, firstImpression):
        '''sets the node's first impression (OPTIONAL FEATURE)'''
        self.firstImpression = firstImpression

    def getFirstImpression(self):
        '''gets the node's first impression (OPTIONAL FEATURE)'''
        return self.firstImpression

    # commands
    def look(self, tempState, textToDisplay):
        '''return the respond for the command look'''
        if self.explored == False:
            self.explored = True
            textToDisplay.append(self.firstImpression)
        else:
            textToDisplay.append(self.flavor)
        tempState["time"] += 2

        if len(self.objectList) == 0:
            textToDisplay.append("There is no object here.")
        elif len(self.objectList) == 1:
            textToDisplay.append("There is {}.".format(objectList[0].getLoc()))
        elif len(self.objectList) == 2:
            textToDisplay.append("There are {} and {}.".format(self.objectList[0].getLoc(), self.objectList[1].getLoc()))
        else:
            response = "There are "
            for object in self.objectList[:-1]:
                response += object.getLoc() + ", "
            response += "and " + self.objectList[-1].getLoc() + "."
            textToDisplay.append(response)

        '''WIP
        doorList = [[x,"IN"] for x in self.doorInList] + [[x,"OUT"] for x in self.doorOutList]
        if len(self.doorList) == 0:
            textToDisplay.append("There is no door in this room.")
        elif len(self.doorList) == 1:
            textToDisplay.append("There is {}.".format(self.doorList[0].getLoc()))
        elif len(self.doorList) == 2:
            textToDisplay.append("There are {} and {}.".format(self.doorList[0].getLoc(), self.doorList[1].getLoc()))
        else:
            response = "There are "
            for object in self.doorList[:-1]:
                response += object.getLoc() + ", "
            response += "and " + self.doorList[-1].getLoc() + "."
        '''
        return tempState, textToDisplay

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

    def __init__(self, name, flavor, flavor2, location, room, hasInvent=False, hasResource = False, getable = False):
        super().__init__(name, flavor, flavor2)
        self.hasInvent = hasInvent
        self.hasResource = hasResource
        self.loc = str(location)
        self.room = room
        room.addObject(self)
        if hasInvent:
            self.inventory = []
        if hasResource:
            self.resourceNodes = {} #format> "name":ResourceNode

    def setLoc(self, location):
        self.loc = str(location)

    def getLoc(self):
        return self.loc

    def getRoom(self):
        return self.room

    def look(self, tempState, textToDisplay):
        textToDisplay.append(self.flavor)
        return tempState, textToDisplay

class Door(Thing):
    '''a class for all doors'''

    def __init__(self, name, flavor, flavor2, roomIn, roomOut, locationIn, locationOut):
        super().__init__(name, flavor, flavor2)
        #The door connect two location so one room is deemed outside
        self.locIn = str(locationIn)
        self.locOut = str(locationOut)
        self.roomIn = roomIn
        roomIn.addDoorOut(self)
        self.roomOut = roomOut
        roomOut.addDoorIn(self)

    def setLocIn(self, location):
        '''sets the string discribe where the door located in the inside room'''
        self.locIn = str(locationIn)

    def getLocIn(self):
        '''gets the string discribe where the door located in the outside room'''
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

    def look(self, tempState, textToDisplay):
        textToDisplay.append(self.flavor)
        return tempState, textToDisplay

    def go(self, tempState, textToDisplay):
        if tempState["currentMap"] == self.roomIn:
            tempState["currentMap"] = self.roomOut
            tempState, textToDisplay = self.roomOut.look(tempState, textToDisplay)
        elif tempState["currentMap"] == self.roomOut:
            tempState["currentMap"] = self.roomIn
            tempState, textToDisplay = self.roomIn.look(tempState, textToDisplay)
        return tempState, textToDisplay

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
        if checkValue > self.max and self.loop:
            checkValue = self.min - self.interval + (checkValue-self.max)
        self.value = min(self.max, max(self.min, checkValue))

    def decrease(self, n =1):
        '''decrease the value by n interval'''
        checkValue = self.value - self.interval*n
        if checkValue < self.min and self.loop:
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
    def __init__(self, name, flavor, location, isControlling = False):
        self.name = name
        self.flavor = flavor
        self.recall = {}

        self.health = 100
        self.hunger = 100
        self.stress = 0

        self.inventory = []
        self.location = None
        self.isControlling = isControlling

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

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

class Story():
    '''class for progressing the main story and arranging events'''
    def __init__(self, name, key, requirements = [], link = None, text = [], isComplete = False):
        self.name = name
        self.key = key
        self.text = text
        self.requirements = requirements
        self.link = link
        self.currentState = -1

    def __repr__(self):
        return self.name

    def setActive(self, tempState):
        '''sets the story as active in the tempState'''
        if self not in tempState['activeStory']:
            tempState['activeStory'].append(self)
            self.isComplete = False
            return True # return True if it was unset and set successfully
        else:
            return False # return False if it was already active

    def setLink(self, link):
        '''sets the linked story node'''
        self.link = link

    def setText(self, story):
        '''sets text using normal string or a list from story.txt'''
        if type(story) == list:
            lines = getStoryText(story, self.key)
        else:
            lines = string.split("\n")
        self.text = [[]]
        currentSection = 0
        for line in lines:
            if "SEPT" in line:
                currentSection = int(line[7:].strip())
            else:
                if len(self.text) > currentSection:
                    self.text[currentSection].append(line)
                else:
                    for i in range(len(self.text)-1, currentSection):
                        self.text.append([])
                    self.text[currentSection].append(line)

    def getText(self):
        '''gets the text of the story'''
        return self.text

    def complete(self, tempState):
        '''complete the story and link the next one'''
        tempState["activeStory"].pop(tempState["activeStory"].index(self))
        if self.link == None:
            pass
        elif type(self.link) == list:
            tempState["activeStory"] += self.link
        else:
            tempState["activeStory"].append(self.link)

    def checkReqs(self, tempState, textToDisplay):
        '''check whether tempState match the requirements to progress story state'''
        if self.currentState != len(self.text)-1:
            match = True
            if len(self.requirements[self.currentState+1]) == 0:
                pass
            else:
                for func in self.requirements[self.currentState+1]:
                    if not func(tempState): match = False
            if match:
                self.currentState += 1
                textToDisplay += self.text[self.currentState]
        elif self.currentState == len(self.text)-1:
            match = True
            if len(self.requirements[self.currentState+1]) == 0:
                pass
            else:
                for func in self.requirements[self.currentState+1]:
                    if not func(tempState): match = False
            if match:
                self.complete(tempState)
        return tempState, textToDisplay
