#!/usr/bin/python2
# -*- coding: utf-8 -*-

import csv
import subprocess
import sys
import curses
import os
from collections import deque
import random

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

class Witch:
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

class Santa:
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

class Snowflake:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def draw(self, stdscr, games, current):
    maxy, maxx = stdscr.getmaxyx()
    try:
      l = len(games[current][0] + "  (" + games[current][1] + ")")
      if self.y == maxy / 2 - 1 and maxx / 2 - 12 <= self.x < maxx / 2 - 12 + l :
        stdscr.addch(self.y, self.x, '*', curses.A_REVERSE)
      else:
        stdscr.addstr(self.y, self.x, '*')
    except:
      pass

  def update(self, stdscr):
    maxy, maxx = stdscr.getmaxyx()
    self.y = self.y + 1
    tmp = random.random()
    if tmp < 0.2 and self.x > 0:
      self.x = self.x - 1
    elif tmp > 0.8 and self.x < maxx - 1:
      self.x = self.x + 1

snow = []
def update_snow(stdscr, games, current):
  maxy, maxx = stdscr.getmaxyx()
  for flake in snow:
    flake.update(stdscr)
    if flake.y >= maxy:
      snow.remove(flake)
  snow.append(Snowflake(random.randint(0, maxx-1), 0))

def draw_snow(stdscr, games, current):
  for flake in snow:
    flake.draw(stdscr, games, current)


class Rainflake:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def draw(self, stdscr, games, current):
    maxy, maxx = stdscr.getmaxyx()
    try:
      l = len(games[current][0] + "  (" + games[current][1] + ")")
      if self.y == maxy / 2 - 1 and maxx / 2 - 12 <= self.x < maxx / 2 - 12 + l:
        stdscr.addch(self.y, self.x, '/', curses.A_REVERSE)
      else:
        stdscr.addstr(self.y, self.x, '/')
    except:
      pass

  def update(self, stdscr):
    maxy, maxx = stdscr.getmaxyx()
    self.y = self.y + 1
    self.x = self.x - 1

rain = []
def update_rain(stdscr, games, current):
  maxy, maxx = stdscr.getmaxyx()
  for flake in rain:
    flake.update(stdscr)
    if flake.y >= maxy:
      rain.remove(flake)
  rain.append(Rainflake(random.randint(0, maxy + maxx-1), 0))
  rain.append(Rainflake(random.randint(0, maxy + maxx-1), 0))

def draw_rain(stdscr, games, current):
  for flake in rain:
    flake.draw(stdscr, games, current)


def menu_loop(stdscr, games):
  curses.curs_set(0)

  i = 0

  stdscr.timeout(200)

  maxy, maxx = stdscr.getmaxyx()

  santa = Santa(maxx-1, 20)
  witch = Witch(maxy-9, 3)

  while True:
    try:
      draw_menu(stdscr, games, i)
      # draw_snow(stdscr, games, i)
      # santa.draw(stdscr)
      draw_rain(stdscr, games, i)
      witch.draw(stdscr)
      stdscr.refresh()
      while True:
        c = stdscr.getch()
        if c != -1:
          break
        stdscr.erase()
        draw_menu(stdscr,games,i)
        # update_snow(stdscr, games, i)
        # draw_snow(stdscr, games, i)
        # santa.update(stdscr)
        # santa.draw(stdscr)
        update_rain(stdscr, games, i)
        draw_rain(stdscr, games, i)
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
	if i == 0:
	  subprocess.call(["dosbox", games[0][2], "-fullscreen", "-exit"])
	  stdscr.clear()
        elif games[i][1] == "dosbox":
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
    except:
      pass

def main():
  games = find_games()
  print len(games)

  curses.wrapper(menu_loop,games)

if __name__=="__main__":
  main()
