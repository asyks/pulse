
## Procedures for importing a json object from a Google Spreadhsheet using Google Docs Atom feed service
## And creating Google DataStore models from the json object

## standard python library imports
import urllib2
import json
import logging
from datetime import datetime 

## pulse class/object imports
from utility import *
from datamodel import *


## Grabs the json object through the Atom feed service - returns the json object

def import_json_object(feed, sskey, worksheet):

  base_url = 'https://spreadsheets.google.com/feeds/%s/%s/%s/public/basic?alt=json'
  request_url = base_url % (feed, sskey, worksheet)
  page_requested = urllib2.urlopen(request_url)
  page_content = page_requested.read()

  json_object = json.loads(page_content)

  return json_object


## Converts a string formatted as a Google Spreadsheet date into a Python datetime object - returns a datetime object

def cnv_json_to_dt(time_string):

  time_stamp = datetime.strptime(time_string,'%m/%d/%Y %H:%M:%S')

  return time_stamp


## Gets the values of each cell from the json object and stores them in a list - returns the list of values

def get_vals_from_json(feed, sskey, worksheet):

  json_object = import_json_object(feed, sskey, worksheet)
  entries = json_object['feed']['entry']
  scores = []

  contents = [ i['content']['$t'] for i in entries ]

  return contents
 

## Creates a list of scores by slicing a list of values into even 8 length segments - returns the list of scores

def get_scores_from_atom(feed, sskey, worksheet):

  contents = get_vals_from_json(feed, sskey, worksheet)
  offset, scores_max = 8, len(contents) + 1
  starts = range(0, scores_max, offset)
  blocks = [ contents[i : i + offset] for i in starts ]

  scores = [ Scores.create_score(i[1],i[2],int(i[3]),int(i[4]),int(i[5]),int(i[6]),i[7],cnv_json_to_dt(i[0])) for i in blocks if len(i) == 8 ]

  return scores
