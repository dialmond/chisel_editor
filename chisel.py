#!/usr/bin/env python3
from utils import NullChars, NullCharsIterator
import curses
import time
import sys
import textwrap

NEWLINE_CHAR = "↩" #character we use to draw newlines
#SPACE_CHAR = "█" # character we use to draw spaces
SPACE_CHAR = " " # character we use to draw spaces
EOF_CHAR = "◄" #character we use to draw where the file ends
wrapper = textwrap.TextWrapper(replace_whitespace=False)

class App:
    def __init__(self, size, fileName, alphabet=None):
        self.updateSize(size)
        self.voffset = 0 #you can scroll down
        self.vx, self.vy = (0,0) #view x, view y
        self.index = self.firstIndex() #where cursor is
        self.k = None #key
        self.showPreview = True
        self.nullchars = NullChars(fileName, alphabet)

    def updateSize(self, size):
        self.height, self.screenWidth = size
        self.previewWidth = self.screenWidth // 2
        wrapper.width = self.previewWidth
        self.width = self.screenWidth-self.previewWidth-1

    def finalIndex(self):
        return self.width * (self.voffset + self.height) - 1

    def firstIndex(self):
        return self.width * self.voffset

    def indexToView(self):
        index = self.index - (self.voffset * self.width)
        row = (int)(index / self.width)
        col = index % self.width
        return (row, col)

    def viewToIndex(self, x, y):
        return self.firstIndex() + x + y * self.width

    def doAction(self, stdscr):
        if self.k in ['KEY_UP', 'k']:
            self.index = max(self.index - self.width, 0)
        elif self.k == 'KEY_PPAGE':
            self.voffset = max(0, self.voffset - (self.height - 1))
            self.index = max(0, self.index - self.width * (self.height - 1))
        elif self.k in ['KEY_DOWN', 'j']:
            self.index += self.width
        elif self.k == 'KEY_NPAGE':
            self.voffset += self.height
            self.index += self.width * (self.height - 1)
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
        elif self.k == "KEY_MOUSE":
            _,x,y,_,b = curses.getmouse()
            if b == curses.BUTTON1_CLICKED:
                self.index = self.viewToIndex(x,y)

        if self.index < self.firstIndex():
            self.voffset -= 1
        elif self.index > self.finalIndex():
            self.voffset += 1

def drawAll(app, stdscr, previewpanel):
    drawEditor(app, stdscr)
    if app.showPreview and app.k in [' ', '.']:
        drawPreview(app, previewpanel)
        stdscr.refresh()
    row, col = app.indexToView()
    stdscr.move(row, col)

def drawEditor(app, stdscr):
    nullchars = app.nullchars
    index = app.firstIndex()
    ncIndex = max(nullchars.getSKIndex(index), 0)
    def isNull(start, index, end):
        return (index != nullchars.EOFIndex and
            ((nullchars.EOFIndex != -1 and index > nullchars.EOFIndex)
            or ((start != -1 and start <= index and end==-1)
                or (start <= index <= end))))

    for row in range(app.height):
        for col in range(app.width):
            if ncIndex < len(nullchars.sortedKeys) and ncIndex != -1:
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
    preview = ''
    x,y = (0,0)
    i = NullCharsIterator(app.nullchars)
    while y < app.height -1:
        try:
            c = next(i)
        except StopIteration:
            break
        preview += c
        if c == '\n':
            y += 1
            x = 0
        else:
            x += 1
            if x >= app.previewWidth:
                y += 1
                x = 0
    previewpanel.addstr(0, 0, preview)
    '''previewpanel.addstr(0,0, "index " + str(app.index))
    previewpanel.addstr(1,0, "final index " + str(app.finalIndex()))
    previewpanel.addstr(2,0, "first index " + str(app.firstIndex()))
    previewpanel.addstr(3,0, "index to view " + str(app.indexToView()))
    previewpanel.addstr(4,0, "character " + str(app.nullchars.indexToCharacter(app.index)))
    previewpanel.addstr(5,0, "eof index " + str(app.nullchars.EOFIndex))
    previewpanel.addstr(6,0, "voffset " + str(app.voffset))'''
    previewpanel.refresh()

def main(stdscr):
    curses.noecho() # don't add pressed keys to screen
    curses.cbreak() #don't require enter to be pressed
    stdscr.keypad(True) #allow arrow keys
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    #^allow mouse input

    #Initialize curses screen/color
    stdscr.erase()
    stdscr.refresh()
    curses.start_color()
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    if len(sys.argv) >= 2:
        fileName = sys.argv[1]
    else:
        raise Exception('provide a file to edit!')

    app = App(stdscr.getmaxyx(), fileName)
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
