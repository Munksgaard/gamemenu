#!/usr/bin/python2
# -*- coding: utf-8 -*-

import csv
import subprocess
import sys
import curses
import os
from collections import deque
import random
import getopt

class IScreenObject():
  def __init__():
    raise NotImplementedError("This class cannot be instantiated")
  def update(self, stdscr):
    raise NotImplementedError("This method cannot be called")
  def draw(self, stdscr):
    raise NotImplementedError("This method cannot be called")

def find_games():
  games = []
  with open('gamelist', 'r') as gamelist:
    gamereader = csv.reader(gamelist, delimiter=';')
    for game in gamereader:
      games.append(game)
  return games

def draw_menu(stdscr, games, i):
  maxy, maxx = stdscr.getmaxyx()
  x = maxx / 2 - 12
  midy = maxy / 2 - 1

  stdscr.addstr(midy, x, games[i][0] + "  (" + games[i][1] + ")", curses.A_REVERSE)

  starty = max(midy - i, 0)
  startindex = max(i - midy, 0)
  for y, game in enumerate(games[startindex:i]):
    stdscr.addstr(starty + y, x, game[0] + "  (" + game[1] + ")")

  endindex = min(len(games), i + (maxy - midy))
  for y, game in enumerate(games[i+1:endindex]):
    stdscr.addstr(midy + y + 1, x, game[0] + "  (" + game[1] + ")")

def draw_sprite(start_y, start_x, sprite, stdscr, escape_char = None):
  maxy, maxx = stdscr.getmaxyx()
  for y, line in enumerate(sprite.splitlines()):
    for x, c in enumerate(line):
      if 0 <= start_x + x < maxx and 0 <= start_y + y < maxy and c != escape_char:
        stdscr.addch(start_y + y, start_x + x, c)

class Witch(IScreenObject):
  def __init__(self, y, x):
    self.x = x
    self.y = y
    filehandle = open("halloween.txt")
    self.sprites = filehandle.read().split("@\n")
    filehandle.close()
    self.current_sprite = 0

  def draw(self, stdscr):
    draw_sprite(self.y, self.x, self.sprites[self.current_sprite], stdscr)

  def update(self):
    self.current_sprite = (self.current_sprite + 1) % len(self.sprites)

class Santa(IScreenObject):
  def __init__(self, x, y):
    self.x = x
    self.y = y

  sprite = """
@@@@@@@@@@@@@@@@@@@@   @
@@@   @@@@@@@@@@@@@  * @
@@  #  @@@@@@@@@@@  /\\ @
@ .O___,         __ {P    / @
@  (___)~~~~~/~~~*-(-_)|^^^| @
@  /\ /\     \_____||H_|___| @
@@                          @
"""[1:]

  def draw(self, stdscr):
    draw_sprite(self.y, self.x, self.sprite, stdscr, '@')

  def update(self, stdscr):
    maxy, maxx = stdscr.getmaxyx()
    self.x = self.x-1
    tmp = random.random()
    if tmp < 0.05 and self.y > 0:
      self.y = self.y - 1
    elif tmp > 0.95 and self.y < maxy - 1:
      self.y = self.y + 1

    if -1000 - (tmp * 1000) > self.x:
      self.x = maxx
      self.y = int(random.random() * maxy)

def draw_maybe_inverted_character(stdscr, char, y, x):
  try:
    if stdscr.inch(y, x) & curses.A_REVERSE != 0:
      stdscr.addch(y, x, char, curses.A_REVERSE)
    else:
      stdscr.addch(y, x, char)
  except curses.error:
    pass

class Snowflake(IScreenObject):
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def draw(self, stdscr):
    draw_maybe_inverted_character(stdscr, "*", self.y, self.x)

  def update(self, stdscr):
    maxy, maxx = stdscr.getmaxyx()
    self.y = self.y + 1
    tmp = random.random()
    if tmp < 0.2 and self.x > 0:
      self.x = self.x - 1
    elif tmp > 0.8 and self.x < maxx - 1:
      self.x = self.x + 1

snow = []
def update_snow(stdscr):
  maxy, maxx = stdscr.getmaxyx()
  for flake in snow:
    flake.update(stdscr)
    if flake.y >= maxy:
      snow.remove(flake)
  snow.append(Snowflake(random.randint(0, maxx-1), 0))

def draw_snow(stdscr):
  for flake in snow:
    flake.draw(stdscr)

class Raindrop(IScreenObject):
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def draw(self, stdscr):
    draw_maybe_inverted_character(stdscr, "/", self.y, self.x)

  def update(self, stdscr):
    maxy, maxx = stdscr.getmaxyx()
    self.y = self.y + 1
    self.x = self.x - 1

rain = []
def update_rain(stdscr):
  maxy, maxx = stdscr.getmaxyx()
  for flake in rain:
    flake.update(stdscr)
    if flake.y >= maxy:
      rain.remove(flake)
  rain.append(Raindrop(random.randint(0, maxy + maxx-1), 0))
  rain.append(Raindrop(random.randint(0, maxy + maxx-1), 0))

def draw_rain(stdscr):
  for flake in rain:
    flake.draw(stdscr)

def menu_loop(stdscr, games, debug):
  curses.curs_set(0)

  i = 0

  stdscr.timeout(200)

  maxy, maxx = stdscr.getmaxyx()

  santa = Santa(maxx-1, 20)
  witch = Witch(maxy-9, 3)

  while True:
    try:
      draw_menu(stdscr, games, i)
      # draw_snow(stdscr)
      # santa.draw(stdscr)
      draw_rain(stdscr)
      witch.draw(stdscr)
      stdscr.refresh()
      while True:
        c = stdscr.getch()
        if c != -1:
          break
        stdscr.erase()
        draw_menu(stdscr,games,i)
        # update_snow(stdscr)
        # draw_snow(stdscr)
        # santa.update(stdscr)
        # santa.draw(stdscr)
        update_rain(stdscr)
        draw_rain(stdscr)
        witch.update()
        witch.draw(stdscr)
      if c == curses.KEY_DOWN:
        i = min(i + 1, len(games) - 1)
      elif c == curses.KEY_UP:
        i = max(0, i - 1)
      elif c == ord('r'):
        games = find_games()
        i = 0
      elif c == ord('\n'):
        if games[i][1] == "dosbox":
          subprocess.call(["dosbox", games[i][2], "-fullscreen", "-exit"])
          stdscr.clear()
        elif games[i][1] == "mame":
          subprocess.call(["mame", "-autosave", games[i][2]])
          stdscr.clear()
        elif games[i][1] == "nes":
          subprocess.call(["fceux", "-fullscreen", "1", games[i][2]])
          stdscr.clear()
        elif games[i][1] == "console":
          olddir = os.getcwd()
          os.chdir(games[i][2])
          subprocess.call(["xterm", "-rv", "-fullscreen", "-e", games[i][3]])
          os.chdir(olddir)
          stdscr.clear()
        else:
          print "I don't know how to run that game..." + games[i][1]
      stdscr.erase()
    except KeyboardInterrupt:
      if debug:
        sys.exit(1)
      else:
        pass

def main(argv):
  debug = False
  errorFile = "error.log"
  # Parse input arguments
  try:
    opts, args = getopt.getopt(argv,"hde:",["errfile="])
  except getopt.GetOptError:
    print "gamemenu.py"
    sys.exit(2)
  for opt, arg in opts:
    if opt in ("-h","--debug"):
      print """gamemenu.py flags:
-h:\t\tPrint help
-d:\t\tEnable debug mode
-e, --errfile:\tSpecify the new location of std.err."""
      sys.exit(2)
    if opt in ("-d","--debug"):
      debug = True
    if opt in ("-e","--errfile"):
      errorFile = arg

  games = find_games()
  print len(games)

  # Redirect errors while curses is active
  f = open("error.log","w")
  original_stderr = sys.stderr
  sys.stderr = f
  curses.wrapper(menu_loop,games,debug)
  sys.stderr = original_stderr
  f.close()

if __name__=="__main__":
  main(sys.argv[1:])
