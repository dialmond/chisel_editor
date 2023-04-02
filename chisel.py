#!/usr/bin/env python3
from utils import NullChars
import curses
import time
import sys
import textwrap

HISTORY_SIZE = 100 #size of our history for "undo"
NEWLINE_CHAR = "↩" #character we use to draw newlines
#SPACE_CHAR = "█" # character we use to draw spaces
SPACE_CHAR = " " # character we use to draw spaces
EOF_CHAR = "◄" #character we use to draw where the file ends
wrapper = textwrap.TextWrapper(replace_whitespace=False)

class App:
    def __init__(self, size, alphabet, fileName):
        self.updateSize(size)
        self.voffset = 0 #you can scroll down
        self.vx, self.vy = (0,0) #view x, view y
        self.index = 0 #where cursor is
        self.k = None #key
        self.showPreview = True
        self.nullchars = NullChars(alphabet, fileName)

    def updateSize(self, size):
        self.height, self.screenWidth = size
        self.previewWidth = self.screenWidth // 2
        wrapper.width = self.previewWidth
        #self.height -= 1
        self.width = self.screenWidth-self.previewWidth-1

    def finalIndex(self):
        return self.width * (self.voffset + self.height) - 1

    def firstIndex(self):
        return self.width * self.voffset

    def doAction(self, stdscr):
        if self.k in ['KEY_UP', 'k']:
            self.index = max(self.index - self.width, 0)
        elif self.k in ['KEY_DOWN', 'j']:
            self.index += self.width
        elif self.k in ['KEY_LEFT', 'h']:
            self.index = max(0, self.index - 1)
        elif self.k in ['KEY_RIGHT', 'l']:
            self.index += 1
        elif self.k in ['b']:
            self.index = max(0, self.index - len(self.nullchars.alphabet))
        elif self.k in ['w']:
            self.index += len(self.nullchars.alphabet)
        elif self.k in [' ']:
            self.nullchars.insert(self.index)
            self.index += 1
        elif self.k in ['.']:
            if (self.nullchars.EOFIndex == -1
                or self.index < self.nullchars.EOFIndex):
                self.nullchars.EOFIndex = self.index
        #elif self.k in ['u']:
        #    self.nullchars.remove(self.index)
        if self.index < self.firstIndex():
            self.voffset -= 1
        elif self.index > self.finalIndex():
            self.voffset += 1

    def indexToView(self):
        index = self.index - (self.voffset * self.width)
        row = (int)(index / self.width)
        col = index % self.width
        return (row, col)

def drawAll(app, stdscr, previewpanel):
    drawEditor(app, stdscr)
    if app.showPreview and app.k in [' ', 'u', '.']:
        drawPreview(app, previewpanel)
        stdscr.refresh()
    row, col = app.indexToView()
    stdscr.move(row, col)

def drawEditor(app, stdscr):
    nullchars = app.nullchars
    index = app.voffset * app.width
    ncIndex = 0
    def isNull(start, index, end):
        return ((nullchars.EOFIndex != -1 and index > nullchars.EOFIndex)
            or ((start != -1 and start <= index and end==-1)
                or (start <= index <= end)))

    for row in range(app.height):
        for col in range(app.width):
            if ncIndex < len(nullchars.sortedKeys):
                start = nullchars.sortedKeys[ncIndex]
                end = nullchars.rangeDict[start]
            else:
                start = end = -1
            c = (EOF_CHAR if index == nullchars.EOFIndex
                 else nullchars.indexToCharacter(index))
            if c == ' ':
                c = SPACE_CHAR
            elif c == '\n':
                c = NEWLINE_CHAR
            style, color = (curses.A_DIM, 2) if isNull(start, index, end) else (curses.A_BOLD, 1)
            stdscr.addstr(row, col, c, curses.color_pair(color) | style)
            index += 1
            if end != -1 and index > end:
                ncIndex += 1

def drawPreview(app, previewpanel):
    previewpanel.erase()
    preview = '\n'.join(app.nullchars.toText(app.finalIndex()).splitlines()[:app.height])
    previewpanel.addstr(0, 0, preview)
    #previewpanel.addstr(0,0, "index " + str(app.index))
    #previewpanel.addstr(1,0, "final index " + str(app.finalIndex()))
    #previewpanel.addstr(2,0, "first index " + str(app.firstIndex()))
    #previewpanel.addstr(3,0, "index to view " + str(app.indexToView()))
    #previewpanel.addstr(4,0, "character " + str(app.nullchars.indexToCharacter(app.index)))
    previewpanel.refresh()

def main(stdscr):
    curses.noecho() # don't add pressed keys to screen
    curses.cbreak() #don't require enter to be pressed
    stdscr.keypad(True) #allow arrow keys

    #Initialize curses screen/color
    stdscr.erase()
    stdscr.refresh()
    curses.start_color()
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    fileName = 'debug.txt' #TODO: remove this
    alphabet = 'abcdefghijklmnopqrstuvwxyz \n'
    if len(sys.argv) >= 2:
        fileName = sys.argv[1]
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ \n'

    app = App(stdscr.getmaxyx(), alphabet, fileName)
    previewpanel = curses.newwin(
            app.height, app.previewWidth, 0, app.screenWidth-app.previewWidth)
    stdscr.move(0,0)
    drawPreview(app, previewpanel)
    while True:
        app.updateSize(stdscr.getmaxyx())
        app.doAction(stdscr)
        drawAll(app, stdscr, previewpanel)
        k = stdscr.getkey()
        app.k = k
        time.sleep(0)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print('bye!')
