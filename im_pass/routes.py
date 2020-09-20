

from flask import render_template,redirect, url_for, request, flash,  send_file

# .....


from im_pass import app  #From this package. app is created in __init__
from im_pass import forms #Notice forms.SignupForm, etc...  way to access object in other file. 



from flask_mongoengine import MongoEngine, Document
from mongoengine import *
from wtforms import StringField, PasswordField, FileField
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


from PIL import Image, ImageDraw, ImageFilter, ImageFont 
import os.path


from im_pass import settings 
from flask import jsonify

from im_pass import enc_msg

import base64

app.config['MONGODB_SETTINGS'] = {
    'db': 'db_impass',
    'host': 'localhost',
    'port': 27017
}

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

class User(UserMixin, db.Document):
    meta = {'collection': 'PassHolders'}   #Mongodb collection name is defined here
    email = db.StringField(max_length=30)
    password = db.StringField()
    confirmed = db.BooleanField(default=False)   #Used for email conformation
    name = db.StringField(max_length=30)
    picture=db.ImageField(size=(160,160,True))
    reports = ListField(EmbeddedDocumentField(Report))


@app.errorhandler(413)
def error413(e):
    flash("Size of Picture/Report cannot exceed 1MB")
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
    return render_template('home.html')


from im_pass import email

def generate_email_confirmation(email_id):
    #Form email activation link and send
    token = enc_msg.gen_activation_key(email_id)
    confirm_url = url_for('__activate', token=token, _external=True)
    html = render_template('email_activation.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    # email activation is disabled for demo version now. to activate, uncomment generate_email.
    # email.send_email(email_id, subject, html)  #email integration is not done.
    #flash('Check your email for activation link')

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
            generate_email_confirmation(form.email.data.lower())

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
            if(current_user.picture == None):  #First time updating
                current_user.picture.put(pf) 
            else:
                current_user.picture.replace(pf) 

            current_user.save()
        except Exception as e:
            flash(e.message)
            return render_template('getpassport.html', title = 'Immunity Passport Request', form=form)

        tempFileObj = generate_idcard(current_user)
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

        tempFileObj = generate_idcard(current_user)
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

        user_rec = User.objects(email=emailid.decode('utf8')).first()
        if user_rec:
            return 'SUCCESS: User has a VALID immunity passport!!'
    return 'Authentication FAILED'

@app.route('/printpassport', methods=['GET', 'POST'])
@login_required
def printpassport():
    if request.method == 'GET':
        if (current_user.name == None or current_user.picture == None or len(current_user.reports) == 0):
            flash ('Provide user/test data first using Get New option','success')
            return redirect(url_for('dashboard'))
        else:
            tempFileObj = generate_idcard(current_user)
            response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
            return response





@app.route('/__activate')
def __activate():
    form = forms.__ActivateForm(request.args, meta={'csrf': False})  #Note passing request.args for GET; csrf explicit declaration need
    if request.method == 'GET' and form.validate():
        token = form.token.data
    try:
        email = enc_msg.confirm_activation_key(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    user_rec = User.objects(email=email).first()
    if user_rec.confirmed:
        flash('Account confirmed. Please login.', 'success')
    else:
        user_rec.confirmed = True
        user_rec.save()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('login'))


import io
from tempfile import NamedTemporaryFile
from shutil import copyfileobj



def generate_idcard(current_user):

    card = Image.open(os.path.join(settings.APP_STATIC, 'Immunity Passport.png'))
    cardx, cardy = card.size

    im_stream = current_user.picture.get()
    photo = Image.open(im_stream)


    MAX_SIZE = (160,160)
    photo.thumbnail(MAX_SIZE, Image.ANTIALIAS) #Maintains the aspect ratio.; May be store small file itself in database once size is standardized
    photox, photoy = photo.size

    qrcode = generate_auth_qrcode(current_user)
    qrx, qry = qrcode.size

    stamp = Image.open(os.path.join(settings.APP_STATIC, 'IssuingAuthority.png'))
    stamp.thumbnail(MAX_SIZE, Image.ANTIALIAS) #Maintains the aspect ratio. 
    stampx, stampy = stamp.size

    card.paste(qrcode, ((cardx//2 - qrx//2), (cardy//2 - qry//2)-50))
    card.paste(photo, (cardx - photox - 30, cardy - photoy - 30))
    card.paste(stamp, (cardx - stampx - 30, 30))

    d = ImageDraw.Draw(card)
    font = ImageFont.truetype("FreeMono.ttf",20)
    d.text((30,cardy-75), current_user.name, fill=(0,0,0), font=font)  #Need to strp after certain length ?

    rep = current_user.reports[-1]
    datestr = str(rep.lab_date)
    d.text((30,cardy-50), datestr, fill=(0,0,0), font=font)

    #card.show()
    #card.save('idcard.png', quality=95)



    tempFileObj = NamedTemporaryFile(mode='w+b',suffix='png')
    card.save(tempFileObj, "PNG")
    tempFileObj.seek(0,0)

    return tempFileObj


# Import QRCode from pyqrcode 
import qrcode 



def ggenerate_auth_qrcode(current_user):
    # String which represents the QR code 
    authurl = url_for("__verify",_external=True, key=enc_msg.encrypt_msg(current_user.email)) #Need to encrypt
    # Generate QR code 
    img = qrcode.make(authurl) 
    return img 


def generate_auth_qrcode(current_user):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    authurl = url_for("__verify",_external=True, key=enc_msg.encrypt_msg(current_user.email)) #Need to encrypt
    qr.add_data(authurl)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


