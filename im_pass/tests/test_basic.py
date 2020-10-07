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
        app.config['EMAIL_ACTIVATION_ENABLED']=True
        app.config['SEND_PASS_BY_MAIL']= True
        app.config['LAB_REPORT_NEEDS_APPROVAL']=True
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
            data=dict(email=email, password=password, submit_button='Submit'),
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
    def test_001_valid_user_registration(self):
        response = self.register('validuser1@nomail.com', 'validpassword', 'validpassword')
        self.assertEqual(response.status_code, 200)
        if (app.config['EMAIL_ACTIVATION_ENABLED']==True):
            #self.assertIn(b'Check your email for activation link', response.data) 
            self.assertIn(b'Please sign in', response.data) 
            response = self.login("validuser1@nomail.com", "validpassword")
            self.assertIn(b"Activate your account by confirming email",response.data)
            response = self.activate_valid_user1()
            self.assertIn(b'Login - Immunity Passport', response.data)
            response = self.login("validuser1@nomail.com", "validpassword")
            self.assertEqual(response.status_code, 200)

    def test_002_invalid_user_registration_different_passwords(self):
        response = self.register('invalid_user1@nomail.com', 'validpassword', 'nomatchforyou')
        self.assertIn(b'Passwords must match', response.data)

    def test_003_valid_login(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)

    def test_004_print_when_no_record(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        response = self.print_passport()
        self.assertIn(b'Provide user/test data first', response.data)
    
    def test_005_add_profile(self):  # Each test is independent. I have to go through login again.
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        prof_pic = os.path.join(TEST_ASSETS,"profpic1.jpg")
        response = self.add_profile("Jonhy Chang",prof_pic)
        self.assertIn(b'Profile is updated Successfully', response.data)
    
    def test_006_add_profile_again(self):  # Should not be issue. It will take as update automatically
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        prof_pic = os.path.join(TEST_ASSETS,"profpic1.jpg")
        response = self.add_profile("David Boom",prof_pic)
        self.assertIn(b'Profile is updated Successfully', response.data)
        response = self.get_profile()
        self.assertIn(b'David Boom', response.data)

    def test_007_add_update_profile(self):  # Should not be issue. It will take as update automatically
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        response = self.get_profile()
        prof_pic = os.path.join(TEST_ASSETS,"profpic2.jpg")
        response = self.update_profile("Kevin Dan",prof_pic)
        self.assertIn(b'Profile is updated Successfully', response.data)
        response = self.get_profile()
        self.assertIn(b'Kevin Dan', response.data)

    def test_008_add_update_profile(self):  # Update profile should also be able to handle missing field.
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        prof_pic = os.path.join(TEST_ASSETS,"profpic2.jpg")
        response = self.update_profile("Changed Nameonly")
        self.assertIn(b'Profile is updated Successfully', response.data)
        response = self.get_profile()
        self.assertIn(b'Changed Nameonly', response.data)

    def test_009_print_when_only_profile_present(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        response = self.print_passport()
        self.assertIn(b'Provide user/test data first', response.data)

    def test_010_update_report(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        lab_report = os.path.join(TEST_ASSETS,"report1.pdf")
        response = self.update_labreport("Name of lab", "my city", "IND", "2020-09-02", "Vaccination", lab_report)
        if(app.config['LAB_REPORT_NEEDS_APPROVAL'] == True):
            self.assertIn(b'Report is sent for approval. Download once it is done',response.data)
            response = self.approve_report_valid_user1(0)
            self.assertIn(b'You have approved the Report. Thank you!',response.data)
            response = self.approve_report_valid_user1(0)  #Try again
            self.assertIn(b'Report is already approved; Thank you',response.data)
            response = self.print_passport()
            self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')
        else:
            self.assertIn(b"Report Updated. Click on Download to get the Pass",response.data)
            response = self.print_passport()
            self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')
    
    def test_011_goto_dashboard_vailid(self):
        response = self.dashboard()
        self.assertEqual(response.status_code, 200)

    def test_012_valid_logout(self):
        response = self.logout()
        self.assertEqual(response.status_code, 200)

    def test_013_valid_gets(self):
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


    def test_014_goto_dashboard_invalid(self): #Not logged in
        response = self.dashboard()
        self.assertIn(b'Please log in to access this page', response.data)
    
    def test_015_add_user_and_labreport(self):
        response = self.register('validuser2@nomail.com', 'validpassword', 'validpassword')
        self.assertEqual(response.status_code, 200)
        if (app.config['EMAIL_ACTIVATION_ENABLED']==True):
            self.assertIn(b'Check your email for activation link', response.data) 
            response = self.activate_valid_user2()
            self.assertIn(b'Login - Immunity Passport', response.data)
        response = self.login("validuser2@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        lab_report = os.path.join(TEST_ASSETS,"report1.pdf")
        prof_pic = os.path.join(TEST_ASSETS,"profpic2.jpg")
        response = self.update_user_and_labreport("Name of lab", "my city", "IND", "2020-09-02", "Vaccination", lab_report,"Brandnew User", prof_pic)
        if(app.config['LAB_REPORT_NEEDS_APPROVAL'] == True):
            self.assertIn(b'Report is sent for approval. Download once it is done',response.data)
            response = self.approve_report_valid_user2(0)
            self.assertIn(b'You have approved the Report. Thank you!',response.data)
            response = self.print_passport()
            self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')
        else:
            self.assertIn(b"Report Updated. Click on Download to get the Pass",response.data)
            response = self.print_passport()
            self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')

    def test_016_invalid_password_login(self):
        response = self.login("validuser1@nomail.com", "invalidpassword")
        self.assertIn(b'Invalid Credentials', response.data)
        response = self.logout()
        self.assertEqual(response.status_code, 200)

    def test_017_invalid_email_login(self):
        response = self.login("not_a_validuser1@nomail.com", "validpassword")
        self.assertIn(b'Invalid Credentials', response.data)

    def test_018_invalid_logout(self):
        response = self.logout()
        self.assertIn(b'Please log in to access this page', response.data)

    def test_019_verify_report_expired(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        lab_report = os.path.join(TEST_ASSETS,"report1.pdf")
        response = self.update_labreport("Name of lab", "my city", "IND", "2018-09-02", "Antibody Test", lab_report) #old; this should expire
        if(app.config['LAB_REPORT_NEEDS_APPROVAL'] == True):
            self.assertIn(b'Report is sent for approval. Download once it is done',response.data)
            response = self.approve_report_valid_user1(1)
            self.assertIn(b'You have approved the Report. Thank you!',response.data)
            response = self.print_passport()
            self.assertIn (b'Your Report has expired; submit new lab report',response.data)
        else:
            self.assertIn(b"Report Updated. Click on Download to get the Pass",response.data)
            response = self.print_passport()
            self.assertIn (b'Your Report has expired; submit new lab report',response.data)
        response = self.verify_valid_user1()
        self.assertIn(b'FAILURE', response.data)

    def test_020_verify_report_valid(self):
        response = self.login("validuser1@nomail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        lab_report = os.path.join(TEST_ASSETS,"report1.pdf")
        response = self.update_labreport("Name of lab", "my city", "IND", "2020-09-02", "Vaccination", lab_report) #old; this should expire
        if(app.config['LAB_REPORT_NEEDS_APPROVAL'] == True):
            self.assertIn(b'Report is sent for approval. Download once it is done',response.data)
            response = self.approve_report_valid_user1(2)
            self.assertIn(b'You have approved the Report. Thank you!',response.data)
            response = self.print_passport()
            self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')
        else:
            self.assertIn(b"Report Updated. Click on Download to get the Pass",response.data)
            response = self.print_passport()
            self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')
        response = self.verify_valid_user1()
        self.assertIn(b'SUCCESS', response.data)


    def test_000_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 
 
if __name__ == "__main__":
    unittest.main()


