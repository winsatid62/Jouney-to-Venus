# Jittipat Shobbakbun
# 01/08/2021
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

# global variables
textDelayMultiplier = 1
debug = False
debugWidth = 30
debugHeight = 20
textSpeed = 1
screenWidth = 0
screenHeight = 0
textUpOffset = -1 # set to -1 to use textUpOffsetRatio
textUpOffsetRatio = 0

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
    "LOOK":["LOOK"],
    "MOVE":["MOVE", "GO"]
}

options = {"Text display speed":1}

#screen config
upperlineRY = 4
lowerlineRY = 4

#setup the station map

#setup Map


#setup default gameState
gameState = {
    "map":{
        "room4012":MapNode(
            name = "Room 4012",
            flavor = "This is where you are staying. It is similar to normal hotel rooms found on earth.",
            flavor2 = "It shaped like an L. The walls are blue with white accents, and the room is basked in a warm orange tinted light."
        ),
        "testSpace":MapNode(
            name = "White void",
            flavor = "It is all white. You see nothing but white. There is no horizon line, no sky, no ground. There is nothing but white. ",
            flavor2 = "There is no shadow, no shade, no perspective. You feel like standing on a normal ground, but you cannot distinguish where the ground start or where the sky end. You can still feel yourself, so that mean can see yourself. You just unable to distinguish it from anything else. It is all white.",
            firstImpression = "You woke up and all you see is white. You looked around and all you see is white. You can't even see yourself."
        ),
    },
    "story":2,
    "characters":{
        "Alice":Person(
            "Alice Mirancoff",
            "She is an acomplished astronomer an the captain of the S.P.E.A.R.",
             None,
             True
        ),
        "":None,
        "":None,
        "":None,
        "":None,
        "":None,
    },
    "currentCharacterIndex":4,
    "textLog":[],
    "timer":0, # time in seconds after Jan 1, 2070
    "":None,
}

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

def storyInterpreter(list, key):
    '''gets lines from "story.txt" with coresponding key and format them'''
    start = list.index("[" + key + "-")
    end = list.index("-" + key + "]")
    texts = [list[i] for i in range(start+1,end)]
    seperatedTexts = []
    removedLines = 0
    for string in texts:
        testList = string.split(" : ")
        if len(testList) == 2:
            seperatedTexts.append(testList)
        elif len(testList) == 1 and testList[0] != "":
            seperatedTexts.append(testList + [""])
        elif len(testList) == 1 and testList[0] == "":
            seperatedTexts.append(["NEWL", "-"])
    logging.debug(str(seperatedTexts))
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
            addLines = ["" for i in range(len(massage))]
            continue
        else:
            pre = "{} : ".format(type)
            space = " " * len(pre)
            massageList = str_wrap('"' + massage + '"', screenWidth - len(pre))
            for i, line in enumerate(massageList):
                if i == 0:
                    formattedMassageList.append(pre + line)
                else:
                    formattedMassageList.append(space + line)
        if addLines != None:
            formattedTextList.append(addLines + formattedMassageList)
            addLines = None
        else:
            formattedTextList.append(formattedMassageList)
    return formattedTextList

def str_hardWrap(string, width):
    '''return a list of lines of text confined to width (not cutting words)'''
    length = len(string)
    lineCount = math.ceil(length/width)
    retList = ["" for i in range(lineCount)]
    for i in range(lineCount):
        retList[i] = string[width*i:(width*(i+1))]
    return retList

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

#Commands
def commandHandeler(input):
    words = input.split()
    if words[0] in commandDict["PAUSE"]:
        pass

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

#Loops
def menu(stdscr, debugWindow, hasSave, allStart):
    '''game loop for menu screen'''
    global debug
    #MenuSetup
    if hasSave:
        menuSelector = Slider(0,4,1)
        loadAttr = curses.A_NORMAL
    else:
        menuSelector = Slider(0,2,1)
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
                    return "INTRO"
                elif menuSelector.getValue() == 2:
                    return "LOAD"
                elif menuSelector.getValue() == 3:
                    return "OPTION"
                elif menuSelector.getValue() == 4:
                    introLoop = False
                    return "END"
            else:
                if menuSelector.getValue() == 0:
                    return "INTRO"
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
    '''game loop for option screen'''
    pass

def save(stdscr, debugWindow, allStart):
    pass

def pOption(stdscr, debugWindow, allStart):
    pass

def intro(stdscr, debugWindow, allStart):
    '''gameLoop for intro'''
    global debug
    global options
    global keyBinding

    #IntroSetup
    pauseSelector = Slider(0,4,1)
    blinker = Timer(True, 0.6, True)
    textToDisplay = []
    textToDisplay += storyInterpreter(story, "tutorial")
    logging.debug(str(textToDisplay))

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

    #introLoop
    textDelay = (100 - options["Text display speed"])*textDelayMultiplier*0.01
    paused = False
    waited = False

    textLog = []
    top = max(0,len(textLog)-1)
    lineCount = 0
    autoUp = False

    step = 0
    lastStep = -1
    stepper = Timer(True, textDelay, True)
    previousSteping = True

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

        if paused:
            if waited: #exit confirm loop
                if holdCh == keyBinding["LEFT"]:
                    waitSelector.decrease()
                if holdCh == keyBinding["RIGHT"]:
                    waitSelector.increase()
                if holdCh == "\n":
                    if waitSelector.getValue() == 0:
                        #savefile <------------------------------------
                        return "MAIN"
                    elif waitSelector.getValue() == 1:
                        return "MAIN"
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
                        return "SAVE"
                    elif pauseSelector.getValue() == 2:
                        return "pLOAD"
                    elif pauseSelector.getValue() == 3:
                        return "pOPTION"
                    elif pauseSelector.getValue() == 4:
                        waitSelector = Slider(0,1,1)
                        if saved: #<----------------------------------Compare current state to last saved state?
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
                        commandHandeler(inputUpper)
                    autoUp = True
                    textBuffer = ""
            elif holdCh == keyBinding["DELETE"]:
                textBuffer = textBuffer[:len(textBuffer)-1]
            elif len(str(holdCh)) == 1:
                textBuffer += holdCh
            #AdditionalShortcutKeys
            if holdCh == keyBinding["TEXTUP"]:
                if top > 0:
                    top -= 1
                    autoUp = False
            if holdCh == keyBinding["TEXTDOWN"]:
                if top < len(textLog)-1:
                    top += 1
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
            step = stepper.getStep()
            stepperTime = stepper.getTime()
            # Text processing
            if step != lastStep:
                for line in textToDisplay[step]:
                    if line == "\\n":
                        textLog.append(" ")
                    else:
                        textLog.append(line)
                autoUp = True
            if step == len(textToDisplay)-1 and stepper.getProgressing():
                stepper.pause()
            if step != len(textToDisplay)-1 and not stepper.getProgressing():
                stepper.resume()
            lastStep = stepper.getStep()
            if autoUp:
                top = max(top,len(textLog)-screenHeight+lowerlineRY+5+textUpOffset)
                autoUp = False

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
            for i in range(top,min(top+screenHeight-lowerlineRY-5,len(textLog))):
                if type(textLog[i]) == list:
                    stdscr.addstr(upperlineRY+1+i-top, 0, textLog[i][0], textLog[i][1])
                elif type(textLog[i]) == str:
                    stdscr.addstr(upperlineRY+1+i-top, 0, textLog[i])

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
                    "INTRO",
                    [holdCh],
                    stop - allStart,
                    1/max(actualLoopLength,0.000001),
                    averageLoopLength,
                    str(step) + " / " + "{:.5}".format(stepperTime),
                    top,
                )

        curses.doupdate()

        #Loop and time
        loopCount += 1
        stop = time.time()
        loopLength = stop-start
        time.sleep(0.01)
        actualStop = time.time()
        actualLoopLength = actualStop-start

#Code
def main(stdscr):
    '''the main code inside the wrapper for curses module'''
    global debug
    global screenWidth
    global screenHeight

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
    gameLoop = True
    saves = []
    try:
        savefileNames = os.listdir("saves")
        if len(savefileNames) == 0:
            hasSave = False
        else:
            hasSave = True
            saves = [None for x in range(len(savefileNames))]
            for name in savefileNames:
                with open("saves/" + str(name), "rb") as file:
                    save = pickle.load(file)
                saves[save["index"]] = save
    except:
        pass
        hasSave = False

    #TEMPORARY VARIABLES <------------------------ (REMOVE BEFORE USE)
    debug = True

    currentLoop = "MENU" #Creat NOTE loop to communicate with classmates (setting MAC key binding, etc.)
    while gameLoop:
        if currentLoop == "MENU":
            currentLoop = menu(stdscr, debugWindow, hasSave, allStart)
        elif currentLoop == "INTRO":
            currentLoop = intro(stdscr, debugWindow, allStart)
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
