
## standard python library imports
import urllib2
import json
import logging
from datetime import datetime 

## pulse class/object imports
from utility import *
from datamodel import *

## Imports a json object from a Google Spreadhsheet using Google Docs Atom feed service

def atom_import(feed, sskey, worksheet):

  base_url = 'https://spreadsheets.google.com/feeds/%s/%s/%s/public/basic?alt=json'
  request_url = base_url % (feed, sskey, worksheet)
  page_requested = urllib2.urlopen(request_url)
  page_content = page_requested.read()
  json_object = json.loads(page_content)
  entries = json_object['feed']['entry']

  scores = []

  contents = [ i['content']['$t'] for i in entries ]

  scores_max = len(contents) + 1
  nums = range(0, scores_max, 1)
  offset = 8
  starts = range(0, scores_max, offset)
  blocks = [ contents[i : i + offset] for i in starts ]

  for element in blocks:

    if element and len(element) == 8:
      logging.warning(element)
      timestamp = datetime.strptime(element[0],'%m/%d/%Y %H:%M:%S')

      score = Scores.create_score(element[1],
                                  element[2],
                                  int(element[3]),
                                  int(element[4]),
                                  int(element[5]),
                                  int(element[6]),
                                  element[7],
                                  timestamp)

      scores.append(score)

  return scores
