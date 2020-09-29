
# .....
# main routing module with functions for signup, login and other functions
#

from flask import render_template,redirect, url_for, request, flash,  send_file

from im_pass import app  #From this package. app is created in __init__
from im_pass import forms #Notice forms.SignupForm, etc...  way to access object in other file. 
from im_pass import settings 
from im_pass import enc_msg
from im_pass import gen_pass 



from flask_mongoengine import MongoEngine, Document
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from mongoengine import *
from wtforms import StringField, PasswordField, FileField
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


from datetime import datetime, timedelta

from flask import jsonify
import base64


db = MongoEngine(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class Report(db.EmbeddedDocument):
    lab_name = db.StringField()
    lab_city = db.StringField()
    lab_country = db.StringField()
    lab_date = db.DateField()
    lab_report_type = db.StringField()
    lab_report = db.FileField()
    approved = db.BooleanField(default=False)   #Used for email approval of the report

class User(UserMixin, db.Document):
    meta = {'collection': 'PassHolders'}   #Mongodb collection name is defined here
    email = db.StringField(max_length=30)
    password = db.StringField()
    confirmed = db.BooleanField(default=False)   #Used for email conformation
    name = db.StringField(max_length=30)
    #picture=db.ImageField(size=(160,160,True))   #Limitation Mongoengine does not maintain aspect ratio. So need to use PIL
    picture=db.ImageField() 
    reports = ListField(EmbeddedDocumentField(Report))


@app.errorhandler(413)
def error413(e):
    flash("Size of Picture/Report recommended 1MB; cannot exceed 5MB")
    return render_template('dashboard.html')

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.objects(pk=user_id).first()
    except Exception as e:
        flash ("Critical Error connecton to MongoDB Failed:") 
        return None

@app.route('/')
def home():
    if (current_user and current_user.is_authenticated == True):
        return redirect(url_for('dashboard'))
    return render_template('home.html')


from im_pass import email

def generate_email_confirmation(email_id):
    #Form email activation link and send
    token = enc_msg.gen_activation_key(email_id)
    confirm_url = url_for('__activate', token=token, _external=True)
    html = render_template('email_activation.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    try:
       email.send_email(email_id, subject, html)  #email integration is not done.
    except Exception as e:
        flash("Error connecting to email server; try again later")
    flash('Check your email for activation link')

def generate_email_report_approval(email_id, fattach, name, lab_name, lab_city, lab_country, lab_date, lab_report_type,report_index):
    token = enc_msg.gen_activation_key(email_id)
    confirm_url = url_for('__approve', token=token, report_index=report_index,_external=True)
    html = render_template('approval_request.html', confirm_url=confirm_url,
                            name=name, lab_name=lab_name, lab_city=lab_city, lab_country=lab_country, 
                            lab_date=lab_date, lab_report_type=lab_report_type)
    subject = "Please review attached report and click on the link to approve"
    try:
       email.send_email(app.config['APPROVER_EMAIL'], subject, html,fattach, "report.pdf","pdf")  #email integration is not done.
    except Exception as e:
        flash("Error connecting to email server; try again later")
        return
    flash('Report is sent for approval. Download once it is done')

# Once the report is approved, this is called to send immunity pass through e-mail
def generate_email_immunity_pass(email_id, fattach):
    html = render_template('passportby_mail.html')
    subject = "Your immunity pass is approved"
    try:
        email.send_email(email_id, subject, html,fattach,"immunity_passport.png", "png")  #email integration is not done.
    except Exception as e:
        return   #Silent here as user can later download always.


def is_date_later_than_today(input_date):
    today = datetime.today().date()
    if (input_date > today):
        return True
    return False

# Checks if the lab report in hand has expired
def check_if_expired(rep_type, rep_date):
    today = datetime.today().date()
    expired=False
    if rep_type == "Covid- Real Time PCR":
        if (rep_date + timedelta(days=app.config['REPORT_VALIDITY']['CovidTest']) < today):
                expired = True;
    elif rep_type == "Antibody Test":
        if (rep_date + timedelta(days=app.config['REPORT_VALIDITY']['AntibodyTest']) < today):
                expired = True;
    elif rep_type == "Vaccination":
        if (rep_date + timedelta(days=app.config['REPORT_VALIDITY']['Vaccination']) < today):
                expired = True;
    else:
        expired = True # Error we don't understand this type of test.
    return expired

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated == True:
        flash('Logout before registering another user')
        return redirect(url_for('dashboard'))
    form = forms.SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            existing_user = User.objects(email=form.email.data.lower()).first()
        except Exception as e:
            flash(e)   #Likely that MongoDB connection has failed.
            return render_template('home.html')

        if existing_user is None:
            hashpass = generate_password_hash(form.password.data, method='sha256')
            newuser = User(email=form.email.data.lower(),password=hashpass).save()

            if(app.config['EMAIL_ACTIVATION_ENABLED'] == True):
                generate_email_confirmation(form.email.data.lower())
                return redirect(url_for('login'))
            else:
                newuser.confirmed = True  # temporary till email activation is enabled.
                newuser.save()
                flash('Registered Successfully; Log in with email/password')
        else:
            flash('You have already registered; Log in with email/password')
        return redirect(url_for('login'))
    else:
        return render_template('signup.html', title = 'Sing up with your email ID', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('dashboard'))
    form = forms.LoginForm()
    if request.method == 'POST' and form.validate():
        print(form.email.data)
        print(form.password.data)
        try:
            user_rec = User.objects(email=form.email.data.lower()).first()
        except Exception as e:
            flash(e)   #Likely that MongoDB connection has failed.
            return render_template('home.html')

        if user_rec:
            if check_password_hash(user_rec['password'], form.password.data):
                if (user_rec.confirmed == False):
                    flash("Activate your account by confirming email") 
                    generate_email_confirmation(form.email.data.lower()) #Need better way to provide resend confirm
                    return redirect(url_for('home'))
                else:
                    login_user(user_rec)
                    return redirect(url_for('dashboard'))
        flash('Invalid Credentials; Try again')
        return redirect(url_for('login'))
    else:
        return render_template('login.html', title='Sign In', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
   if (current_user.name == None or current_user.picture == None or len(current_user.reports) == 0):
      return render_template('dashboard.html', name=current_user.email, pass_ready=False)
   else:
      return render_template('dashboard.html', name=current_user.email, pass_ready=True)


@app.route('/getpassport', methods=['GET', 'POST'])
@login_required
def getpassport():
    if request.method == 'POST' and request.form['submit_button'] == 'Home':
        return redirect(url_for('dashboard'))
    form = forms.GetPassportForm()
    if request.method == 'POST' and form.validate() and  request.form['submit_button'] == 'Submit':
        if (is_date_later_than_today(form.lab_date.data)):
            flash("Report Date cannot be later than today")
            return render_template('getpassport.html', title = 'Immunity Passport Request', form=form)

        rep = Report(lab_name=form.lab_name.data, lab_city=form.lab_city.data, 
            lab_country=form.lab_country.data,lab_date=form.lab_date.data, lab_report_type=form.lab_report_type.data)

        f = form.lab_report.data
        filename = secure_filename(f.filename)
        try:
            rep.lab_report.put(f) 
            current_user.reports.append(rep)  #Should there be limit on number of submissions ?

            current_user.name = form.username.data
            pf = form.picture.data
            filename = secure_filename(pf.filename) #May be I can make the file names to be legit or safer this way.
            gen_pass.optimize_image(pf)
            if(current_user.picture == None):  #First time updating
                current_user.picture.put(pf) 
            else:
                current_user.picture.replace(pf) 

            current_user.save()
        except Exception as e:
            flash(e.message)
            return render_template('getpassport.html', title = 'Immunity Passport Request', form=form)

        if (app.config['LAB_REPORT_NEEDS_APPROVAL'] == True):
            tempFileObj = gen_pass.generate_temp_report(current_user)
            rep = current_user.reports[-1]
            report_index = len(current_user.reports)-1
            generate_email_report_approval(current_user.email, tempFileObj, current_user.name, 
                    rep.lab_name, rep.lab_city, rep.lab_country, rep.lab_date, rep.lab_report_type,report_index)
            return redirect(url_for('dashboard'))
        else:
            auth_url = url_for("__verify",_external=True, key=enc_msg.encrypt_msg(current_user.email)) #Need to encrypt
            tempFileObj = gen_pass.generate_idcard(current_user,auth_url)
            current_user.reports[-1].approved = True
            current_user.save()
            response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
        return response

    elif (current_user.name != None):  #User information already present; just ask for test/vaccination details 
        return redirect(url_for('update'))
    else:
        return render_template('getpassport.html', title = 'Immunity Passport Request', form=form)

@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    if request.method == 'POST' and request.form['submit_button'] == 'Home':
        return redirect(url_for('dashboard'))
    form = forms.UpdateCovidTestForm()
    if request.method == 'POST' and form.validate():
        if (is_date_later_than_today(form.lab_date.data)):
            flash("Report Date cannot be later than today")
            return render_template('update.html', title = 'Immunity Passport Request', form=form)
#        elif (len(current_user.reports) and current_user.reports[-1].approved == False):
#            flash ('Current report is waiting for approval. Try again later','success')
#            return render_template('update.html', title = 'Immunity Passport Request', form=form)

        rep = Report(lab_name=form.lab_name.data, lab_city=form.lab_city.data, 
            lab_country=form.lab_country.data,lab_date=form.lab_date.data, lab_report_type=form.lab_report_type.data)

        try:
            f = form.lab_report.data
            filename = secure_filename(f.filename)
    
            rep.lab_report.put(f) 
    
            current_user.reports.append(rep)  #Should there be limit on number of submissions ?
            current_user.save()
        except Exception as e:
            flash(e.message)
            return render_template('update.html', title = 'Immunity Passport Request', form=form)

        if (app.config['LAB_REPORT_NEEDS_APPROVAL'] == True):
            tempFileObj = gen_pass.generate_temp_report(current_user)
            rep = current_user.reports[-1]
            report_index = len(current_user.reports)-1
            generate_email_report_approval(current_user.email, tempFileObj, current_user.name, 
                    rep.lab_name, rep.lab_city, rep.lab_country, rep.lab_date, rep.lab_report_type,report_index)
            return redirect(url_for('dashboard'))
        else:
            auth_url = url_for("__verify",_external=True, key=enc_msg.encrypt_msg(current_user.email)) #Need to encrypt
            tempFileObj = gen_pass.generate_idcard(current_user,auth_url)
            current_user.reports[-1].approved = True
            current_user.save()
            response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
        return response

    else:
        return render_template('update.html', title = 'Immunity Passport Request', form=form)


def profilepic():
    img = ""
    fs =  current_user.picture.get()
    if (fs != None):
        img = base64.b64encode(fs.read())
        img = img.decode("utf8")
    return img

@app.route('/addprofile', methods=['GET', 'POST'])
@login_required
def addprofile():
    form = forms.AddProfileForm()
    if request.method == 'POST' and form.validate():
        current_user.name = form.username.data

        pf = form.picture.data
        filename = secure_filename(pf.filename)
        gen_pass.optimize_image(pf)

        try:
            if(current_user.picture == None):  #First time updating
                current_user.picture.put(pf) 
            else:
                current_user.picture.replace(pf) 
    
            current_user.save()

        except Exception as e:
            flash(e.message)
            return render_template('addprofile.html', title = 'Edit Profile Data', 
                           email=current_user.email, form=form)
    
        flash('Profile is updated Successfully')
        return redirect(url_for('dashboard'))

    if (current_user.name == None):  #First time update. So we make fields mandatory.
        return render_template('addprofile.html', title = 'Edit Profile Data', 
                           email=current_user.email, form=form)
    else:
        return redirect(url_for('updateprofile'))

@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateprofile():

    if request.method == 'POST' and request.form['submit_button'] == 'Home':
        return redirect(url_for('dashboard'))

    form = forms.UpdateProfileForm()
    if request.method == 'POST' and form.validate():
        if(form.username.data):
            current_user.name = form.username.data

        pf = form.picture.data
        try:
            if (pf):
                filename = secure_filename(pf.filename)
                gen_pass.optimize_image(pf)
                if(current_user.picture == None):  #First time updating
                    current_user.picture.put(pf) 
                else:
                    current_user.picture.replace(pf) 
    
            current_user.save()
        except Exception as e:
            flash(e.message)
            img = None
            fs =  current_user.picture.get()
            if (fs != None):
                img = base64.b64encode(fs.read())
                img = img.decode("utf8")
            return render_template('updateprofile.html', title = 'Edit Profile Data', 
                               profile_pic=img, email=current_user.email, name=current_user.name,form=form)

        if(form.username.data or pf):  #Success message only when there is an update
            flash('Profile is updated Successfully')
        return redirect(url_for('dashboard'))


    if (current_user.name == None):  #First time update. So we make fields mandatory.
        return render_template('addprofile.html', title = 'Edit Profile Data', 
                               email=current_user.email, form=form)
    else:
        img = None
        fs =  current_user.picture.get()
        if (fs != None):
            img = base64.b64encode(fs.read())
            img = img.decode("utf8")
        return render_template('updateprofile.html', title = 'Edit Profile Data', 
                               profile_pic=img, email=current_user.email, name=current_user.name,form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/__verify")
def __verify():
    form = forms.__VerifyForm(request.args, meta={'csrf': False})  #Note passing request.args for GET; csrf explicit declaration need
    if request.method == 'GET' and form.validate():
        key = form.key.data
        emailid = enc_msg.decrypt_msg(key)

        #return jsonify(receivedkey=key, email=emailid.decode('utf8'))  This was for testing only.
        try:
            user_rec = User.objects(email=emailid.decode('utf8')).first()
        except Exception as e:
            return render_template('verify_response.html',"Server Error"+e.message) 
        if user_rec:
            if (check_if_expired(user_rec.reports[-1].lab_report_type,user_rec.reports[-1].lab_date) == True):
                message = 'FAILURE: User has an expired report'
            else:
                message =  'SUCCESS: User has a VALID immunity passport!!'
        else:
            message = 'FAILURE: Authentication FAILED'
        return render_template('verify_response.html',message=message) 

# Route to download the immunity passport. If user or lab records are missing or if lab report is not approved yet,
# just display warning and go back to dashboard.
@app.route('/printpassport', methods=['GET'])
@login_required
def printpassport():
    if (current_user.name == None or current_user.picture == None or len(current_user.reports) == 0):
        flash ('Provide user/test data first using Get New option','success')
    elif (current_user.reports[-1].approved == False):
        flash ('Lab report is waiting for approval. Try again later','success')
    elif (check_if_expired(current_user.reports[-1].lab_report_type,current_user.reports[-1].lab_date) == True):
        flash ('Your Report has expired; submit new lab report','success')
    else:
        auth_url = url_for("__verify",_external=True, key=enc_msg.encrypt_msg(current_user.email)) #Need to encrypt
        tempFileObj = gen_pass.generate_idcard(current_user,auth_url)
        response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
        return response
    return render_template('dashboard.html',pass_ready=True)



@app.route('/__activate')
def __activate():
    form = forms.__ActivateForm(request.args, meta={'csrf': False})  #Note passing request.args for GET; csrf explicit declaration need
    if request.method == 'GET' and form.validate():
        token = form.token.data
    try:
        email = enc_msg.confirm_activation_key(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    if(email):
        user_rec = User.objects(email=email).first()
        if user_rec.confirmed:
            flash('Account confirmed. Please login.', 'success')
        else:
            user_rec.confirmed = True
            user_rec.save()
            flash('You have confirmed your account. Thanks!', 'success')
            return redirect(url_for('login'))
    return render_template('home.html')  #invalid link, expired token... we just return to home page.

@app.route('/__approve')
def __approve():
    form = forms.__ApproveForm(request.args, meta={'csrf': False})  #Note passing request.args for GET; csrf explicit declaration need
    if request.method == 'GET' and form.validate():
        token = form.token.data
        report_index = form.report_index.data
    try:
        email = enc_msg.confirm_activation_key(token)
    except:
        message = 'The confirmation link is invalid or has expired.'
    user_rec = User.objects(email=email).first()
    if (user_rec == None or report_index >= len(user_rec.reports)):
        message = 'The confirmation link is invalid or has expired.'
    if user_rec.reports[report_index].approved == True:
       message = 'Report is already approved; Thank you.'
    else:
        user_rec.reports[report_index].approved = True
        user_rec.save()
        message =  'You have approved the Report. Thank you!'
        if (app.config['SEND_PASS_BY_MAIL'] == True and 
                check_if_expired(user_rec.reports[report_index].lab_report_type,user_rec.reports[report_index].lab_date) == False):

            auth_url = url_for("__verify",_external=True, key=enc_msg.encrypt_msg(user_rec.email)) #Need to encrypt
            tempFileObj = gen_pass.generate_idcard(user_rec,auth_url)
            generate_email_immunity_pass(user_rec.email, tempFileObj)

    return render_template('approval_response.html',message=message) 
