
## standard python library imports
from datetime import datetime
from utility import *
from google.appengine.ext import db

import logging
import calendar

def scores_key(group='default'):
  return db.Key.from_path('Scores', group)

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
  week_num = db.FloatProperty()
  submitted = db.DateTimeProperty(auto_now_add=True) 

  @classmethod
  def create_score(cls, un, pj, pr, cm, ex, ch, fb=None, ts=datetime.utcnow()):

    ts_year, ts_month, ts_weekday, ts_day = ts.year, ts.month, ts.weekday(), ts.day
    adjust_month_or_year = False

    if ts_weekday in (3,4,5,6):
      ts_day = ts_day - ts_weekday
    elif ts_weekday in (0,1,2):
      ts_day = ts_day - ts_weekday - 7

    if ts_day <= 0:
      adjust_month_or_year = True

    if adjust_month_or_year == True:
      if ts_month == 1:
        ts_month = 12
        ts_year -= 1
      else:
        ts_month -= 1
      ts_day = calendar.monthrange(ts_year, ts_month)[1] - abs(ts_day)

    ts_week_date = datetime.date(datetime(ts_year, ts_month, ts_day))
    week_num = int(ts_week_date.strftime('%W'))
    week_id = ts_year + week_num / 100.0

    pl = (pr + cm + ex + ch) / 4.0

    logging.warning('score created')
    return cls(parent = scores_key(),
               username = un,
               project = pj,
               pride = pr,
               communication = cm,
               expectations = ex,
               challenge = ch,
               pulse = pl,
               feedback = fb,
               timestamp = ts,
               week_date = ts_week_date,
               week_num = week_id)

  @classmethod
  def put_score(cls, score): ## takes one score model instance and puts them in the datastore
    score.put()

  @classmethod
  def put_scores(cls, scores=[]): ## takes a list of score instances and puts them in the datastore
    db.put(scores)

  @classmethod
  def get_by_project(cls, pj, reverse_sort=False): ## gets a list of n score instances by project and timestamp and returns them
    sort = 'timestamp'
    if reverse_sort:
      sort = '-timestamp'
    scores = cls.all()
    scores = scores.filter('project =', pj).order(sort).run()
    return scores

  @classmethod
  def get_by_week(cls, wk, reverse_sort=False): ## gets a list of n score instances by project and timestamp and returns them
    sort = 'timestamp'
    if reverse_sort:
      sort = '-timestamp'
    scores = cls.all()
    scores = scores.filter('week =', wk).order(sort).run()
    return scores

  @classmethod
  def get_by_week_num(cls, week_num): ## gets a list of n score instances by project and timestamp and returns them
    scores = cls.all()
    scores = scores.filter('week_num =', week_num).run()
    return scores

  @classmethod
  def get_by_project_and_week(cls, pj, reverse_sort=False): ## gets a list of n score instances by project and timestamp and returns them
    sort = 'timestamp'
    if reverse_sort:
      sort = '-timestamp'
    scores = cls.all()
    scores = scores.filter('project =', pj).order(sort).run()
    return scores

  @classmethod
  def get_by_username(un): ## gets a list of score instances by username and timestamp and returns them
    score = cls.all()
    score = score.filter('username =', un).order('-timestamp').get()
    return score

  @classmethod
  def get_max_week(cls, pj=None): ## gets a list of n score instances by project and timestamp and returns them
    scores = cls.all()
    if pj is None:
      scores = scores.order('-timestamp').get()
    else:
      scores = scores.filter('project =', pj).order('timestamp').get()
    return scores.week_num

  @classmethod
  def drop_table(cls): ## drops the scores table
    all_scores = cls.all()
    db.delete(all_scores)

  @classmethod
  def remove_score(cls, score_key):
    db.delete(score_key)

def projects_key(group='default'):
  return db.Key.from_path('Projects', group)

class Projects(db.Model): ## datamodel for Team Pulse - Projects Model

  project = db.StringProperty(required=True)
  date_added = db.DateTimeProperty(auto_now_add=True) 

  @classmethod
  def create_project(cls, pj):
    return cls(parent = projects_key(),
               project = pj)

  @classmethod
  def remove_project(cls, pj):
    project = cls.all()
    project = project.filter('project =', pj).get()
    cls.delete(project)

  @classmethod
  def put_project(cls, project):
    logging.warning("putting %s into the datastore" % project)
    project.put()

  @classmethod
  def get_projects(cls):
    logging.warning("getting projects from the datastore")
    projects = cls.all()
    projects = projects.order('date_added').run()
    return projects

def specialusers_key(group='default'):
  return db.Key.from_path('SpecialUsers', group)

class SpecialUsers(db.Model): ## datamodel for Team Pulse - Projects Model

  user_name = db.StringProperty(required=True)
  table_access = db.BooleanProperty(required=True)
  admin_access = db.BooleanProperty(required=True)
  date_added = db.DateTimeProperty(auto_now_add=True) 

  @classmethod
  def create_user(cls, us):
    return cls(parent = specialusers_key(),
               user_name = us,
               table_access = False,
               admin_access = False)

  @classmethod
  def put_user(cls, user):
    user.put()

  @classmethod
  def get_users(cls):
    users = cls.all()
    users = users.order('date_added').run()
    return users

  @classmethod
  def remove_user(cls, us):
    user = cls.all()
    user = user.filter('user_name =', us).get()
    cls.delete(user)

  @classmethod
  def flip_table_access(cls, us):
    user = cls.all()
    user = user.filter('user_name =', us).get()
    access = user.table_access
    if access is True:
      user.table_access = False
    if access is False:
      user.table_access = True
    cls.put_user(user)
    
  @classmethod
  def flip_admin_access(cls, us):
    user = cls.all()
    user = user.filter('user_name =', us).get()
    access = user.admin_access
    if access is True:
      user.admin_access = False
      user.table_access = False
    if access is False:
      user.admin_access = True
      user.table_access = True
    cls.put_user(user)
