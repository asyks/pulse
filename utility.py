
## standard python library imports
import hashlib, hmac, string, random, re, logging
## pulse class/object imports
from datetime import datetime

## date format and string substitution procedures
def format_datetime(date_time):
  time_format = '%x' 
  return date_time.strftime(time_format)

def make_last_edit_str(time):
  return 'This page was last edited on: %s' % time
 
## datastore entry validation stuff
PROJECT_RE = re.compile(r'([0-9a-zA-Z_-]+)/?')
def validate_all_projects(projects):
  for project in projects:
    return project_validate(str(project))

def project_validate(project):
  if not PROJECT_RE.match(project):
    return False

def project_entry_validate(project):
  if PROJECT_RE.match(project):
    return True
  else:
    return False

def project_exists(project, projects):
  for p in projects:
    if str(project) == str(p.project):
      return True

def user_exists(user, users):
  for u in users:
    if str(user) == str(u.user_name):
      return True

def validate_all_scores(pr, cm, ex, ch):
  return score_validate(pr) and score_validate(cm) and score_validate(ex) and score_validate(ch) 

def score_validate(scores): 
  for score in scores:
    if not score or score not in range(1,11):
      return False
  return True 

## sign-up form validation stuff
USER_RE = re.compile("^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")
def user_validate(u):
  if USER_RE.match(u):
    return True

def password_validate(p):
  if PASS_RE.match(p):
    return True

def password_verify(p,v):
  if p == v:
    return True

def email_validate(e): 
  if not e:
    return True
  if e and EMAIL_RE.match(e):
    return True

## cookie setting stuff
secret = 'you will never guess me'
def make_secure_val(val):
  return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
  val = secure_val.split('|')[0]
  if secure_val == make_secure_val(val):
    return val 

## password hashing stuff
def make_salt():
  return ''.join(random.choice(string.letters) for x in range(5))

def make_hash(un, pw, salt=None):
  if not salt:
    salt = make_salt()
  h = hashlib.sha256(un + pw + salt).hexdigest()
  return '%s|%s' % (salt, h)

def check_hash(un, pw, h):
  salt = h.split('|')[0]
  if h == make_hash(un, pw, salt):
    return True
