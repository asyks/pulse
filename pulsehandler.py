
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
from visualize import *

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

    self.params['user'] = self.user

    if self.request.url.endswith('.json'):
      self.format = 'json'
    else:
      self.format = 'html'


class SpecialHandler(Handler): ## Pulse RequestHandler class: parent of all other request handlers
    
  def initialize(self, *a, **kw):

    webapp2.RequestHandler.initialize(self, *a, **kw)

    self.user = users.get_current_user()
    if not self.user: # or self.user is None:
      request_uri = self.request.uri 
      login_url = users.create_login_url()
      self.redirect(login_url)

    special_users, name_match = list(SpecialUsers.get_users()), False 
    for u in special_users:
      if str(self.user) == str(u.user_name): 
        name_match = True
        
    if not name_match:
      self.redirect('/')
      return

    self.params['user'] = self.user

    if self.request.url.endswith('.json'):
      self.format = 'json'
    else:
      self.format = 'html'


class Home(Handler): ## Handler for Home page requests

  def get(self):

    projects = Projects.get_projects()
    self.params['projects'] = projects

    self.render('home.html', **self.params)


class Table(SpecialHandler): ## Handler for all Tables requests

  def get(self, project):

    project = project.replace('-',' ')
    self.params['project'] = str(project)

    scores = Scores.get_by_project(project, reverse_sort=True)
    self.params['scores'] = list(scores)

    self.render('table.html', **self.params)


class CommentTable(SpecialHandler): ## Handler for all Comment Tables requests

  def get(self, project):

    project = project.replace('-',' ')
    self.params['project'] = str(project)

    scores = Scores.get_by_project(project, reverse_sort=True)
    self.params['scores'] = list(scores)

    self.render('commenttable.html', **self.params)


class UserCommentTable(SpecialHandler): ## Handler for all Comment Tables requests

  def render_page(self, project):

    project = project.replace('-',' ')
    self.params['project'] = project

    scores = Scores.get_by_project(project, reverse_sort=True)
    self.params['scores'] = list(scores)

    self.render('usercommenttable.html', **self.params)

  def get(self, project):

    project = str(project)
    self.render_page(project)

  def post(self, project): ## remove selected score

    score_key = self.request.get('selected-score')
    Scores.remove_score(score_key)

    project = str(project)
    self.render_page(project)
    

class Charts(Handler): ## Handler for all Visuals requests

  def get(self, project):

    project = project.replace('-',' ')
    self.params['project'] = str(project)

    scores = list(Scores.get_by_project(project)) or None

    if scores is None: ## this conditional redirect will need to be replaced before going into production
      self.redirect('/')
      return

    enough_entries, visual_objects = createChartObjects(scores) 

    if not enough_entries: ## this conditional redirect will need to be replaced before going into production
      self.redirect('/')
      return

    else:
      self.params['line_chart_object'] = visual_objects[0]
      self.params['this_week_pulse_gauge_object'] = visual_objects[1]
      self.params['last_week_pulse_gauge_object'] =  visual_objects[2]
      self.params['this_week_breakout_gauge_object'] = visual_objects[3]
      self.params['last_week_breakout_gauge_object'] = visual_objects[4]

    self.render('charts.html', **self.params)

class Summary(Handler):

  def get(self):

    ## get current week and then query scores by that week or the most recent week
    current_week = Scores.get_max_week()
    scores = Scores.get_by_week_num(current_week)
    summary_gauge_object = createSummaryObject(scores)
    self.params['summary_gauge_object'] = summary_gauge_object 
    self.render('summary.html', **self.params)

class Picks(Handler): ## Handler for all Picks requests

  def get(self):

    projects = Projects.get_projects()
    self.params['projects'] = projects

    self.render('picks.html', **self.params)

  def post(self): ## posting to Picks redirects the user to surveys

    projects = self.request.POST.getall('selected-project')

    join_char = '&selected-project='
    projects_url = '/survey/entry-form/?selected-project='
    projects_url += join_char.join(projects)

    self.redirect(projects_url)


class Survey(Handler): ## Handler for Survey page requests

  def get(self):

    projects = Projects.get_projects()
    self.params['projects'] = list(projects)

    selected_projects = self.request.GET.getall('selected-project')
    self.params['selected_projects'] = selected_projects 

    have_error = False 
    self.params['have_error'] = have_error

    self.render('surveys.html', **self.params)

  def post(self):

    projects = Projects.get_projects()
    self.params['projects'] = list(projects)

    selected_projects = self.request.POST.getall('selected-project')
    self.params['selected_projects'] = selected_projects 

    prs, cms = self.request.POST.getall('pride'), self.request.POST.getall('communication') 
    exs, chs = self.request.POST.getall('expectations'), self.request.POST.getall('challenge') 
    fbs = self.request.POST.getall('feedback') 

    prs = [ int(pr) if pr != '' else '' for pr in prs ]
    cms = [ int(cm) if cm != '' else '' for cm in cms ]
    exs = [ int(ex) if ex != '' else '' for ex in exs ]
    chs = [ int(ch) if ch != '' else '' for ch in chs ]

    self.params['prs'], self.params['cms'], self.params['exs'], self.params['chs'] = prs, cms, exs, chs
    self.params['fbs'] = fbs

    have_error = False 
    self.params['pulse_error'] = [] 

    if validate_all_projects(selected_projects):
      have_error = True
      self.params['pulse_error'].append('One of the projects you selected is invalid') 

    if not validate_all_scores(prs, cms, exs, chs):
      have_error=True
      self.params['pulse_error'].append('One of the scores you selected is invalid')

    self.params['have_error'] = have_error

    if have_error is True:
      self.render("surveys.html", **self.params)

    else: ## if all form inputs are valid then put the scores into Google DataStore

      pjs, un = selected_projects, str(self.user)
      scores = [ Scores.create_score(un, pjs[i], prs[i], cms[i], exs[i], chs[i], fbs[i]) for i in range(0, len(pjs)) ]
      Scores.put_scores(scores)

      self.redirect('/')


class AdminConsole(SpecialHandler): ## Class that handles requests of the import import admin page

  def get(self):
    
    self.params['user'] = self.user
    self.render('adminconsole.html', **self.params)


class AdminImport(SpecialHandler): ## Class that handles requests of the import import admin page

  def post(self):

    feed = self.request.get('feed') or 'cells'
    sskey = self.request.get('sskey') or '0AocOg3jXOHrbdEV4WmdaQW9yTnM4d05wQlpGRzlJS0E'
    worksheet = self.request.get('worksheet') or 'od6'

    scores = get_scores_from_atom(feed, sskey, worksheet) 

    Scores.put_scores(scores)
    self.redirect('/admin/console')


class AdminDrops(SpecialHandler): ## Class that handles requests for the drops tables admin page

  def post(self):

    Scores.drop_table()
    self.redirect('/admin/console') 


class AdminProjects(SpecialHandler): ## Class that handles requests for the project admin page

  def render_admin_projects(self, **params):

    self.params = params
    projects = Projects.get_projects()
    self.params['projects'] = projects

    self.render('projects.html', **self.params)
    
  def get(self):
  
    have_error, error = False, None
    self.params['have_error']  = have_error
    self.params['error'] = error

    self.render_admin_projects(**self.params)

  def post(self):

    have_error, error = False, None
    projects = list(Projects.get_projects())
    project = self.request.get('project')

    entry_is_valid = project_entry_validate(project)
    if project is '' or not entry_is_valid:
      have_error, error = True, 'that project name is invalid'
    elif project_exists(project, projects):
      have_error, error = True, 'that project already exists'
    else:
      project = Projects.create_project(project)
      Projects.put_project(project)

    self.params['have_error']  = have_error
    self.params['error'] = error

    self.render_admin_projects(**self.params)


class AdminProjectsRemove(SpecialHandler): ## Class that handles project remove reqests

  def post(self):

    project = self.request.get('project')
    project = Projects.remove_project(project)

    self.redirect('/admin/projects')


class Logout(Handler): ## Class that handles user login requests

  def get(self):

    self.logout(self.user) ## removes user cookie  


class AdminUsers(SpecialHandler): ## Class that handles requests for the project admin page

  def render_page(self, **params):

    self.params = params
    users = SpecialUsers.get_users()
    self.params['users'] = users

    self.render('users.html', **self.params)
    
  def get(self):
  
    have_error, error = False, None
    self.params['have_error']  = have_error
    self.params['error'] = error

    self.render_page(**self.params)

  def post(self):

    have_error, error = False, None
    users = list(SpecialUsers.get_users())
    user = self.request.get('user')

    if not email_validate(user):
      have_error, error = True, 'that user is invalid'
    elif user_exists(user, users):
      have_error, error = True, 'that user already exists'
    else:
      user = SpecialUsers.create_user(user)
      SpecialUsers.put_user(user)

    self.params['have_error']  = have_error
    self.params['error'] = error

    self.render_page(**self.params)


class AdminUsersModify(SpecialHandler): ## Class that handles project remove reqests

  def post(self):

    user = self.request.get('user')
    remove = self.request.get('remove')
    table_access = self.request.get('table-access')
    admin_access = self.request.get('admin-access')
    
    if not user:
      self.redirect('/admin/users')
      return

    if remove:
      SpecialUsers.remove_user(user)
    if table_access and not remove:
      SpecialUsers.flip_table_access(user)
    if admin_access and not remove:
      SpecialUsers.flip_admin_access(user)

    self.redirect('/admin/users')


class Error(Handler): ## Default handler for 404 errors

  def get(self):

    global last_page
    self.write("There's been an error... Woops")


## Mickipebia Routing Table 

PROJECT_RE = r'([0-9a-zA-Z_-]+)/?' # regex for handling wiki page requests

app = webapp2.WSGIApplication([(r'/?', Home),
                               (r'/logout/?', Logout),
                               (r'/visuals/charts/' + PROJECT_RE, Charts),
                               (r'/visuals/summary/?', Summary ),
                               (r'/survey/project-select/?', Picks),
                               (r'/survey/entry-form/?', Survey),
                               (r'/scores/table/' + PROJECT_RE, Table),
                               (r'/scores/table/comments/' + PROJECT_RE, CommentTable),
                               (r'/scores/table/comments/users/' + PROJECT_RE, UserCommentTable),
                               (r'/admin/console/?', AdminConsole),
                               (r'/admin/import/?', AdminImport),
                               (r'/admin/drop/?', AdminDrops),
                               (r'/admin/projects/?', AdminProjects),
                               (r'/admin/projects/remove/?', AdminProjectsRemove),
                               (r'/admin/users/?', AdminUsers),
                               (r'/admin/users/modify/?', AdminUsersModify),
                               (r'/.*', Error)
                               ],
                                debug=True)
