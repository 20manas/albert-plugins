# -*- coding: utf-8 -*-

"""This is a simple python template extension.
Search bash/fish history and launch/copy commands from it.

This extension does simple case-insensitive search.

Synopsis: <trigger><query>"""

from albertv0 import *
from pathlib import Path
import re

__iid__ = "PythonInterface/v0.1"
__prettyname__ = "Shell History"
__version__ = "0.1"
__trigger__ = ">>"
__author__ = "Manas Khurana"

class Cmd:
  def __init__(self):
    self.history = []
    self.cmdSet = set()
  def add(self, cmd, time):
    if cmd[0:4] == 'func' or len(cmd) > 300 or cmd in self.cmdSet: return

    self.cmdSet.add(cmd)

    self.history.append({
      'cmd': cmd,
      'time': time,
    })
  def sort(self):
    def key(a):
      return a['time']
    self.history.sort(key = key, reverse = True)

history = Cmd()

def getBashHistory():
  home = str(Path.home())
  return open(home + '/.bash_history').read().splitlines()

def addBashHistory(lines):
  time = 0
  cmd = ''

  for line in lines:
    if re.match('#[0-9]*', line):
      if cmd != '':
        history.add(cmd, time)
      
      time = int(line.split('#')[1])
      cmd = ''
    else:
      if cmd != '' and time != 0:
        cmd += '\n' + line
      else:
        cmd = line
      
      if time != 0: history.add(cmd, 0)

  if cmd != '':
    history.add(cmd, time)

def getFishHistory():
  home = str(Path.home())
  return open(home + '/.local/share/fish/fish_history').read().splitlines()

def addFishHistory(lines):
  time = 0
  cmd = ''

  paths = False
  for line in lines:
    if re.match('- cmd: ', line):
      paths = False
      cmd = re.split('- cmd: ', line)[1]
    elif paths: continue
    elif re.match('  when: ', line):
      time = int(re.split('  when: ', line)[1])
      if cmd != '': history.add(cmd, time)
      cmd = ''
    elif re.match('  paths:', line):
      paths = True

def initialize():
  addFishHistory(getFishHistory())
  addBashHistory(getBashHistory())

  history.sort()

def handleQuery(query):
  if not query.isTriggered: return
  
  def containsQuery(line):
    if len(line['cmd']) > 200: return False
    return query.string.lower() in line['cmd'].lower()
  
  items = []
  for line in filter(containsQuery, history.history):
    item = Item()
    item.text = line['cmd']
    item.subtext = 'Launch in terminal "' + line['cmd'] + '"'
    item.completion = __trigger__ + line['cmd']
    item.icon = ':terminal'
    item.addAction(TermAction(text = 'Launch in terminal', commandline = line['cmd'].split(' ')))
    item.addAction(ClipAction(text = 'Copy command to clipboard', clipboardText = line['cmd']))
    item.addAction(ProcAction(text = 'Launch in background', commandline = line['cmd'].split(' ')))

    items.append(item)

  return items
