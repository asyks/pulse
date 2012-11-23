
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

  for score in scores:

    pr, cm, ex, ch, pl = score.pride, score.communication, score.expectations, score.challenge, score.pulse
    logging.warning(scores.index(score))
    logging.warning(len(scores)-1)
    logging.warning(scores.index(score) == len(scores) - 1)

    if score.week_date != current_week or scores.index(score) == len(scores) - 1:
      logging.warning('elif')
      weeks[current_week] = dict()
      weeks[current_week]['entries_per_week'] = entries_per_week
      weeks[current_week]['pr'] = sum_of_pr
      weeks[current_week]['cm'] = sum_of_ex
      weeks[current_week]['ex'] = sum_of_cm
      weeks[current_week]['ch'] = sum_of_ch
      weeks[current_week]['pl'] = sum_of_pl

      current_week = score.week_date
      entries_per_week = 1
      sum_of_pr = pr
      sum_of_cm = cm
      sum_of_ex = ex
      sum_of_ch = ch
      sum_of_pl = pl

    elif score.week_date == current_week:
      entries_per_week += 1  
      sum_of_pr += pr
      sum_of_cm += cm
      sum_of_ex += ex
      sum_of_ch += ch
      sum_of_pl += pl

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
