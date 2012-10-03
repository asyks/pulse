
from utility import *

from google.appengine.ext import db

class Scores(db.Model):

  username = db.StringProperty(required=True)
  project = db.StringProperty(required=True)
  pride = db.IntegerProperty(required=True)
  communication = db.IntegerProperty(required=True)
  expectations = db.IntegerProperty(required=True) 
  challenge = db.IntegerProperty(required=True) 
  feedback = db.TextProperty(required=True) 
  submitted = db.DateTimeProperty(auto_now_add=True) 

  @classmethod
  def create_score(cls, un, pj, pr, cm, ex, ch, fb):
    return cls(username = un,
               project = pj,
               pride = pr,
               communication = cm,
               expectations = ex,
               challenge = ch,
               feedback = fb)

  @classmethod
  def put_score(score):
    score.put()

  @classmethod
  def get_by_project(cls, pj):
    score = cls.all()
    score = score.filter('project =', pj).order('-submitted').get()
    return score

  @classmethod
  def get_by_username(un):
    score = cls.all()
    score = score.filter('username =', un).order('-submitted').get()
    return score
