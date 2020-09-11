from flask import Flask


#Note that create_app is called by default
# To run this app, use these commands
#$ export FLASK_APP=<directory name where __init__.py is present
#$ export FLASK_ENV= <development/production>
#$ flask run
#def create_app():
#    create and configure the app
app = Flask(__name__, instance_relative_config=True)

#class Config(object):
#    SECRET_KEY = "eYv1IUmovJMkw6CQ8K3C0mF8Z"
#app.config.from_object(Config)

app.config.from_pyfile('config.py', silent=True)


from im_pass import forms
from im_pass import routes




#return app

