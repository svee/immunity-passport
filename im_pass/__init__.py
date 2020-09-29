from flask import Flask
from flask_mail import Mail

#Note that create_app is called by default
# To run this app, use these commands
#$ export FLASK_APP=<directory name where __init__.py is present
#$ export FLASK_ENV= <development/production>
#$ flask run
#def create_app():
#    create and configure the app
app = Flask(__name__, instance_relative_config=True)


app.config.from_pyfile('config.py', silent=True)

mail = Mail(app)

from im_pass import settings
from im_pass import forms
from im_pass import routes

