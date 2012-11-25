
## standard python library imports
import json
import logging

## pulse class/object imports
from datamodel import *
from utility import *


def createWeeksObject(scores):

  current_week = scores[0].week_date
  weeks = list()
  wk_en, sum_of_pr, sum_of_cm, sum_of_ex, sum_of_ch, sum_of_pl = 0,0,0,0,0,0
  store_op, reset_op, iterate_op = False, False, True ## set initial state: iterate but don't store or reset

  for score in scores:

    pr, cm, ex, ch, pl = score.pride, score.communication, score.expectations, score.challenge, score.pulse
    
    if score.week_date != current_week: ## if state is start of new week then don't iterate, store and reset
      iterate_op, store_op, reset_op = False, True, True

    if scores.index(score) == len(scores) - 1: ## if state is last object then interate and store, but don't reset
      interate_op, store_op, reset_op = True, True, False

    if iterate_op: ## iterate operation
      wk_en += 1  
      sum_of_pr += pr
      sum_of_cm += cm
      sum_of_ex += ex
      sum_of_ch += ch
      sum_of_pl += pl

    if store_op: ## store operation
      week = dict()
      # week.__setitem__(current_week, dict())
      week['wk'] = current_week
      week['wk_en'] = wk_en
      week['pr'] = sum_of_pr
      week['cm'] = sum_of_ex
      week['ex'] = sum_of_cm
      week['ch'] = sum_of_ch
      week['pl'] = sum_of_pl
      weeks.append(week)

    if reset_op: ## reset operation
      iterate_op, store_op, reset_op = True, False, False ## just iterate the next iterable
      current_week = score.week_date ## reset current_week
      wk_en = 1 ## reset entries_per_week
      sum_of_pr, sum_of_cm, sum_of_ex, sum_of_ch, sum_of_pl = pr, cm, ex, ch, pl

  logging.warning(weeks)
  return weeks


def createLineChartObject(weeks):

  json_object, cols_one, cols_two = dict(), dict(), dict() 
  columns  = list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'date', 'Date', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'

  columns.append(cols_one); columns.append(cols_two)

  json_object['cols'] = columns
  json_object['rows'] = [ {'c':[{'v': format_datetime(week['wk'])}, {'v': week['pl'] / week['wk_en']}]} for week in weeks ]

  json_object = json.dumps(json_object)

  return json_object
 

def createGuageObject(weeks):

  guage_object, cols_one, cols_two = dict(), dict(), dict() 
  columns, rows = list(), list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'week', 'Week', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'
  columns.append(cols_one)
  columns.append(cols_two)
  guage_object['cols'] = columns

  current_week, sum_of_pulses, num_of_entries = format_datetime(weeks[0]['wk']), weeks[0]['pl'], weeks[0]['wk_en']
  pulse_of_week = sum_of_pulses / num_of_entries
  rows.append(current_week)
  rows.append(pulse_of_week)
  guage_object['rows'] = rows

  guage_object = json.dumps(guage_object)

  return guage_object


def createChartObjects(scores):

  weeks = createWeeksObject(scores)
  json_object = createLineChartObject(weeks)
  guage_object = createGuageObject(weeks) # guage object isn't working

  return json_object, guage_object
