
import logging
## standard python library imports
import json

## pulse class/object imports
from datamodel import *
from utility import *


def createGuageObject(scores):

  scores = list(scores)

  current_week = scores[0].week_date
  weeks = dict()
  entries_per_week, sum_of_pr, sum_of_cm, sum_of_ex, sum_of_ch, sum_of_pl = 0,0,0,0,0,0
  store_op, reset_op, iterate_op = False, False, True 

  for score in scores:

    pr, cm, ex, ch, pl = score.pride, score.communication, score.expectations, score.challenge, score.pulse
    
    if score.week_date != current_week: ## if state is start of new week then don't iterate, store and reset
      iterate_op, store_op, reset_op = False, True, True

    if scores.index(score) == len(scores) - 1: ## if state is last object then interate and store, but don't reset
      interate_op, store_op, reset_op = True, True, False

    if iterate_op: ## iterate operation
      entries_per_week += 1  
      sum_of_pr += pr
      sum_of_cm += cm
      sum_of_ex += ex
      sum_of_ch += ch
      sum_of_pl += pl

    if store_op: ## store operation
      weeks[current_week] = dict()
      weeks[current_week]['entries_per_week'] = entries_per_week
      weeks[current_week]['pr'] = sum_of_pr
      weeks[current_week]['cm'] = sum_of_ex
      weeks[current_week]['ex'] = sum_of_cm
      weeks[current_week]['ch'] = sum_of_ch
      weeks[current_week]['pl'] = sum_of_pl

    if reset_op: ## reset operation
      iterate_op, store_op, reset_op = True, False, False ## just iterate the next iterable
      current_week = score.week_date ## reset current_week
      entries_per_week = 1 ## reset entries_per_week
      sum_of_pr, sum_of_cm, sum_of_ex, sum_of_ch, sum_of_pl = pr, cm, ex, ch, pl

  logging.warning(weeks)

  json_object, cols_one, cols_two = dict(), dict(), dict() 
  columns  = list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'date', 'Date', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'

  columns.append(cols_one); columns.append(cols_two)

  json_object['cols'] = columns
  json_object['rows'] = [ {"c":[{"v": format_datetime(score.timestamp)}, {"v": score.pulse}]} for score in scores ]

  json_object = json.dumps(json_object)

  return json_object
