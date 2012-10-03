
## standard python library imports and app engine library imports
import webapp2
import jinja2
import os 
import logging

## wiki - Mickipebia class/object imports
from utility import *
from datamodel import *
#from wikimemcache import *

## app engine library memcache import
from google.appengine.api import memcache
from google.appengine.api import users

path = os.path.dirname(__file__)
templates = os.path.join(path, 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(templates), autoescape=True) 
last_page = '/' ## initialize last_page to wiki front


## Main RequestHandler class: parent of all other request handlers

class Handler(webapp2.RequestHandler):

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
    return cookie_val and check_secure_val(cookie_val) ## return a and b: if a then return b 

  def login(self, user): ## sets the user_id cookie by calling set_user_cookie()
    user_id = str(user.key().id()) 
    self.set_user_cookie(user_id)
    set_user_cache(user_id, user)

  def logout(self, user):
#    if user:
#      user_id = str(user.key().id())
#      memcache.delete(user_id)
    self.response.delete_cookie('user_id')
    self.response.delete_cookie('dev_appserver_login')

  def get_wiki_page(self, title, version=None):
    if not version:
      wiki = Wiki.by_title(title)
    elif version:
      wiki = Wiki.by_title_and_version(title, int(version)) 
    logging.error('self.get_wiki_page - wiki: %s' % wiki)
    return wiki
 
  params = {} ## params contains key value pairs used by jinja2 templates to render all html

  def make_logged_out_header(self, page):
    history_link = '/_history' + page 
    self.params['history'] = '<a href ="%s">history</a>' % history_link
    self.params['auth'] = '<a href="/login"> login </a>|<a href="/signup"> signup </a>'

  def make_logged_in_header(self, page, user, version=None):
    history_link = '/_history' + page 
    if version:
      self.params['edit'] = '<a href="/_edit%s?v=%s">edit</a>' % (page, version)
    else:
      self.params['edit'] = '<a href="/_edit%s">edit</a>' % page
    self.params['history'] = '<a href ="%s">history</a>' % history_link
    self.params['auth'] = user.username + '(<a href="/logout"> logout </a>)' 
    
  def initialize(self, *a, **kw):
    webapp2.RequestHandler.initialize(self, *a, **kw)
#    user_id, self.user = self.read_user_cookie(), None 
#    if user_id: ## user_id is the value of the user_id cookie
#      user, last_login = get_user_cache(str(user_id))
#      if user: ## if user is cached we don't need to query Users Object
#        self.user = user 
#      else: ## if user isn't cached we will need to query Users Object
#        self.user = Users.by_id(int(user_id)) 

    self.user = users.get_current_user()
    if not self.user:
      self.redirect(users.create_login_url(self.request.uri))

    if self.request.url.endswith('.json'):
      self.format = 'json'
    else:
      self.format = 'html'


## Handler for all VisPage requests

class VisPage(Handler):

  def get(self):
    self.write("VisPage Handler is working <br>")
    self.write(self.user)

class Survey(Handler):

  def get(self):
#    self.write("Survey Handler is working")
    self.params['user'] = self.user
    self.render('survey.html', **self.params)


## Class that handles user login requests

class Login(Handler):
  
  def get(self):

    self.render('/login-form.html')
 
  def post(self):

    username = self.request.get('username')
    password = self.request.get('password')

#    user = Users.login(username, password)

#    if user:
#      self.login(user) ## sets user cookie 
#      self.redirect(last_page)

#    else:
#      self.render('/login-form.html', error='invalid username or password')


## Class that handles user login requests

class Logout(Handler):

  def get(self):

    self.logout(self.user) ## removes user cookie  
#    self.redirect(last_page)


## Handler for all signup requests

class Signup(Handler):

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


## Default handler for 404 errors

class Error(Handler):

  def get(self):

    global last_page
    self.write("There's been an error... Woops")


## Mickipebia Routing Table 

PAGE_RE = r'/(?:[a-zA-Z0-9_-]+/?)*' # regex for handling wiki page requests

app = webapp2.WSGIApplication([(r'/login/?', Login),
                               (r'/logout/?', Logout),
                               (r'/signup/?', Signup),
                               (r'/visual/?' + PAGE_RE, VisPage),
                               (r'/survey/?', Survey),
                               (r'/.*', Error)
                               ],
                                debug=True)