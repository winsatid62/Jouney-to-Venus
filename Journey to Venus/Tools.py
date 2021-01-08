# Jittipat Shobbakbun
# 10/31/2020
# Tools.py

# imports
from subprocess import call
from Player import Player
from Display import Display
import time

# global variables

def clear():
    if debug==False:
        call("clear",shell=True)

def countSection(story):
    list = []
    key = None
    for word in story:
        if len(word) > 1:
            if word[0] == "[" and word[-1] == "-":
                key = word[1:-1]
                start = story.index("[" + key.upper() + "-")
                end = story.index("-" + key.upper() + "]")
                texts = [story[i] for i in range(start+1,end)]
                max = 0
                count = 0
                lineCount = 0
                for line in texts:
                    lineCount += 1
                    count += len(line)
                    if len(line) > max:
                        max = len(line)
                print("SECTION KEY: " + str(key))
                print("Lines count: " + str(max))
                print("Max length : " + str(max))
                print("All length : " + str(count))
                print()

def main():
    print("CountSection[1], Example[2]")
    select = input("> ")
    if select == "CountSection" or select == "1":
        file = open("story.txt", "r")
        text = file.read()
        story = text.split("\n")
        file.close()
        countSection(story)
    elif select == "Example" or select == "2":
        pass

if __name__ == "__main__":
    main()
