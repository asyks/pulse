
##
# Procedures for importing a json object from a Google Spreadhsheet
# makes use of the Google Docs Atom feed service
##

# standard python library imports
import urllib2, json, logging
from datetime import datetime 
# pulse class/object imports
from utility import *
from datamodel import *

# Returns a json of Google Docs data using the Atom feed service 
def import_json_object(feed, sskey, worksheet):  
  base_url = 'https://spreadsheets.google.com/feeds/%s/%s/%s/public/basic?alt=json'
  request_url = base_url % (feed, sskey, worksheet)
  page_requested = urllib2.urlopen(request_url)
  page_content = page_requested.read()
  json_object = json.loads(page_content)
  return json_object

# Returns a Python datetime object
def cnv_json_to_dt(time_string):
  time_stamp = datetime.strptime(time_string,'%m/%d/%Y %H:%M:%S')
  return time_stamp

# Returns a list of Atom field values
def get_vals_from_json(feed, sskey, worksheet): 
  json_object = import_json_object(feed, sskey, worksheet)
  entries = json_object['feed']['entry']
  scores = []
  contents = [ i['content']['$t'] for i in entries ]
  return contents
 
# Slices a list into segments of length 8 - returns a list of scores
def get_scores_from_atom(feed, sskey, worksheet):

  contents = get_vals_from_json(feed, sskey, worksheet)
  offset, scores_max = 8, len(contents) + 1
  starts = range(0, scores_max, offset)
  blocks = [ contents[i : i + offset] for i in starts ]

  scores = [ Scores.create_score(i[1],i[2],int(i[3]),int(i[4]),int(i[5]),int(i[6]),i[7],cnv_json_to_dt(i[0])) for i in blocks if len(i) == 8 ]

  return scores
