import os
import unittest

from im_pass import app, mail
from flask import url_for 

# __file__ refers to the file settings.py 
TEST_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
TEST_ASSETS = os.path.join(TEST_ROOT, 'assets')

from werkzeug.datastructures import FileStorage
# Warning test is using same database as application. So need to be dropped each time.
# app.config['MONGODB_SETTINGS'] = { 'db': 'db_unittest_im', 'host': 'localhost', 'port': 27017 }

from mongoengine import connect, disconnect

# Register; Login and test all endpoints for get.
class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SERVER_NAME']="127.0.0.1"
        app.config['EMAIL_ACTIVATION_ENABLED']=False
        app.config['SEND_PASS_BY_MAIL']= False
        app.config['LAB_REPORT_NEEDS_APPROVAL']=False
        self.app = app.test_client()

 
        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass

    ########################
    #### helper methods ####
    ########################
     
    def register(self, email, password, confirm):
        return self.app.post(
            '/signup',
            data=dict(email=email, password=password, confirm=confirm),
            follow_redirects=True
        )
     
    def login(self, email, password):
        return self.app.post(
            '/login',
            data=dict(email=email, password=password,submit_button='Submit'),
            follow_redirects=True
        )
     
    def logout(self):
        return self.app.get(
            '/logout',
            follow_redirects=True
        ) 
    def add_profile(self,username,prof_pic):
        fprofpic = FileStorage(
            stream=open(prof_pic, "rb"),
            filename="profpic.jpg",
            content_type="image/jpeg",
        )
        return self.app.post(
            '/addprofile',
            data=dict(username=username, picture=fprofpic),
            content_type="multipart/form-data",
            follow_redirects=True
        )
    def update_profile(self,username=None,prof_pic=None):

        if (prof_pic):
            fprofpic = FileStorage(
                stream=open(prof_pic, "rb"),
                filename="profpic.jpg",
                content_type="image/jpeg",
            )
        else:
            fprofpic=None

        return self.app.post(
            '/updateprofile',
            data=dict(username=username, picture=fprofpic, submit_button='Submit'),
            content_type="multipart/form-data",
            follow_redirects=True
        )


    def update_labreport(self,lab_name, lab_city, lab_country, lab_date, lab_report_type, lab_report):
        flabreport = FileStorage(
            stream=open(lab_report, "rb"),
            filename="labreport.pdf",
            content_type="application/pdf",
        )
        return self.app.post(
           '/update',
           data=dict(lab_name=lab_name, lab_city=lab_city, lab_country=lab_country, lab_date=lab_date, lab_report_type=lab_report_type, lab_report=flabreport, submit_button='Submit'),
           content_type="multipart/form-data",
           follow_redirects=True
        )
    def update_user_and_labreport(self,lab_name, lab_city, lab_country, lab_date, lab_report_type, lab_report,username,prof_pic):
        fprofpic = FileStorage(
           stream=open(prof_pic, "rb"),
           filename="profpic.jpg",
           content_type="image/jpeg",
        )
        flabreport = FileStorage(
            stream=open(lab_report, "rb"),
            filename="labreport.pdf",
            content_type="application/pdf",
        )
        return self.app.post(
           '/getpassport',
           data=dict(lab_name=lab_name, lab_city=lab_city, lab_country=lab_country, lab_date=lab_date, lab_report_type=lab_report_type, lab_report=flabreport, username=username, picture=fprofpic,submit_button='Submit'),
           content_type="multipart/form-data",
           follow_redirects=True
        )

    def get_profile(self):
        return self.app.get(
            '/updateprofile',
            follow_redirects=True
        )
    def print_passport(self):
        return self.app.get(
            '/printpassport',
            follow_redirects=True
        )

    def dashboard(self):
        return self.app.get(
            '/dashboard',
            follow_redirects=True
        )
 
    def activate_valid_user1(self):
        return self.app.get(
             '/__activate?token=InZhbGlkdXNlcjFAbm9tYWlsLmNvbSI.X3MRBw.CZIm_4tKuRzwhmlVSRRLBmSgbtg',
            follow_redirects=True

        )
    def activate_valid_user2(self):
        return self.app.get(
            '/__activate?token=InZhbGlkdXNlcjJAbm9tYWlsLmNvbSI.X27Xvw.qtIJcHLdRlG-GtTh-6BQSVMsMKI',
            follow_redirects=True

        )
    def approve_report_valid_user1(self,index):
        url = '/__approve?token=InZhbGlkdXNlcjFAbm9tYWlsLmNvbSI.X3MUzQ.j4jPiKqv0A87DJPYzxf5ABRsEhE&report_index='+str(index)
        return self.app.get(
                url,
            follow_redirects=True
        )
    def approve_report_valid_user2(self,index):
        url = '/__approve?token=InZhbGlkdXNlcjJAbm9tYWlsLmNvbSI.X3MVRw.QIo6PTOijMc40xncHb9UYZXdhOI&report_index='+str(index)
        return self.app.get(
                url,
            follow_redirects=True
        )
    def verify_valid_user1(self):
        return self.app.get(
            '/__verify?key=gAAAAABfcyM_FrPX4rRXAFIyVtGp6Is-nl_gZ0Po0jj4oQ5I7kR4tBJ2Zgy63UXH0-0Diyk0ZoQ4_xMalleg1DORadA97MWeOnFMp-RsMaWh6-3oa8B2W1c%3D',
            follow_redirects=True
        )
###############
#### tests ####
###############
    def test_000_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    def test_001_valid_user_registration(self):
        response = self.register('validuser1@nomail.com', 'validpassword', 'validpassword')
        self.assertEqual(response.status_code, 200)
        if (app.config['EMAIL_ACTIVATION_ENABLED']==True):
            self.assertIn(b'Check your email for activation link', response.data) 
            response = self.login("validuser1@nomail.com", "validpassword")
            self.assertIn(b"Activate your account by confirming email",response.data)
            response = self.activate_valid_user1()
            self.assertIn(b'Login - Immunity Passport', response.data)
            response = self.login("validuser1@nomail.com", "validpassword")
            self.assertEqual(response.status_code, 200)

    def test_002_valid_login(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)

    def test_003_valid_logout(self):
        response = self.logout()
        self.assertEqual(response.status_code, 200)

    def test_004_valid_gets(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/updateprofile',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/dashboard',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/updateprofile',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/addprofile',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/update',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/getpassport',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    # Access without login; It should throw login screen in response plus flashed message
    def test_005_invalid_gets(self):
        response =  self.app.get(
            '/updateprofile',
            follow_redirects=True
        )
        self.assertIn(b'Login - Immunity Passport', response.data)
        response =  self.app.get(
            '/dashboard',
            follow_redirects=True
        )
        self.assertIn(b'Login - Immunity Passport', response.data)
        response =  self.app.get(
            '/updateprofile',
            follow_redirects=True
        )
        self.assertIn(b'Login - Immunity Passport', response.data)
        response =  self.app.get(
            '/addprofile',
            follow_redirects=True
        )
        self.assertIn(b'Login - Immunity Passport', response.data)
        response =  self.app.get(
            '/update',
            follow_redirects=True
        )
        self.assertIn(b'Login - Immunity Passport', response.data)
        response =  self.app.get(
            '/getpassport',
            follow_redirects=True
        )
        self.assertIn(b'Login - Immunity Passport', response.data)
        response =  self.app.get(
            '/',
            follow_redirects=True
        )
        self.assertIn(b'Home - Immunity Passport', response.data)  #This is the only link which is valid

 
 
if __name__ == "__main__":
    unittest.main()


