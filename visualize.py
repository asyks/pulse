
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

  return weeks

def weekAverage(total, entries):
  return round(total/entries, 2)

def createLineChartObject(weeks):

  line_chart_object, cols_one, cols_two = dict(), dict(), dict() 
  columns = list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'date', 'Date', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'

  columns.append(cols_one); columns.append(cols_two)

  line_chart_object['cols'] = columns
  line_chart_object['rows'] = [ {'c':[{'v': format_datetime(week['wk'])}, {'v': weekAverage(week['pl'], week['wk_en'])}]} for week in weeks ]

  line_chart_object = json.dumps(line_chart_object)

  return line_chart_object
 

def createPulseGaugeObject(weeks, n):

  logging.warning(weeks)
  guage_object, cols_one, cols_two = dict(), dict(), dict() 
  columns, rows = list(), list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'week', 'Week', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'
  columns.append(cols_one)
  columns.append(cols_two)
  guage_object['cols'] = columns

  rows.append( {'c':[{'v': format_datetime(weeks[n]['wk'])}, {'v': weekAverage(weeks[n]['pl'], weeks[n]['wk_en'])}]} )
  guage_object['rows'] = rows

  guage_object = json.dumps(guage_object)

  return guage_object


def createBreakoutGaugeObject(weeks, n):

  guage_object, cols_one, cols_two = dict(), dict(), dict() 
  columns, rows = list(), list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'score', 'Score', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'
  columns.append(cols_one)
  columns.append(cols_two)
  guage_object['cols'] = columns

  rows.append( {'c':[{'v': 'Pride'}, {'v': weekAverage(weeks[n]['pr'], weeks[n]['wk_en'])}]} )
  rows.append( {'c':[{'v': 'Communication'}, {'v': weekAverage(weeks[n]['cm'], weeks[n]['wk_en'])}]} )
  rows.append( {'c':[{'v': 'Expectations'}, {'v': weekAverage(weeks[n]['ex'], weeks[n]['wk_en'])}]} )
  rows.append( {'c':[{'v': 'Challenge'}, {'v': weekAverage(weeks[n]['ch'], weeks[n]['wk_en'])}]} )
  guage_object['rows'] = rows

  guage_object = json.dumps(guage_object)

  return guage_object


def createChartObjects(scores):

  weeks = createWeeksObject(scores)

  if len(weeks) >= 2:
    enough_entries = True     
    line_chart_object = createLineChartObject(weeks)
    this_week_pulse_gauge_object = createPulseGaugeObject(weeks, -1)
    last_week_pulse_gauge_object = createPulseGaugeObject(weeks, -2)
    this_week_breakout_gauge_object = createBreakoutGaugeObject(weeks, -1)
    last_week_breakout_guage_object = createBreakoutGaugeObject(weeks, -2)

    visual_objects = ( line_chart_object,
											 this_week_pulse_gauge_object,
											 last_week_pulse_gauge_object,
											 this_week_breakout_gauge_object,
											 last_week_breakout_guage_object)
  else:
    enough_entries = False
    visual_objects = (None, None, None, None, None)

  return enough_entries, visual_objects 

def createSummaryObject(scores):

  pl_sum, pl_count = 0, 0
  for score in scores:
    pl_sum, pl_count += score.pl_sum, score.pl_count
