
## standard python library imports
from datetime import datetime
from utility import *
from google.appengine.ext import db

import logging


class Scores(db.Model): ## datamodels for Team Pulse - Currently only Scores model

  username = db.StringProperty(required=True)
  project = db.StringProperty(required=True)
  pride = db.IntegerProperty(required=True)
  communication = db.IntegerProperty(required=True)
  expectations = db.IntegerProperty(required=True) 
  challenge = db.IntegerProperty(required=True) 
  pulse = db.FloatProperty(required=True)
  feedback = db.TextProperty() 
  timestamp = db.DateTimeProperty()
  week_date = db.DateProperty()
  week_num = db.IntegerProperty()
  submitted = db.DateTimeProperty(auto_now_add=True) 

  @classmethod
  def create_score(cls, un, pj, pr, cm, ex, ch, fb=None, ts=datetime.utcnow()):

    pl = (pr + cm + ex + ch) / 4.0

    ts_year, ts_month, ts_weekday, ts_week_num, ts_day = ts.year, ts.month, ts.weekday(), int(ts.strftime('%W')), ts.day
    if ts_weekday in (4,5,6):
      ts_week_num +=  1
    ts_day -= ts_weekday
    ts_week_date = datetime.date(datetime(ts_year, ts_month, ts_day))

    return cls(username = un,
               project = pj,
               pride = pr,
               communication = cm,
               expectations = ex,
               challenge = ch,
               pulse = pl,
               feedback = fb,
               timestamp = ts,
               week_date = ts_week_date,
               week_num = ts_week_num)

  @classmethod
  def put_score(cls, score): ## takes one score model instance and puts them in the datastore
    score.put()

  @classmethod
  def put_scores(cls, scores=[]): ## takes a list of score instances and puts them in the datastore
    db.put(scores)

  @classmethod
  def get_by_project(cls, pj): ## gets a list of n score instances by project and timestamp and returns them
    # n = 10
    scores = cls.all()
    scores = scores.filter('project =', pj).order('-timestamp').run()
    return scores

  @classmethod
  def get_by_username(un): ## gets a list of score instances by username and timestamp and returns them
    score = cls.all()
    score = score.filter('username =', un).order('-timestamp').get()
    return score

  @classmethod
  def drop_table(cls): ## drops the scores table
    all_scores = cls.all()
    db.delete(all_scores)

class Weeks(db.Model): ## datamodels for Team Pulse - Currently only Scores model

  project = db.StringProperty(required=True)
  pride = db.IntegerProperty(required=True)
  communication = db.IntegerProperty(required=True)
  expectations = db.IntegerProperty(required=True) 
  challenge = db.IntegerProperty(required=True) 
  pulse = db.FloatProperty(required=True)
  timestamp = db.DateTimeProperty()
  week_date = db.DateProperty()
  week_num = db.IntegerProperty()
  submitted = db.DateTimeProperty(auto_now_add=True) 

  @classmethod
  def create_score(cls, un, pj, pr, cm, ex, ch, fb=None, ts=datetime.utcnow()):

    pl = (pr + cm + ex + ch) / 4.0

    ts_year, ts_month, ts_weekday, ts_week_num, ts_day = ts.year, ts.month, ts.weekday(), int(ts.strftime('%W')), ts.day
    ts_week_date = datetime.date(datetime(ts_year, ts_month, ts_day))
    if ts_weekday in (4,5,6):
      ts_week_num +=  1

    return cls(username = un,
               project = pj,
               pride = pr,
               communication = cm,
               expectations = ex,
               challenge = ch,
               pulse = pl,
               feedback = fb,
               timestamp = ts,
               week_date = ts_week_date)

