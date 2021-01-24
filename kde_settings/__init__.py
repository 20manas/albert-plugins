# -*- coding: utf-8 -*-

"""Search through KDE settings.

This extension indexes .desktop files in /usr/share/kservices5/ which contains shortcuts for \
KDE settings. It does a simple case-insensitive search (no regex, no fuzzy).

Synopsis: <query>"""

from albertv0 import *
import os, re
# from fuzzywuzzy import fuzz, process


__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'KDE Settings'
__version__ = '0.1'
__author__ = 'Manas Khurana'
# __dependencies__ = 'fuzzywuzzy'

settings = []

def initialize():
  path = '/usr/share/kservices5/'
  for file in os.listdir(path):
    if not file.endswith('.desktop'): continue
    exec = []
    name = ''
    icon = ''
    comment = ''
    keywords = ''

    for line in open(path + file).read().splitlines():
      if re.match('Exec=', line):
        exec = re.split('Exec=', line)[1]
      elif re.match('Name=', line):
        name = re.split('Name=', line)[1]
      elif re.match('Icon=', line):
        icon = re.split('Icon=', line)[1]
      elif re.match('Comment=', line):
        comment = re.split('Comment=', line)[1]
      elif re.search('Keywords=', line):
        keywords = re.split('Keywords=', line)[-1].lower()

    if name and exec and icon and comment:
      settings.append({
        'name': name,
        'exec': exec.split(' '),
        'icon': icon,
        'comment': comment,
        'execText': 'Open ' + name,
        'searchString': name.lower() + ' ' + comment.lower() + ' ' + keywords,
      })

def handleQuery(query):
  items = []
  if query.rawString == '': return items
  queryArr = query.rawString.lower().split(' ')

  def test(setting):
    for word in queryArr:
      if word in setting['searchString']: return True

  # for match in process.extractBests(query.rawString, settings.keys(), scorer = fuzz.token_sort_ratio, score_cutoff = 50):
    # matchedItem = settings[match[0]]
  for matchedItem in (setting for setting in settings if test(setting)):
    item = Item()

    # item.id = match[0]
    item.id = matchedItem['name']
    item.icon = iconLookup(matchedItem['icon'])
    # item.text = match[0]
    item.text = matchedItem['name']
    item.subtext = matchedItem['comment']
    item.addAction(ProcAction(text = matchedItem['execText'], commandline = matchedItem['exec']))

    items.append(item)

  return items
