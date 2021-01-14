# Jittipat Shobbakbun
# 01/10/2021
# MainGame.py

# imports
from Classes import *
import time
import math
import pickle #smt=pickle.load(file) / pickle.dump(smt, file)
import curses
import os
import sys
from subprocess import call
import logging
import threading

# global variables
textDelayMultiplier = 1
debug = False
textSpeed = 1
screenWidth = 0
screenHeight = 0

#screen config
debugWidth = 30
debugHeight = 20
textUpOffset = -1 # set to -1 to use textUpOffsetRatio
textUpOffsetRatio = 0
upperlineRY = 3
lowerlineRY = 4
optionInputLength = 5
optionLength = 40

# settings
months = {
    "January":31,
    "Febuary":28,
    "March":31,
    "April":30,
    "May":31,
    "June":30,
    "July":31,
    "August":31,
    "September":30,
    "October":31,
    "November":30,
    "December":31
}

keyBinding = {
    "EmergencyEscape":"Q",
    "UP":"KEY_UP",
    "DOWN":"KEY_DOWN",
    "LEFT":"KEY_LEFT",
    "RIGHT":"KEY_RIGHT",
    "DEBUG":"KEY_F(1)",
    "PAUSE":"p",
    "TEXTUP":"KEY_SR",
    "TEXTDOWN":"KEY_SF",
    "DELETE":"KEY_BACKSPACE"
}

commandDict = {
    "PAUSE":["PAUSE", "STOP", "P"],
    "LOOK":["LOOK", "LOOK AT"],
    "GO":["MOVE", "GO", "GO TO", "GO THROUGH", "WALK TO", "RUN TO", "WALK", "RUN"],
    "ROOM":["ROOM", "AROUND", "THE ROOM"],
    "TTP":["TTP"],
    "DEBUG":["DEBUG"],
}

options = {
    "Back to Main Menu":None,
    "Text display speed":1,
    "test option with float":2.5,
    "test option with boolean":False,
    "A sligthlyyyyyyy too long optionnnnnnnnnn":2
}

gameState = {}

def setupDefaultGameState():
    '''sets up the default (in case of no save file) gameState'''
    #setup the station map

    #setup Map

    #setup default gameState

    # generating rooms
    map = {
        "room4012":MapNode(
            name = "Room 4012",
            flavor = "This is where you are staying. It is similar to normal hotel rooms found on earth.",
            flavor2 = "It shaped like an L. The walls are blue with white accents, and the room is basked in a warm orange tinted light.",
            firstImpression = "You woke up again. But this time, it is in your room on the Lance. A similar room that you recognize."
        ),
        "testSpace":MapNode(
            name = "White void",
            flavor = "The room is all white. You see nothing but white. There is no horizon line, no sky, no ground. There is nothing but white.",
            flavor2 = "There is no shadow, no shade, no perspective. You feel like standing on a normal ground, but you cannot distinguish where the ground start or where the sky end. You can still feel yourself, so that mean can see yourself. You just unable to distinguish it from anything else. It is all white.",
            firstImpression = "You woke up and all you see is white. You looked around and all you see is white. You can't even see yourself."
        ),
    }

    # Detailing rooms / add doors
    doors = {
        "testSpace-Room4012":Door(
            name = "Black portal",
            flavor = "It is a black hole.",
            flavor2 = "You look closer and see no shade or other sign that it reflect ligth. You also feel sligth suction, but it is resitable",
            roomIn = map["testSpace"],
            roomOut = map["room4012"],
            locationIn = "a BLACK PORTAL flaoting above you",
            locationOut = "no sign of the hole you just went through"
        )
    }

    # Generating objects $ populating rooms with objects
    objects = {
        #room4012
        "waterBottle":Object(
            name = "Water bottle",
            flavor = "It is an ordinary bottle from some 3D printer.",
            flavor2 = "",
            location = "a WATER BOTTLE flaoting in front of you",
            room = map["testSpace"],
            hasResource = True,
            getable = True
        ),
        "pencil0":Object(
            name = "Pencil",
            flavor = "It is very short pencil. You cannot help but wonder who used it to this length instead of recycling for a new one.",
            flavor2 = "",
            location = "a PENCIL on the 'floor'",
            room = map["testSpace"],
            hasResource = True,
            getable = True
        )
    }

    # generating characters
    characters = {
        "Alice":Person(
            name = "Alice Mirancoff",
            flavor = "She is an acomplished astronomer an the captain of the S.P.E.A.R.",
            location = None,
            isControlling = True
        ),
        "":Person(
            name = "",
            flavor = "",
            location = None
        ),
        "":Person(
            name = "",
            flavor = "",
            location = None
        ),
        "":Person(
            name = "",
            flavor = "",
            location = None
        ),
        "":Person(
            name = "",
            flavor = "",
            location = None
        ),
        "":Person(
            name = "",
            flavor = "",
            location = None
        )
    }

    # Creating story conditions
    story = {
        "intro":Story(
            name = "intro",
            key = "intro",
            requirements = [
                [], # first (index = 0) requirement is to get from state -1 to state 0
                [lambda tempState : tempState["lastCommand"][0] == "LOOK"], # second and other (index = 1 to len(requirement)-1) requirement is to get from state index-1 to state index
                [lambda tempState : tempState["lastCommand"][0] == "LOOKOBJ"],
                [lambda tempState : tempState["lastCommand"][0] == "GODOOR"],
                [] # last requirement is to complete the current story and link the next one
            ],
        ),
    }

    story["intro"].setLink(story["firstTraining"])

    # Combining a gameState
    defaultGameState = {
        "map":map,
        "currentMap":map["testSpace"],
        "objects":objects,
        "doors":doors,
        "characters":characters,
        "story":story,
        "activeStory":[],
        "time":1, # time in seconds after Jan 1, 2070 1m=60 1h=3600 1d=86400
        "top":0,
        "lastCommand":["UNKNOW",None],
        "textLog":[],
    }
    return defaultGameState

#Functions
def wrapper(func, *args, **kwds):
    """Wrapper function that initializes curses and calls another function,
    restoring normal keyboard/screen behavior on error.
    The callable object 'func' is then passed the main window 'stdscr'
    as its first argument, followed by any other arguments passed to
    wrapper().
    *** Original code from https://github.com/enthought/Python-2.7.3/blob/master/Lib/curses/wrapper.py ***
    *** Adapted by Win Shobbakbun ***
    """

    try:
        # Initialize curses
        stdscr = my_stdscr(curses.initscr(), 0, 0)

        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()
        curses.cbreak()

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.get_stdscr().keypad(1)

        # Start color, too.  Harmless if the terminal doesn't have
        # color; user can test with has_color() later on.  The try/catch
        # works around a minor bit of over-conscientiousness in the curses
        # module -- the error return from C start_color() is ignorable.
        try:
            curses.start_color()
        except:
            pass

        return func(stdscr, *args, **kwds)
    finally:
        # Set everything back to normal
        if 'stdscr' in locals():
            stdscr.get_stdscr().keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

def str_wrap(string, width):
    '''return a list of lines of text confined to width (not cutting words)'''
    chCount = 0
    retList = [None]
    list = string.split()
    lastLine = 0
    for i, word in enumerate(list):
        if i == 0:
            retList[0] = word
            chCount += len(word)
            continue
        else:
            chCount += 1 + len(word)
        if chCount%width == 0:
            lastLine = (chCount//width)-1
            retList[lastLine] += (" " + str(word))
        elif lastLine != chCount//width:
            lastLine = chCount//width
            chCount -= 1 + len(word)
            if chCount%width == 0:
                chCount += len(word)
            else:
                chCount += width-(chCount%width)
                chCount += len(word)
            retList.append(word)
        elif lastLine == chCount//width:
            retList[lastLine] += (" " + str(word))
    while True:
        if None in retList:
            retList.pop(retList.index(None))
        else:
            break
    return retList

def storyInterpreter(list):
    '''gets lines from list and format them'''
    seperatedTexts = []
    removedLines = 0
    for string in list:
        if " : " not in string and len(string) != 0:
            seperatedTexts.append(["DCPT", string])
        else:
            testList = string.split(" : ")
            if len(testList) == 2:
                seperatedTexts.append(testList)
            elif len(testList) == 1 and testList[0] != "":
                seperatedTexts.append(testList + [""])
            elif len(testList) == 1 and testList[0] == "":
                seperatedTexts.append(["NEWL", "-"])
    formattedTextList = []
    addLines = None
    for index, (type, massage) in enumerate(seperatedTexts):
        type = type.strip()
        formattedMassageList = []
        if type == "THOG":
            formattedMassageList = str_wrap("(" + massage + ")", screenWidth)
        elif type == "DCPT":
            formattedMassageList = str_wrap(massage, screenWidth)
        elif type == "FDBK":
            massageList = str_wrap(massage, screenWidth)
            formattedMassageList = [[line, curses.A_DIM] for line in massageList]
        elif type == "NEWL":
            if addLines == None:
                addLines = ["" for i in massage]
            else:
                addLines += ["" for i in massage]
            continue
        else:
            addLines = None
            pre = "{} : ".format(type)
            space = " " * len(pre)
            massageList = str_wrap('"' + massage + '"', screenWidth - len(pre))
            for i, line in enumerate(massageList):
                if i == 0:
                    formattedMassageList.append(pre + line)
                else:
                    formattedMassageList.append(space + line)
        if addLines != None and type != "NEWL":
            formattedTextList.append(addLines + formattedMassageList)
            addLines = None
        else:
            formattedTextList.append(formattedMassageList)
    #return formattedTextList
    # additional option
    reformattedTextList = []
    for thing in formattedTextList:
        reformattedTextList += thing
    return reformattedTextList

def str_hardWrap(string, width):
    '''return a list of lines of text confined to width (not cutting words)'''
    length = len(string)
    lineCount = math.ceil(length/width)
    retList = ["" for i in range(lineCount)]
    for i in range(lineCount):
        retList[i] = string[width*i:(width*(i+1))]
    return retList

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

def storyCheck(tempState, textToDisplay):
    '''use the story and the key with additional formatting'''
    for story in tempState["activeStory"]:
        tempState, textToDisplay = story.checkReqs(tempState, textToDisplay)
    return tempState, textToDisplay

#Commands
def multiwordCompare(testList, checkList):
    '''return true if first list of words is somewhere in the second list'''
    if type(testList) == str: testList = testList.split()
    if type(checkList) == str: checkList = checkList.split()
    lastMatchIndex = -1
    for checkWord in checkList:
        match = False
        for index, testWord in enumerate(testList):
            if testWord == checkWord:
                match = True
                matchIndex = index
                break
        if not match:
            return False
        else:
            if lastMatchIndex != -1:
                if matchIndex - lastMatchIndex != 1:
                    return False
        lastMatchIndex = matchIndex
    return True

def multiwordIsIn(testList, checkList, mustFirst = False, requestIndex = False):
    '''return true if first list of words is somewhere in the second list'''
    for checkPhrase in checkList:
        lastMatchIndex = -1
        if type(checkPhrase) == str: checkPhrase = checkPhrase.split()
        for checkWord in checkPhrase:
            match = False
            for index, testWord in enumerate(testList):
                if mustFirst and index > 0 and not match:
                    break
                if testWord == checkWord:
                    match = True
                    matchIndex = index
                    break
            if not match:
                break
            else:
                if lastMatchIndex != -1:
                    if matchIndex - lastMatchIndex != 1:
                        match = False
                        break
            lastMatchIndex = matchIndex
        if match == True:
            if requestIndex:
                return True, len(checkPhrase)
            else:
                return True
    if requestIndex:
        return False, -1
    else:
        return False

def commandHandeler(input, tempState, textToDisplay):
    words = input.upper().split()
    index = -1
    command = ""
    for key, commandList in commandDict.items():
        isMatch, index = multiwordIsIn(words, commandList, True, True)
        if isMatch:
            command = key
            break
        else:
            command = "UNKNOWN"
    objects = words[index:]
    retCommand = command
    retObject = None
    if command == "LOOK":
        if len(objects) == 0:
            retObject = tempState["currentMap"]
            tempState, textToDisplay = tempState["currentMap"].look(tempState, textToDisplay)
        elif multiwordIsIn(objects, commandDict["ROOM"]):
            retObject = tempState["currentMap"]
            tempState, textToDisplay = tempState["currentMap"].look(tempState, textToDisplay)
        else:
            for object in tempState["currentMap"].getObjects():
                if multiwordCompare(objects, object.getName().upper()):
                    retCommand = "LOOKOBJ"
                    retObject = object
                    tempState, textToDisplay = object.look(tempState, textToDisplay)
                    break
            else:
                textToDisplay.append("FDBK : Cannot find what you are looking for.")
    elif command == "GO":
        for door in tempState["currentMap"].getDoors():
            if multiwordCompare(objects, door.getName().upper()):
                retCommand = "GODOOR"
                retObject = door
                tempState, textToDisplay = door.go(tempState, textToDisplay)
                break
        else:
            textToDisplay.append("FDBK : Cannot find where you want to go to.")
    elif command == "TTP":
        textToDisplay.append(str(textToDisplay))
    elif command == "DEBUG" and debug:
        textToDisplay.append(str(tempState))
    else:
        textToDisplay.append("FDBK : Command not recognized")
    tempState["lastCommand"] = [retCommand, retObject]
    return tempState, textToDisplay

def commandCheck(input, commandList, objectList):
    '''check whether the input match the commandList and objectList'''
    words = input.upper().split()
    index = -1
    command = ""
    isCommandMatch, index = multiwordIsIn(words, commandList, True, True)
    objects = words[index:]
    isObjectMatch = multiwordIsIn(objects, objectList)
    return isComplete and isObjectMatch

def pause(stepper, paused, previousSteping):
    if paused:
        paused = False
        if previousSteping == True:
            stepper.resume()
    else:
        paused = True
        previousSteping = stepper.getProgressing()
        stepper.pause()
    return paused, previousSteping

#Loop Components
def characterProcessing(my_stdscr, pressList = [-1 for x in range(7)]):
    '''get the pressed key and seperate tapping and holding'''
    stdscr = my_stdscr.get_stdscr()
    holdCount = 0
    try:
        currentCh = stdscr.getkey()
    except:
        currentCh = -1
    pressList.pop(0)
    pressList.append(currentCh)
    for cha in pressList:
        if cha != -1:
            testList = pressList.copy()
            testList.pop(pressList.index(cha))
            if cha in testList:
                holdCh = cha
                holdCount += 1
            else:
                holdCh = pressList[-1]
                holdCount = 0
            break
    else:
        holdCh = -1
        holdCount = 0
    return holdCh, holdCount, pressList

def debugWindowUpdate(debugWindow, *args):
    '''show the debug overley with informations (arguments)'''
    debugWindow.erase()
    for index, arg in enumerate(args):
        if type(arg) == int:
            debugWindow.addstr(index, (debugWidth-len("{}".format(str(arg)))), "{}".format(str(arg)))
        elif type(arg) == float:
            debugWindow.addstr(index, (debugWidth-len("{:.5f}".format(arg))), "{:.5f}".format(arg))
        elif type(arg) == str:
            debugWindow.addstr(index, (debugWidth-len("{}".format(arg))), "{}".format(arg))
        else:
            debugWindow.addstr(index, (debugWidth-len("{}".format(str(arg)))), "{}".format(str(arg)))
    debugWindow.noutrefresh(0,0, 0,screenWidth-debugWidth,screenHeight,screenWidth)

#Loops
def menu(stdscr, debugWindow, hasSave, allStart):
    '''game loop for menu screen'''
    global debug
    global gameState

    #MenuSetup
    if hasSave:
        menuSelector = Slider(0, 4, 1, loop = True)
        loadAttr = curses.A_NORMAL
    else:
        menuSelector = Slider(0,2,1, loop = True)
        loadAttr = curses.A_DIM
    #Loop
    loopCount = 0
    start = 0
    stop = 0
    maxLoopLength = 0
    loopLengthList = [0 for x in range(100)]
    averageLoopLength = 0
    loopLength = 0
    actualLoopLength = 0
    pressList = [-1 for x in range(7)]

    step = 0
    lastStep = 0

    menuLoop = True
    while menuLoop:
        #Loop and time
        start = time.time()
        if debug:
            loopLengthList.pop(0)
            loopLengthList.append(loopLength)
            if loopLength > maxLoopLength:
                maxLoopLength = loopLength
            averageLoopLength = (averageLoopLength*100 + loopLength - loopLengthList[0])/100

        #Character processing
        holdCh, holdCount, pressList = characterProcessing(stdscr, pressList)

        #Character check
        if holdCh == keyBinding["EmergencyEscape"]:
            if "\x1b" in pressList:
                break
        if debug:
            if holdCh == keyBinding["DEBUG"]:
                debug = False
        else:
            if holdCh == keyBinding["DEBUG"]:
                debug = True
        if holdCh == keyBinding["DOWN"]:
            menuSelector.increase()
        if holdCh == keyBinding["UP"]:
            menuSelector.decrease()
        if holdCh == "\n":
            if hasSave:
                if menuSelector.getValue() == 0:
                    pass #NEED WORKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK
                elif menuSelector.getValue() == 1:
                    gameState = defaultGameState
                    return "MAIN"
                elif menuSelector.getValue() == 2:
                    return "LOAD"
                elif menuSelector.getValue() == 3:
                    return "OPTION"
                elif menuSelector.getValue() == 4:
                    introLoop = False
                    return "END"
            else:
                if menuSelector.getValue() == 0:
                    gameState = defaultGameState
                    return "MAIN"
                elif menuSelector.getValue() == 1:
                    return "OPTION"
                elif menuSelector.getValue() == 2:
                    return "END"

        #Logic
        if hasSave:
            if menuSelector.getValue() == 0:
                l0 = "> "
                r0 = " <"
                l1 = r1 = l2 = r2 = l3 = r3 = l4 = r4 = " "
            elif menuSelector.getValue() == 1:
                l1 = "> "
                r1 = " <"
                l0 = r0 = l2 = r2 = l3 = r3 = l4 = r4 = " "
            elif menuSelector.getValue() == 2:
                l2 = "> "
                r2 = " <"
                l0 = r0 = l1 = r1 = l3 = r3 = l4 = r4 = " "
            elif menuSelector.getValue() == 3:
                l3 = "> "
                r3 = " <"
                l0 = r0 = l1 = r1 = l2 = r2 = l4 = r4 = " "
            elif menuSelector.getValue() == 4:
                l4 = "> "
                r4 = " <"
                l0 = r0 = l1 = r1 = l2 = r2 = l3 = r3 = " "
        else:
            if menuSelector.getValue() == 0:
                l1 = "> "
                r1 = " <"
                l2 = r2 = l3 = r3 = l4 = r4 = " "
            elif menuSelector.getValue() == 1:
                l3 = "> "
                r3 = " <"
                l1 = r1 = l2 = r2 = l4 = r4 = " "
            elif menuSelector.getValue() == 2:
                l4 = "> "
                r4 = " <"
                l1 = r1 = l2 = r2 = l3 = r3 = " "

        #Display
        stdscr.erase()
        y,x = stdscr.relativeAddtext(0.7, 0.5, "{}NEW GAME{}".format(l1, r1))
        if hasSave: stdscr.addstr(y-1, x-math.ceil(len("{}CONTINUE{}".format(l0, r0))/2), "{}CONTINUE{}".format(l0, r0))
        stdscr.addstr(y+1, x-math.ceil(len("{}  LOAD  {}".format(l2, r2))/2), "{}  LOAD  {}".format(l2, r2), loadAttr)
        stdscr.addstr(y+2, x-math.ceil(len("{} OPTION {}".format(l3, r3))/2), "{} OPTION {}".format(l3, r3))
        stdscr.addstr(y+3, x-math.ceil(len("{}  QUIT  {}".format(l4, r4))/2), "{}  QUIT  {}".format(l4, r4))
        stdscr.noutrefresh()

        if debug:
            debugWindowUpdate(
                debugWindow,
                "MENU",
                [holdCh],
                loopCount/100,
                stop - allStart,
                loopLength,
                actualLoopLength,
                1/max(actualLoopLength,0.000001),
                averageLoopLength,
            )

        curses.doupdate()

        #Loop and time
        loopCount += 1
        stop = time.time()
        loopLength = stop-start
        time.sleep(0.01)
        actualStop = time.time()
        actualLoopLength = actualStop-start

def load(stdscr, debugWindow, allStart):
    pass

def option(stdscr, debugWindow, allStart):
    '''gameLoop for option screen'''
    global debug
    global options

    #OptionSetup
    blinker = Timer(True, 0.6, True)
    optionSelector = Slider(0, len(options)-1, 1, startingPoint = 1)
    isEditing = False
    commandType = None
    editedBool = None
    upOptionList = []
    currentOptionText = ""
    downOptionList = []
    middleScreen = math.floor(screenHeight/2)
    upperBound = upperlineRY + 3
    upperSpace = middleScreen - upperBound - 1
    lowerBound = screenHeight - lowerlineRY - 2
    lowerSpace = lowerBound - middleScreen - 1
    warningText = ""

    #Loop
    loopCount = 0
    start = 0
    stop = 0
    maxLoopLength = 0
    loopLengthList = [0 for x in range(100)]
    averageLoopLength = 0
    loopLength = 0
    actualLoopLength = 0
    aall = 0.01 #averageActualLoopLength
    tall = 0
    pressList = [-1 for x in range(7)]
    textBuffer = ""

    introLoop = True
    while introLoop:
        #Loop and time
        start = time.time()
        if debug:
            loopLengthList.pop(0)
            loopLengthList.append(loopLength)
            if loopLength > maxLoopLength:
                maxLoopLength = loopLength
            averageLoopLength = (averageLoopLength*100 + loopLength - loopLengthList[0])/100

        #Character processing
        holdCh, holdCount, pressList = characterProcessing(stdscr, pressList)

        #Character check
        if holdCh == keyBinding["EmergencyEscape"]:
            if "\x1b" in pressList:
                break
        if debug:
            if holdCh == keyBinding["DEBUG"]:
                debug = False
        else:
            if holdCh == keyBinding["DEBUG"]:
                debug = True

        #command input
        if holdCh == "\n":
            if optionSelector.getValue() == 0:
                return "MENU"
            if isEditing:
                if textBuffer != "":
                    warningText = ""
                    key = list(options.keys())[optionSelector.getValue()]
                    if optionType == bool:
                        options[key] = editedBool
                    else:
                        try:
                            options[key] = optionType(textBuffer)
                        except:
                            warningText = "Please input {}".format(optionType.__name__)
                    if warningText == "":
                        textBuffer = ""
                        isEditing = False
                else:
                    warningText = ""
                    isEditing = False
            else:
                isEditing = True
                key = list(options.keys())[optionSelector.getValue()]
                optionType = type(options[key])
                if optionType == int or optionType == str or optionType == float:
                    #textBuffer = str(options[key])
                    textBuffer = ""
                elif optionType == bool:
                    editedBool = options[key]
        elif holdCh == keyBinding["DELETE"] and isEditing:
            textBuffer = textBuffer[:len(textBuffer)-1]
        elif len(str(holdCh)) == 1 and isEditing and len(textBuffer) < optionInputLength and optionType != bool:
            textBuffer += holdCh
        #AdditionalShortcutKeys
        if isEditing and optionType == bool:
            if holdCh == keyBinding["LEFT"] or holdCh == keyBinding["RIGHT"]:
                editedBool = not editedBool
        if not isEditing:
            if holdCh == keyBinding["DOWN"]:
                optionSelector.increase()
            if holdCh == keyBinding["UP"]:
                optionSelector.decrease()

        #Logic
        # Text processing
        name = str(list(options.keys())[optionSelector.getValue()])
        value = str(options[name])
        if name == "Back to Main Menu":
            currentOptionText = "[          Back to Main Menu           ]"
        else:
            currentOptionText = "[ " + name + " " + " "*(optionLength-len(name)-len(value)-7) + "[" + value + "]" + " ]"
        if optionSelector.getValue() != 0:
            upOptionList = []
            for index, (name, value) in enumerate(options.items()):
                name = str(name)
                value = str(value)
                if index < optionSelector.getValue():
                    if name == "Back to Main Menu":
                        upOptionList.append("[          Back to Main Menu           ]")
                    else:
                        upOptionList.append("[ " + name + " " + " "*(optionLength-len(name)-len(value)-7) + "[" + value + "]" + " ]")
        else:
            upOptionList = []
        if optionSelector.getValue() != len(options)-1:
            downOptionList = []
            for index, (name, value) in enumerate(options.items()):
                name = str(name)
                value = str(value)
                if index > optionSelector.getValue():
                    downOptionList.append("[ " + name + " " + " "*(optionLength-len(name)-len(value)-7) + "[" + value + "]" + " ]")
        else:
            downOptionList = []
        if isEditing:
            name = str(list(options.keys())[optionSelector.getValue()])
            if optionType == bool:
                currentOptionText = "[ " + name + " " + " "*(optionLength-len(name)-len(str(editedBool))-9) + "◄[" + str(editedBool) + "]►" + " ]"
            else:
                if blinker.getStep()%2 == 0:
                    textWithCursor = textBuffer + "_"
                else:
                    textWithCursor = textBuffer + " "
                inputSlot = str(textWithCursor)[:5] + " "*max(0, 5 - len(textWithCursor))
                currentOptionText = "[ " + name + " " + " "*(optionLength-len(name)-len(inputSlot)-7) + "[" + inputSlot + "]" + " ]"

        #Display
        stdscr.erase()
        #screen format
        dates = toDate(gameState["time"]).values()
        stdscr.addstr(1, math.floor(screenWidth*0.5)-3, "OPTIONS")
        stdscr.hline(upperlineRY,0,"─",screenWidth)
        stdscr.hline(screenHeight-lowerlineRY,0,"─",screenWidth)
        #text display
        leftOffset = math.floor((screenWidth-optionLength)/2)
        if upperSpace > 0 and len(upOptionList) > 0:
            for i in range(min(upperSpace, len(upOptionList))):
                stdscr.addstr(i + max(upperBound, middleScreen-1-len(upOptionList)), leftOffset, upOptionList[i])

        if isEditing:
            stdscr.addstr(middleScreen, leftOffset - 2,"> " + currentOptionText + " <")
            if warningText != "":
                stdscr.addstr(middleScreen + 1, math.floor((screenWidth-len(warningText))/2), warningText, curses.A_DIM)
        else:
            if optionSelector.getValue() != 0:
                stdscr.addstr(middleScreen - 1, math.floor(screenWidth/2), "▲")
            stdscr.addstr(middleScreen, leftOffset, currentOptionText)
            if optionSelector.getValue() != len(options)-1:
                stdscr.addstr(middleScreen + 1, math.floor(screenWidth/2), "▼")

        if lowerSpace > 0  and len(downOptionList) > 0:
            for i in range(min(lowerSpace, len(downOptionList))):
                stdscr.addstr(i + middleScreen + 2, leftOffset, downOptionList[i])

        stdscr.noutrefresh()

        if debug:
            debugWindowUpdate(
                debugWindow,
                "OPTION",
                [holdCh],
                #loopCount/100,
                stop - allStart,
                #loopLength,
                #actualLoopLength,
                1/max(actualLoopLength,0.000001),
                averageLoopLength,
                optionSelector.getValue(),
                lowerBound,
            )

        curses.doupdate()

        #Loop and time
        loopCount += 1
        stop = time.time()
        loopLength = stop-start
        time.sleep(0.01)
        actualStop = time.time()
        actualLoopLength = actualStop-start
        tall += actualLoopLength
        aall = tall/loopCount

def save(stdscr, debugWindow, allStart):
    pass

def pOption(stdscr, debugWindow, allStart):
    pass

def mainLoop(stdscr, debugWindow, allStart, gameState):
    '''main gameLoop'''
    global debug
    tempState = dict(gameState)

    #IntroSetup
    pauseSelector = Slider(0, 4, 1, loop = True)
    blinker = Timer(True, 0.6, True)

    textToDisplay = []
    commandsBuffer = []

    #Story Loop
    tempState["currentMap"] = tempState["map"]["testSpace"]
    tempState["story"]["intro"].setActive(tempState)

    #Loop
    loopCount = 0
    start = 0
    stop = 0
    maxLoopLength = 0
    loopLengthList = [0 for x in range(100)]
    averageLoopLength = 0
    loopLength = 0
    actualLoopLength = 0
    aall = 0.01 #averageActualLoopLength
    tall = 0
    pressList = [-1 for x in range(7)]

    #introLoop
    textDelay = (100 - options["Text display speed"])*textDelayMultiplier*0.01
    paused = False
    waited = False

    textLog = tempState["textLog"]
    lineCount = 0
    autoUp = False

    step = 0
    lastStep = 0
    stepper = Timer(True, textDelay, True)
    previousSteping = True

    textBuffer = ""

    isLoop = True
    while isLoop:
        #Loop and time
        start = time.time()
        if debug:
            loopLengthList.pop(0)
            loopLengthList.append(loopLength)
            if loopLength > maxLoopLength:
                maxLoopLength = loopLength
            averageLoopLength = (averageLoopLength*100 + loopLength - loopLengthList[0])/100

        #Character processing
        holdCh, holdCount, pressList = characterProcessing(stdscr, pressList)

        #Character check
        if holdCh == keyBinding["EmergencyEscape"]:
            if "\x1b" in pressList:
                break
        if debug:
            if holdCh == keyBinding["DEBUG"]:
                debug = False
        else:
            if holdCh == keyBinding["DEBUG"]:
                debug = True

        if paused:
            if waited: #exit confirm loop
                if holdCh == keyBinding["LEFT"]:
                    waitSelector.decrease()
                if holdCh == keyBinding["RIGHT"]:
                    waitSelector.increase()
                if holdCh == "\n":
                    if waitSelector.getValue() == 0:
                        return "pSAVE"
                    elif waitSelector.getValue() == 1:
                        return "MENU"
            else: #pause loop
                if holdCh == keyBinding["UP"]:
                    pauseSelector.decrease()
                if holdCh == keyBinding["DOWN"]:
                    pauseSelector.increase()
                if holdCh == "\n":
                    if pauseSelector.getValue() == 0:
                        paused = False
                        if previousSteping == True:
                            stepper.resume()
                    elif pauseSelector.getValue() == 1:
                        return "pSAVE"
                    elif pauseSelector.getValue() == 2:
                        return "pLOAD"
                    elif pauseSelector.getValue() == 3:
                        return "pOPTION"
                    elif pauseSelector.getValue() == 4:
                        waitSelector = Slider(0,1,1)
                        if saved: #<----------------------------------Compare current state to last saved state?
                            gameState = dict(tempState)
                            return "MAIN"
                        else:
                            waited = True
        else: #normal loop
            #command input
            if holdCh == "\n":
                if len(textBuffer) != 0:
                    inputUpper = textBuffer.upper()
                    textLog += [["> " + str(textBuffer), curses.A_DIM]]#callback on the terminal
                    if inputUpper in commandDict["PAUSE"]:
                        paused, previousSteping = pause(stepper, paused, previousSteping)
                        textLog += [["Paused", curses.A_DIM]]
                    else:
                        commandsBuffer.append(inputUpper)
                        commandHandeler(inputUpper, tempState, textToDisplay)
                        saved = False
                    autoUp = True
                    textBuffer = ""
            elif holdCh == keyBinding["DELETE"]:
                textBuffer = textBuffer[:len(textBuffer)-1]
            #add character to the buffer
            elif len(str(holdCh)) == 1:
                textBuffer += holdCh
            #AdditionalShortcutKeys
            if holdCh == keyBinding["TEXTUP"]:
                if tempState["top"] > 0:
                    tempState["top"] -= 1
                    autoUp = False
            if holdCh == keyBinding["TEXTDOWN"]:
                if tempState["top"] < len(textLog)-1:
                    tempState["top"] += 1
                    autoUp = False

        #Logic
        if paused:
            if waited:
                if waitSelector.getValue() == 0:
                    conY = ">"
                    conN = " "
                elif waitSelector.getValue() == 1:
                    conY = " "
                    conN = ">"
            else:
                if pauseSelector.getValue() == 0:
                    l0 = "> "
                    r0 = " <"
                    l1 = r1 = l2 = r2 = l3 = r3 = l4 = r4 = " "
                elif pauseSelector.getValue() == 1:
                    l1 = "> "
                    r1 = " <"
                    l0 = r0 = l2 = r2 = l3 = r3 = l4 = r4 = " "
                elif pauseSelector.getValue() == 2:
                    l2 = "> "
                    r2 = " <"
                    l0 = r0 = l1 = r1 = l3 = r3 = l4 = r4 = " "
                elif pauseSelector.getValue() == 3:
                    l3 = "> "
                    r3 = " <"
                    l0 = r0 = l1 = r1 = l2 = r2 = l4 = r4 = " "
                elif pauseSelector.getValue() == 4:
                    l4 = "> "
                    r4 = " <"
                    l0 = r0 = l1 = r1 = l2 = r2 = l3 = r3 = " "
        else:
            # Text processing
            if len(textToDisplay) > 0:
                textLog += storyInterpreter(textToDisplay)
                textToDisplay = []
                autoUp = True
            '''
            step = stepper.getStep()
            stepperTime = stepper.getTime()
            if step != max(0, len(textToDisplay)-1) and not stepper.getProgressing():
                stepper.resume()
            if step == max(0, len(textToDisplay)-1) and stepper.getProgressing():
                stepper.pause()

            if step != lastStep:
                saved = False
                textToDisplay2 = storyInterpreter(textToDisplay)
                for line in textToDisplay2[step]:
                    textLog.append(line)
                autoUp = True
            lastStep = stepper.getStep()
            '''

            if autoUp:
                tempState["top"] = max(tempState["top"],len(textLog)-screenHeight+lowerlineRY+5+textUpOffset)
                autoUp = False

        # Check active stories' requirement
        tempState, textToDisplay = storyCheck(tempState, textToDisplay)

        #Display
        stdscr.erase()
        if paused:
            if waited: #exit confirm display loop
                y,x = stdscr.relativeAddtext(0.5, 0.5, "Do you want to save the game before quiting?")
                stdscr.addstr(y+2,x-5, "{}YES".format(conY))
                stdscr.addstr(y+2,x+2, "{}NO".format(conN))
            else: #pause display loop
                y,x = stdscr.relativeAddtext(0.3, 0.5, "PAUSED")
                stdscr.addstr(y+int(screenWidth/10), x-math.ceil(len("{}CONTINUE{}".format(l0, r0))/2), "{}CONTINUE{}".format(l0, r0))
                stdscr.addstr(y+int(screenWidth/10)+1, x-math.ceil(len("{}  SAVE  {}".format(l1, r1))/2), "{}  SAVE  {}".format(l1, r1))
                stdscr.addstr(y+int(screenWidth/10)+2, x-math.ceil(len("{}  LOAD  {}".format(l2, r2))/2), "{}  LOAD  {}".format(l2, r2))
                stdscr.addstr(y+int(screenWidth/10)+3, x-math.ceil(len("{} OPTION {}".format(l3, r3))/2), "{} OPTION {}".format(l3, r3))
                stdscr.addstr(y+int(screenWidth/10)+4, x-math.ceil(len("{}  QUIT  {}".format(l4, r4))/2), "{}  QUIT  {}".format(l4, r4))
        else: #normal display loop
            #screen format
            dates = toDate(tempState["time"]).values()
            stdscr.addstr(0,0,"{1} {2}, {0} {3}:{4}:{5}".format(*dates))
            stdscr.addstr(1,0,"Location: {}".format(tempState["currentMap"].getName()))
            stdscr.hline(upperlineRY,0,"─",screenWidth)
            stdscr.hline(screenHeight-lowerlineRY,0,"─",screenWidth)
            #terminal
            if blinker.getStep()%2 == 0:
                textWithCursor = textBuffer + "_"
            else:
                textWithCursor = textBuffer + " "
            terminalText = str_hardWrap(textWithCursor, screenWidth-2)
            if len(terminalText) == 0:
                stdscr.addstr(screenHeight-lowerlineRY+1, 0, "> ")
            elif len(terminalText) == 1:
                stdscr.addstr(screenHeight-lowerlineRY+1, 0, "> {}".format(terminalText[0]))
            else:
                stdscr.addstr(screenHeight-lowerlineRY+1, 0, "> {}".format(terminalText[0]))
                for i in range(1,len(terminalText)):
                    stdscr.addstr(screenHeight-lowerlineRY+1+i, 0, "  {}".format(terminalText[i]))
            #text display
            for i in range(tempState["top"],min(tempState["top"]+screenHeight-lowerlineRY-upperlineRY-1,len(textLog))):
                if type(textLog[i]) == list:
                    stdscr.addstr(upperlineRY+1+i-tempState["top"], 0, textLog[i][0], textLog[i][1])
                elif type(textLog[i]) == str:
                    stdscr.addstr(upperlineRY+1+i-tempState["top"], 0, textLog[i])

        stdscr.noutrefresh()

        if debug:
            if paused:
                debugWindowUpdate(
                    debugWindow,
                    "PAUSE",
                    [holdCh],
                    loopCount/100,
                    stop - allStart,
                    loopLength,
                    actualLoopLength,
                    1/max(actualLoopLength,0.000001),
                    averageLoopLength,
                    str(step) + " / " + "{:.5}".format(stepperTime),
                )
            else:
                debugWindowUpdate(
                    debugWindow,
                    "MAIN",
                    [holdCh],
                    stop - allStart,
                    1/max(actualLoopLength,0.000001),
                    #actualLoopLength,
                    aall,
                    #str(step) + " / " + "{:.5}".format(stepperTime),
                    tempState["top"],
                    str(tempState["activeStory"]),
                )

        curses.doupdate()

        #Loop and time
        loopCount += 1
        stop = time.time()
        loopLength = stop-start
        time.sleep(0.01)
        actualStop = time.time()
        actualLoopLength = actualStop-start
        tall += actualLoopLength
        aall = tall/loopCount

#Code
def main(stdscr):
    '''the main code inside the wrapper for curses module'''
    global debug
    global screenWidth
    global screenHeight
    global gameState

    curses.curs_set(False)
    stdscr.nodelay(True)
    debugWindow = curses.newpad(debugHeight, debugWidth)

    try:
        storyFile = open("resource/story.txt", "r").read()
    except:
        storyFile = open("story.txt","r").read()
    global story
    story = storyFile.split("\n")
    screenWidth = curses.COLS
    screenHeight = curses.LINES
    stdscr.setScreenWidth(curses.COLS)
    stdscr.setScreenHeight(curses.LINES)

    global textUpOffset
    if textUpOffset == -1:
        textUpOffset += int((screenHeight-10)*textUpOffsetRatio)
    allStart = time.time()

    for stor in defaultGameState["story"].values():
        stor.setText(story)

    gameLoop = True
    saves = {}
    try:
        savefileNames = os.listdir("saves")
        if len(savefileNames) == 0:
            hasSave = False
            gameState = setupDefaultGameState()
        else:
            hasSave = True
            for fileName in savefileNames:
                with open("saves/" + str(name), "rb") as file:
                    save = pickle.load(file)
                saves[name[:-2]] = save
    except:
        hasSave = False
        gameState = setupDefaultGameState()

    #TEMPORARY VARIABLES <------------------------ (REMOVE BEFORE USE)
    debug = True

    currentLoop = "MENU" #Creat NOTE loop to communicate with classmates (setting MAC key binding, etc.)
    while gameLoop:
        if currentLoop == "MENU":
            currentLoop = menu(stdscr, debugWindow, hasSave, allStart)
        elif currentLoop == "OPTION":
            currentLoop = option(stdscr, debugWindow, allStart)
        elif currentLoop == "MAIN":
            currentLoop = mainLoop(stdscr, debugWindow, allStart, gameState)
        elif currentLoop == "END":
            break
        else:
            raise Exception("Unknow loop called: {}".format(currentLoop))

if __name__ == "__main__":
    call("clear", shell=True)
    open('logging.log', 'w').close()
    logging.basicConfig(format='%(levelname)s:%(message)s', filename='logging.log', level=logging.DEBUG)
    wrapper(main)
    '''
    try:
        wrapper(main)
    except curses.error:
        errorList = sys.exc_info()
        if str(errorList[1]) == "addwstr() returned ERR":
            print("The screen is too small. Please expand or zoom out the screen.")
        else:
            raise Exception(str(errorList))
    '''
