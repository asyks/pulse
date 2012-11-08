
## standard python library imports
import urllib2
import json
import logging
from datetime import datetime 

## pulse class/object imports
from utility import *
from datamodel import *

## Procedures for importing a json object from a Google Spreadhsheet using Google Docs Atom feed service
## And creating Google DataStore models from the json object

def import_json_object(feed, sskey, worksheet): ## Grabs the json object through the Atom feed service - returns the json object 

  base_url = 'https://spreadsheets.google.com/feeds/%s/%s/%s/public/basic?alt=json'
  request_url = base_url % (feed, sskey, worksheet)
  page_requested = urllib2.urlopen(request_url)
  page_content = page_requested.read()

  json_object = json.loads(page_content)

  return json_object


def cnv_json_to_dt(time_string): ## Converts a string with date format into a Python datetime object - returns a datetime object

  time_stamp = datetime.strptime(time_string,'%m/%d/%Y %H:%M:%S')

  return time_stamp


def get_vals_from_json(feed, sskey, worksheet): ## Gets field values from the json object - returns a list of atom field values

  json_object = import_json_object(feed, sskey, worksheet)
  entries = json_object['feed']['entry']
  scores = []

  contents = [ i['content']['$t'] for i in entries ]

  return contents
 

def get_scores_from_atom(feed, sskey, worksheet): ## Slices a list into segments of length 8 - returns a list of scores

  contents = get_vals_from_json(feed, sskey, worksheet)
  offset, scores_max = 8, len(contents) + 1
  starts = range(0, scores_max, offset)
  blocks = [ contents[i : i + offset] for i in starts ]

  scores = [ Scores.create_score(i[1],i[2],int(i[3]),int(i[4]),int(i[5]),int(i[6]),i[7],cnv_json_to_dt(i[0])) for i in blocks if len(i) == 8 ]

  return scores
