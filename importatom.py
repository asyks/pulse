
import urllib2
import json
import logging

from utility import *
from datamodel import *
from datetime import datetime 
   
## Imports a json object from a Google Spreadhsheet using Google Docs Atom feed service

def atom_import(feed, sskey, worksheet):

  base_url = 'https://spreadsheets.google.com/feeds/%s/%s/%s/public/basic?alt=json'
  request_url = base_url % (feed, sskey, worksheet)
  page_requested = urllib2.urlopen(request_url)
  page_content = page_requested.read()
  json_object = json.loads(page_content)
  entries = json_object['feed']['entry']

  scores = []

  count = 0
  offset = 8

  while count < len(entries):

    entry_slice = entries[count:count + offset]
    score_container = []

    for item in entry_slice:

      content_value = item['content']['$t']
      logging.warning(content_value)
      score_container.append(content_value)

    timestamp = datetime.strptime(score_container[0],'%m/%d/%Y %H:%M:%S')

    score = Scores.create_score(score_container[1],
                                score_container[2],
                                int(score_container[3]),
                                int(score_container[4]),
                                int(score_container[5]),
                                int(score_container[6]),
                                score_container[7],timestamp)

    count += 8
    scores.append(score)

  return scores
