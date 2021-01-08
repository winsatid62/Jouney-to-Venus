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

# global variables
textDelayMultiplier = 1
debug = False
textSpeed = 1
screenWidth = 0
screenHeight = 0

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


#setup default saveState
saveState = {
    "map":{
        "room4012":MapNode(
            "Room 4012",
            "This is where you are staying. It is similar to normal hotel rooms found on earth.",
            "It shaped like an L. The walls are blue with white accents, and the room is basked in a warm orange tinted light."
        ),
        "testSpace":MapNode(
            "White void",
            "It is all white. You see nothing but white. There is no horizon line, no sky, no ground. There is nothing but white. ",
            "There is no shadow, no shade, no perspective. You feel like standing on a normal ground, but you cannot distinguish where the ground start or where the sky end. You can still feel yourself, so that mean can see yourself. You just unable to distinguish it from anything else. It is all white.",
            "You woke up and all you see is white. You looked around and all you see is white. You can't even see yourself."
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

def getTexts(list, key):
    '''gets lines from "story.txt" with coresponding key'''
    start = list.index("[" + key + "-")
    end = list.index("-" + key + "]")
    texts = [list[i] for i in range(start+1,end)]
    return texts

def str_wrap(string, width):
    '''return a list of lines of text confined to width (not cutting words)'''
    chCount = 0
    expectedLines = len(string)//width
    retList = [None for i in range(expectedLines+math.ceil(100/width))]
    list = string.split()
    lastLine = 0
    for i in range(len(list)):
        word = list[i]
        if i == 0:
            chCount += len(word)
        else:
            chCount += 1 + len(word)
        if chCount%width == 0:
            retList[(chCount//width)-1] += (" " + str(word))
            lastLine = (chCount//width)-1
        else:
            if lastLine != chCount//width:
                chCount -= 1 + len(word)
                chCount += width-(chCount%width)
                chCount += 1 + len(word)
            if i == 0:
                if retList[0] == None:
                    retList[0] = str(word)
                else:
                    retList[0] += str(word)
            else:
                if chCount%width <= len(word)+1:
                    chCount -= 1
                    if retList[chCount//width] == None:
                        retList[chCount//width] = str(word)
                    else:
                        retList[chCount//width] += str(word)
                    lastLine = chCount//width
                else:
                    if retList[chCount//width] == None:
                        retList[chCount//width] = (" " + str(word))
                    else:
                        retList[chCount//width] += (" " + str(word))
                    lastLine = chCount//width
    while True:
        if None in retList:
            retList.pop(retList.index(None))
        else:
            break
    return retList

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
#screenName, debugWindow, holdCh, loopCount, allStart, stop, loopLength, actualLoopLength, averageLoopLength, pressList, step, stepperTime):
    '''show the debug overley with informations (arguments)'''
    debugWindow.erase()
    for index, arg in enumerate(args):
        if type(arg) == int:
            debugWindow.addstr(index, (20-len("{}".format(str(arg)))), "{}".format(str(arg)))
        elif type(arg) == float:
            debugWindow.addstr(index, (20-len("{:.5f}".format(arg))), "{:.5f}".format(arg))
        elif type(arg) == str:
            debugWindow.addstr(index, (20-len("{}".format(arg))), "{}".format(arg))
        else:
            debugWindow.addstr(index, (20-len("{}".format(str(arg)))), "{}".format(str(arg)))
    '''
    debugWindow.addstr(0, (20-len("{}".format([holdCh]))), "{}".format([holdCh]))
    debugWindow.addstr(1, (20-len("{:.2f}".format(loopCount/100))), "{:.2f}".format(loopCount/100))
    debugWindow.addstr(2, (20-len("{:.2f}".format(stop - allStart))), "{:.2f}".format(stop - allStart))
    debugWindow.addstr(3, (12), "{:.6f}".format(loopLength))
    debugWindow.addstr(4, (12), "{:.6f}".format(actualLoopLength))
    debugWindow.addstr(5, 20-len("{:.6f}".format(1/max(actualLoopLength,0.000001))), "{:.6f}".format(1/max(actualLoopLength,0.000001)))
    debugWindow.addstr(6, (12), "{:.6f}".format(averageLoopLength))
    debugWindow.addstr(7, 20-len(str(screenName)), str(screenName))
    debugWindow.addstr(8, (20-len("{}, {}".format(step, stepperTime))), "{}, {}".format(step, stepperTime))
    '''
    debugWindow.noutrefresh(0,0, 0,screenWidth-20,screenHeight,screenWidth)

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
            debugWindowUpdate(debugWindow, [holdCh], loopCount/100, stop - allStart, loopLength, actualLoopLength,
                              1/max(actualLoopLength,0.000001), averageLoopLength, "MENU", )

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
    textList = getTexts(story, "tutorial")
    wrappedTextList = []
    for line in textList:
        wrappedTextList.append(str_wrap(line, screenWidth))

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
                    if inputUpper in commandDict["PAUSE"]:
                        paused, previousSteping = pause(stepper, paused, previousSteping)
                    else:
                        commandHandeler(inputUpper)
                    textLog += [[str(textBuffer), curses.A_DIM]]#callback on the terminal
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
            if step != lastStep:
                #textLog.append(str(wrappedTextList))
                for line in wrappedTextList[step]:
                    if line == "\\n":
                        textLog.append(" ")
                    else:
                        textLog.append(line)
                autoUp = True

            if step == len(textList)-1 and stepper.getProgressing():
                stepper.pause()

            lastStep = stepper.getStep()

            if autoUp:
                top = max(top,len(textLog)-(screenHeight-lowerlineRY-5))
                autoUp = False

        #Display
        stdscr.erase()
        if paused:
            if waited: #exit confirm loop
                y,x = stdscr.relativeAddtext(0.5, 0.5, "Do you want to save the game before quiting?")
                stdscr.addstr(y+2,x-5, "{}YES".format(conY))
                stdscr.addstr(y+2,x+2, "{}NO".format(conN))
            else: #pause loop
                y,x = stdscr.relativeAddtext(0.3, 0.5, "PAUSED")
                stdscr.addstr(y+int(screenWidth/10), x-math.ceil(len("{}CONTINUE{}".format(l0, r0))/2), "{}CONTINUE{}".format(l0, r0))
                stdscr.addstr(y+int(screenWidth/10)+1, x-math.ceil(len("{}  SAVE  {}".format(l1, r1))/2), "{}  SAVE  {}".format(l1, r1))
                stdscr.addstr(y+int(screenWidth/10)+2, x-math.ceil(len("{}  LOAD  {}".format(l2, r2))/2), "{}  LOAD  {}".format(l2, r2))
                stdscr.addstr(y+int(screenWidth/10)+3, x-math.ceil(len("{} OPTION {}".format(l3, r3))/2), "{} OPTION {}".format(l3, r3))
                stdscr.addstr(y+int(screenWidth/10)+4, x-math.ceil(len("{}  QUIT  {}".format(l4, r4))/2), "{}  QUIT  {}".format(l4, r4))
        else: #normal loop
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
                    stdscr.addstr(upperlineRY+1+i-top,0,textLog[i][0],textLog[i][1])
                elif type(textLog[i]) == str:
                    stdscr.addstr(upperlineRY+1+i-top,0,textLog[i])

        stdscr.noutrefresh()

        if debug:
            if paused:
                debugWindowUpdate(debugWindow, [holdCh], loopCount/100, stop - allStart, loopLength, actualLoopLength,
                                  1/max(actualLoopLength,0.000001), averageLoopLength, "PAUSE",
                                  (step, stepperTime), )
            else:
                debugWindowUpdate(debugWindow, [holdCh], loopCount/100, stop - allStart, loopLength, actualLoopLength,
                                  1/max(actualLoopLength,0.000001), averageLoopLength, "INTRO",
                                  (step, stepperTime), )

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

    curses.curs_set(False)
    stdscr.nodelay(True)
    debugWindow = curses.newpad(10, 20)

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
