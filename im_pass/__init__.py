import os

from flask import Flask
from flask_mail import Mail

from flask_mongoengine import MongoEngine, Document

from flask_login import LoginManager

#Note that create_app is called by default
# To run this app, use these commands
#$ export FLASK_APP=<directory name where __init__.py is present
#$ export FLASK_ENV= <development/production>
#$ flask run
#def create_app():
#    create and configure the app
app = Flask(__name__, instance_relative_config=True)


app.config.from_pyfile('config.py', silent=True)
app.config.from_pyfile('app_settings.py', silent=True)

# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
app.config['APP_STATIC'] = os.path.join(APP_ROOT, 'static')

db = MongoEngine(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#from im_pass import settings
from im_pass import forms
from im_pass import routes

