
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
#    logging.warning('week_date is %s' % score.week_date)
#    logging.warning('current week is %s' % current_week)

    pr, cm, ex, ch, pl = score.pride, score.communication, score.expectations, score.challenge, score.pulse
    
    if score.week_date != current_week: ## if state is start of new week then store and reset
      store_op, reset_op = True, True

    if store_op: ## store operation
      week = dict()
      week['wk'] = current_week
      week['wk_en'] = wk_en
      week['pr'] = sum_of_pr
      week['cm'] = sum_of_cm
      week['ex'] = sum_of_ex
      week['ch'] = sum_of_ch
      week['pl'] = sum_of_pl
      weeks.append(week)

    if reset_op: ## reset operation
      current_week = score.week_date ## reset current_week
      wk_en, sum_of_pr, sum_of_cm, sum_of_ex, sum_of_ch, sum_of_pl = 0,0,0,0,0,0
      store_op, reset_op = False, False

    ## iterate operation
    wk_en += 1  
    sum_of_pr += pr
    sum_of_cm += cm
    sum_of_ex += ex
    sum_of_ch += ch
    sum_of_pl += pl

    if scores.index(score) == len(scores) - 1: ## if state is end of iterator then store
      week = dict()
      week['wk'] = current_week
      week['wk_en'] = wk_en
      week['pr'] = sum_of_pr
      week['cm'] = sum_of_cm
      week['ex'] = sum_of_ex
      week['ch'] = sum_of_ch
      week['pl'] = sum_of_pl
      weeks.append(week)

  return weeks

def findAverage(total, entries):
  return round(float(total)/float(entries), 2)

def createLineChartObject(weeks):

  line_chart_object, cols_one, cols_two = dict(), dict(), dict() 
  columns = list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'date', 'Date', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'

  columns.append(cols_one); columns.append(cols_two)

  line_chart_object['cols'] = columns
  line_chart_object['rows'] = [ {'c':[{'v': format_datetime(week['wk'])}, {'v': findAverage(week['pl'], week['wk_en'])}]} for week in weeks ]

  line_chart_object = json.dumps(line_chart_object)

  return line_chart_object
 

def createPulseGaugeObject(weeks, n):

  gauge_object, cols_one, cols_two = dict(), dict(), dict() 
  columns, rows = list(), list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'week', 'Week', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'
  columns.append(cols_one)
  columns.append(cols_two)
  gauge_object['cols'] = columns

  rows.append( {'c':[{'v': format_datetime(weeks[n]['wk'])}, {'v': findAverage(weeks[n]['pl'], weeks[n]['wk_en'])}]} )
  gauge_object['rows'] = rows

  gauge_object = json.dumps(gauge_object)

  return gauge_object


def createBreakoutGaugeObject(weeks, n):

  gauge_object, cols_one, cols_two = dict(), dict(), dict() 
  columns, rows = list(), list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'score', 'Score', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'
  columns.append(cols_one)
  columns.append(cols_two)
  gauge_object['cols'] = columns

  rows.append( {'c':[{'v': 'Pride'}, {'v': findAverage(weeks[n]['pr'], weeks[n]['wk_en'])}]} )
  rows.append( {'c':[{'v': 'Communication'}, {'v': findAverage(weeks[n]['cm'], weeks[n]['wk_en'])}]} )
  rows.append( {'c':[{'v': 'Expectations'}, {'v': findAverage(weeks[n]['ex'], weeks[n]['wk_en'])}]} )
  rows.append( {'c':[{'v': 'Challenge'}, {'v': findAverage(weeks[n]['ch'], weeks[n]['wk_en'])}]} )
  gauge_object['rows'] = rows

  gauge_object = json.dumps(gauge_object)

  return gauge_object


def createChartObjects(scores):

  weeks = createWeeksObject(scores)

  if len(weeks) >= 2:
    enough_entries = True     
    line_chart_object = createLineChartObject(weeks)
    this_week_pulse_gauge_object = createPulseGaugeObject(weeks, -1)
    last_week_pulse_gauge_object = createPulseGaugeObject(weeks, -2)
    this_week_breakout_gauge_object = createBreakoutGaugeObject(weeks, -1)
    last_week_breakout_gauge_object = createBreakoutGaugeObject(weeks, -2)

    visual_objects = ( line_chart_object,
											 this_week_pulse_gauge_object,
											 last_week_pulse_gauge_object,
											 this_week_breakout_gauge_object,
											 last_week_breakout_gauge_object)
  else:
    enough_entries = False
    visual_objects = (None, None, None, None, None)

  return enough_entries, visual_objects 

def createPulseifiedObject(scores):

  pulseified_object = dict()

  for score in scores:
    logging.warning(score.project)
    logging.warning(score.pulse)
    if score.project in pulseified_object:
      pulse_list = pulseified_object[score.project]
      pulse_list[0] += score.pulse
      pulse_list[1] += score.pride
      pulse_list[2] += score.communication
      pulse_list[3] += score.expectations
      pulse_list[4] += score.challenge
      pulse_list[5] += 1
    else:
      pulse_list = pulseified_object[score.project] = list()
      pulse_list.append(score.pulse)
      pulse_list.append(score.pride)
      pulse_list.append(score.communication)
      pulse_list.append(score.expectations)
      pulse_list.append(score.challenge)
      pulse_list.append(1)

  return pulseified_object
      
def createChartifiedObject(obj):

  gauge_object, cols_one, cols_two = dict(), dict(), dict() 
  columns, rows = list(), list()

  cols_one['id'], cols_one['label'], cols_one['type'] = 'project', 'Project', 'string'
  cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'
  columns.append(cols_one)
  columns.append(cols_two)
  gauge_object['cols'] = columns

  for key in obj:
    rows.append( {'c':[{'v': key}, {'v': findAverage(obj[key][0], obj[key][5])}]} )
  gauge_object['rows'] = rows

  gauge_object = json.dumps(gauge_object)

  return gauge_object

def createSummaryObject(scores):

  pulseified_object = createPulseifiedObject(scores)
  summary_gauge_object = createChartifiedObject(pulseified_object)
  return summary_gauge_object

def createProjectBreakoutObject(obj):

  breakout_gauges = list()

  for key in obj:

    gauge = list()
    gauge_object, cols_one, cols_two = dict(), dict(), dict() 
    columns, rows = list(), list()

    cols_one['id'], cols_one['label'], cols_one['type'] = 'score', 'Score', 'string'
    cols_two['id'], cols_two['label'], cols_two['type'] = 'pulse', 'Pulse', 'number'
    columns.append(cols_one)
    columns.append(cols_two)
    gauge_object['cols'] = columns

    rows.append( {'c':[{'v': 'Pride'}, {'v': findAverage(obj[key][1], obj[key][5])}]} )
    rows.append( {'c':[{'v': 'Communication'}, {'v': findAverage(obj[key][2], obj[key][5])}]} )
    rows.append( {'c':[{'v': 'Expectations'}, {'v': findAverage(obj[key][3], obj[key][5])}]} )
    rows.append( {'c':[{'v': 'Challenge'}, {'v': findAverage(obj[key][4], obj[key][5])}]} )
    gauge_object['rows'] = rows

    gauge_object = json.dumps(gauge_object)
    gauge.append(key.replace('\'','_').replace('-','_'))
    gauge.append(gauge_object)
    breakout_gauges.append(gauge)

  return breakout_gauges 

def createBreakoutObject(scores):

  pulseified_object = createPulseifiedObject(scores)
  breakout_gauges = createProjectBreakoutObject(pulseified_object)
  return breakout_gauges
