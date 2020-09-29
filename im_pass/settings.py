import os
from im_pass import app  #From this package. app is created in __init__
# __file__ refers to the file settings.py 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
app.config['APP_STATIC'] = os.path.join(APP_ROOT, 'static')

app.config['MONGODB_SETTINGS'] = {
    'db': 'db_impass',
    'host': 'localhost',
    'port': 27017
}

# Configure how long report s valid for each of the tests (in days)
app.config['REPORT_VALIDITY'] = {
        "CovidTest":3,
        "AntibodyTest":60,
        "Vaccination":180
        }
app.config['UPLOAD_FOLDER'] = os.path.join(APP_ROOT, 'uploads')
