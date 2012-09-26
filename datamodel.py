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
