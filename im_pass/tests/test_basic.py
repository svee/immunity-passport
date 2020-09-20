import os
import unittest

from im_pass import app, mail
from flask import url_for 

from werkzeug.datastructures import FileStorage
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
            data=dict(email=email, password=password),
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


    def update_labreport(self,lab_name, lab_city, lab_country, lab_date, lab_testtype, lab_report):
        flabreport = FileStorage(
            stream=open(lab_report, "rb"),
            filename="labreport.pdf",
            content_type="application/pdf",
        )
        return self.app.post(
           '/update',
           data=dict(lab_name=lab_name, lab_city=lab_city, lab_country=lab_country, lab_date=lab_date, lab_testtype=lab_testtype, lab_report=flabreport, submit_button='Submit'),
           content_type="multipart/form-data",
           follow_redirects=True
        )
    def update_user_and_labreport(self,lab_name, lab_city, lab_country, lab_date, lab_testtype, lab_report,username,prof_pic):
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
           data=dict(lab_name=lab_name, lab_city=lab_city, lab_country=lab_country, lab_date=lab_date, lab_testtype=lab_testtype, lab_report=flabreport, username=username, picture=fprofpic,submit_button='Submit'),
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
 
###############
#### tests ####
###############
    def test_001_valid_user_registration(self):
        response = self.register('validuser1@gmail.com', 'validpassword', 'validpassword')
        self.assertEqual(response.status_code, 200)
        #self.assertIn(b'Check your email for activation link', response.data) 

    def test_002_invalid_user_registration_different_passwords(self):
        response = self.register('invalid_user1@gmail.com', 'validpassword', 'nomatchforyou')
        self.assertIn(b'Passwords must match', response.data)

    def test_003_valid_login(self):
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)

    def test_012_print_when_no_record(self):
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        response = self.print_passport()
        self.assertIn(b'Provide user/test data first', response.data)
    
    def test_004_add_profile(self):  # Each test is independent. I have to go through login again.
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        prof_pic = os.path.join("/home/vee/python/impassport/im_pass/tests/assets/profpic1.jpg")
        response = self.add_profile("Jonhy Chang",prof_pic)
        self.assertIn(b'Profile is updated Successfully', response.data)
    
    def test_005_add_profile_again(self):  # Should not be issue. It will take as update automatically
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        prof_pic = os.path.join("/home/vee/python/impassport/im_pass/tests/assets/profpic1.jpg")
        response = self.add_profile("David Boom",prof_pic)
        self.assertIn(b'Profile is updated Successfully', response.data)
        response = self.get_profile()
        self.assertIn(b'David Boom', response.data)

    def test_006_add_update_profile(self):  # Should not be issue. It will take as update automatically
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        response = self.get_profile()
        prof_pic = os.path.join("/home/vee/python/impassport/im_pass/tests/assets/profpic2.jpg")
        response = self.update_profile("Kevin Dan",prof_pic)
        self.assertIn(b'Profile is updated Successfully', response.data)
        response = self.get_profile()
        self.assertIn(b'Kevin Dan', response.data)

    def test_007_add_update_profile(self):  # Update profile should also be able to handle missing field.
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        prof_pic = os.path.join("/home/vee/python/impassport/im_pass/tests/assets/profpic2.jpg")
        response = self.update_profile("Changed Nameonly")
        self.assertIn(b'Profile is updated Successfully', response.data)
        response = self.get_profile()
        self.assertIn(b'Changed Nameonly', response.data)

    def test_012_print_when_only_profile_present(self):
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        response = self.print_passport()
        self.assertIn(b'Provide user/test data first', response.data)

    def test_020_update_report(self):
        response = self.login("validuser1@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        lab_report = os.path.join("/home/vee/python/impassport/im_pass/tests/assets/report1.pdf")
        response = self.update_labreport("Name of lab", "my city", "my country", "2020-10-02", "True", lab_report)
#        self.assertIn('Immunity Passport.png', response.getheader('Content-Disposition'))
        self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')
    
    def test_007_goto_dashboard_vailid(self):
        response = self.dashboard()
        self.assertEqual(response.status_code, 200)

    def test_008_valid_logout(self):
        response = self.logout()
        self.assertEqual(response.status_code, 200)

    def test_021_valid_gets(self):
        response = self.login("validuser1@gmail.com", "validpassword")
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
            '/home',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        response =  self.app.get(
            '/editprofile',
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


    def test_007_goto_dashboard_invalid(self): #Not logged in
        response = self.dashboard()
        self.assertIn(b'Please log in to access this page', response.data)
    
    def test_020_add_user_and_labreport(self):
        response = self.register('validuser2@gmail.com', 'validpassword', 'validpassword')
        self.assertEqual(response.status_code, 200)
        response = self.login("validuser2@gmail.com", "validpassword")
        self.assertEqual(response.status_code, 200)
        lab_report = os.path.join("/home/vee/python/impassport/im_pass/tests/assets/report1.pdf")
        prof_pic = os.path.join("/home/vee/python/impassport/im_pass/tests/assets/profpic2.jpg")
        response = self.update_user_and_labreport("Name of lab", "my city", "my country", "2020-10-02", "True", lab_report,"Brandnew User", prof_pic)
        #self.assertIn('Immunity Passport.png', response.getheader('Content-Disposition'))
        self.assertEqual(response.headers['Content-Disposition'] , 'attachment; filename=immunity_passport.png')

    def test_009_invalid_password_login(self):
        response = self.login("validuser1@gmail.com", "invalidpassword")
        self.assertIn(b'Invalid Credentials', response.data)
        response = self.logout()
        self.assertEqual(response.status_code, 200)

    def test_010_invalid_email_login(self):
        response = self.login("not_a_validuser1@gmail.com", "validpassword")
        self.assertIn(b'Invalid Credentials', response.data)

    def test_011_invalid_logout(self):
        response = self.logout()
        self.assertIn(b'Please log in to access this page', response.data)


    def test_000_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
 
 
if __name__ == "__main__":
    unittest.main()
