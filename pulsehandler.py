import json
## standard python library imports
import webapp2, jinja2, os, logging
from datetime import datetime

## app engine library imports
from google.appengine.api import memcache
from google.appengine.api import users

## pulse class/object imports
from utility import *
from datamodel import *
from importatom import *

path = os.path.dirname(__file__)
templates = os.path.join(path, 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates), autoescape=True) 
last_page = '/' ## initialize last_page to wiki front


class Handler(webapp2.RequestHandler): ## Pulse RequestHandler class: parent of all other request handlers

  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **b):
    template = jinja_env.get_template(template)
    return template.render(**b)
 
  def render(self, template, **kw):
    self.write(self.render_str(template, **kw))

  def set_user_cookie(self, val):
    name = 'user_id'
    cookie_val = make_secure_val(val)
    self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))
 
  def read_user_cookie(self):
    name = 'user_id'
    cookie_val = self.request.cookies.get(name)
    return cookie_val and check_secure_val(cookie_val) 

  def login(self, user): ## sets the user_id cookie by calling set_user_cookie()
    user_id = str(user.key().id()) 
    self.set_user_cookie(user_id)
    set_user_cache(user_id, user)

  def logout(self, user):
    self.response.delete_cookie('user_id')
    self.response.delete_cookie('dev_appserver_login')

  params = {} ## params contains key value pairs used by jinja2 templates
    
  def initialize(self, *a, **kw):

    webapp2.RequestHandler.initialize(self, *a, **kw)

    self.user = users.get_current_user()
    if not self.user: # or self.user is None:
      request_uri = self.request.uri 
      login_url = users.create_login_url()
      self.redirect(login_url)

    if self.request.url.endswith('.json'):
      self.format = 'json'
    else:
      self.format = 'html'


class Home(Handler): ## Handler for Home page requests

  def get(self):

    self.params['user'] = self.user
    self.render('home.html', **self.params)


class Tables(Handler): ## Handler for all Tables requests

  def get(self, project):

    self.params['user'] = self.user

    project = project.replace('-',' ')
    scores = Scores.get_by_project(project)
    scores = list(scores)
    self.params['scores'] = scores

    self.render('tables.html', **self.params)


class Visuals(Handler): ## Handler for all Visuals requests

  def get(self, project):

    self.params['user'] = self.user

    project = project.replace('-',' ')
    scores = Scores.get_by_project(project)

    json_object, columns = list(), [{"id": "date", "label": "Date", "type": "date"}, {"id": "pulse", "label": "Pulse", "type": "number"}] 
    json_object.extend(columns)
    for score in scores:
      time_stamp = format_datetime(score.timestamp)
      row = {"c":[{"v": time_stamp}, {"v": score.pulse}]}
      json_object.append(row) # I should try creating seperate objects for col and row

    json_object = json.dumps(json_object)
    logging.warning(json_object)
    self.params['json'] = json_object
    self.params['scores'] = scores

    self.render('chart_test.html', **self.params)


class Picks(Handler): ## Handler for all Picks requests

  def get(self):

    self.params['user'] = self.user
    self.render('picks.html', **self.params)

  def post(self): ## posting to Picks redirects the user to surveys

    projects = self.request.POST.getall('projects')

    join_char = '&project='
    projects_url = '/survey?project='
    projects_url += join_char.join(projects)

    self.redirect(projects_url)


class Survey(Handler): ## Handler for Survey page requests

  def get(self):

    self.params['user'] = self.user
    projects = self.request.GET.getall('project')
    self.params['projects'] = projects 
    self.params['have_error'] = False 

    self.render('surveys.html', **self.params)

  def post(self):

    un, pj, fb = str(self.user), self.request.POST.getall('project'), self.request.POST.getall('feedback') 

    self.params['fbs'] = fb

    pr, cm = self.request.POST.getall('pride'), self.request.POST.getall('communication') 
    ex, ch = self.request.POST.getall('expectations'), self.request.POST.getall('challenge') 

    self.params['prs'], self.params['cms'], self.params['exs'], self.params['chs'] = pr, cm, ex, ch

    have_error = False 
    self.params['pulse_error'] = [] 

    if validate_all_projects(pj):
      have_error = True
      self.params['pulse_error'].append('One of the projects you selected is invalid') 

    if not validate_all_scores(pr, cm, ex, ch):
      have_error=True
      self.params['pulse_error'].append('One of the scores you selected is invalid')

    self.params['have_error'] = have_error
    logging.warning(have_error)

    if have_error is True:
      self.render("surveys.html", **self.params)

    else: ## if all form inputs are valid then put the scores into Google DataStore

      scores = [ Scores.create_score(un, pj[i], int(pr[i]), int(cm[i]), int(ex[i]), int(ch[i]), fb[i]) for i in range(0, len(pj)) ]
      Scores.put_scores(scores)

      self.redirect('/survey')


class Import(Handler): ## Class that handles import page

  def get(self):
    
    self.render('import.html')

  def post(self):

    feed = self.request.get('feed') or 'cells'
    sskey = self.request.get('sskey') or '0AocOg3jXOHrbdDkzWm9KSVB2TzBZcmphX21QZ2owRVE'
    worksheet = self.request.get('worksheet') or 'od6'

    scores = get_scores_from_atom(feed, sskey, worksheet) 

    Scores.put_scores(scores)
    self.redirect('/import')


class Chart(Handler):

  def get(self):

    self.render('chart.html')


class AdminDrops(Handler): ## Class that handles requests for the drops tables admin page

  def get(self):

    self.render('drops.html')

  def post(self):

    Scores.drop_table()
    self.redirect('/admin/drops') 

class Login(Handler): ## Class that handles user login requests
  
  def get(self):

    self.render('/login-form.html')
 
  def post(self):

    username = self.request.get('username')
    password = self.request.get('password')


class Logout(Handler): ## Class that handles user login requests

  def get(self):

    self.logout(self.user) ## removes user cookie  


class Signup(Handler): ## Handler for all signup requests

  def get(self):

    self.render('/signup-form.html')

  def post(self): ## user signup process: tests against regex and then if username is in datastore 

    self.username = self.request.get('username')
    self.password = self.request.get('password')
    self.verify = self.request.get('verify')
    self.email = self.request.get('email')
    have_error = False

    params = dict(username = self.username, email = self.email) 
 
    if not user_validate(self.username):
      have_error = True
      params['error_username'] = 'That username is invalid' 
    elif Users.by_name(self.username):
      have_error = True
      params['error_username'] = 'That username is already taken' 

    if not password_validate(self.password):
      have_error=True
      params['error_password'] = 'That password is invalid'
    elif not password_verify(self.password, self.verify):
      have_error = True
      params['error_verify'] = 'Those passwords do not match'

    if not email_validate(self.email):
      have_error = True
      params['error_email'] = 'That is not a valid email'

    if have_error:
      self.render('/signup-form.html', **params) 

    else:
      new_user = Users.register(self.username, self.password, self.email)
      new_user.put()
      self.login(new_user)
      self.redirect(last_page)


class Error(Handler): ## Default handler for 404 errors

  def get(self):

    global last_page
    self.write("There's been an error... Woops")


## Mickipebia Routing Table 

PROJECT_RE = r'([0-9a-zA-Z_-]+)/?' # regex for handling wiki page requests

app = webapp2.WSGIApplication([(r'/?', Home),
                               (r'/login/?', Login),
                               (r'/logout/?', Logout),
                               (r'/signup/?', Signup),
                               (r'/table/' + PROJECT_RE, Tables),
                               (r'/visual/' + PROJECT_RE, Visuals),
                               (r'/survey/?', Survey),
                               (r'/picks/?', Picks),
                               (r'/import/?', Import),
                               (r'/chart/?', Chart),
                               (r'/admin/drops/?', AdminDrops),
                               (r'/.*', Error)
                               ],
                                debug=True)
