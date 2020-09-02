

from flask import render_template,redirect, url_for, request, flash,  send_file

# .....


from impass import app  #From this package. app is created in __init__
from impass import forms #Notice forms.SignupForm, etc...  way to access object in other file. 



from flask_mongoengine import MongoEngine, Document
from mongoengine import *
from wtforms import StringField, PasswordField, FileField
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


from PIL import Image, ImageDraw, ImageFilter, ImageFont 
import os.path


from impass import settings 
from flask import jsonify

from impass import enc_msg

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
	lab_antibody_test = db.BooleanField()
	lab_report = db.FileField()

class User(UserMixin, db.Document):
    meta = {'collection': 'PassHolders'}
    email = db.StringField(max_length=500)
    password = db.StringField()
    name = db.StringField(max_length=30)
    picture=db.ImageField()
    reports = ListField(EmbeddedDocumentField(Report))



@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

#If used is logged-in (active session); home page will have link/Buttons to Sign-out and Get Passport
#If used is NOT logged-in (inactive session); home page will have link/Buttons to Sign-up and Sign-in
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated == True:
        flash('Logout before registering another user')
        return redirect(url_for('dashboard'))

    form = forms.SignupForm(request.form)
    if request.method == 'POST' and form.validate():

        existing_user = User.objects(email=form.email.data).first()
        if existing_user is None:
            print ("register ok")
            hashpass = generate_password_hash(form.password.data, method='sha256')
            newuser = User(email=form.email.data,password=hashpass).save()
            flash('Check your email for activation link')
            return redirect(url_for('login'))
        flash('You have already registered')
        return redirect(url_for('login'))
    return render_template('signup.html', title = 'Sing up with your email ID', form=form)

# This function is yet to be implemented.
@app.route('/activate', methods=['GET'])
def activate():
    form = forms.ActivateForm(request.form)
    if request.method == 'GET' and form.validate():
        flash('Your Account is now active; Proceed to log-in')
        return redirect(url_for('login'))
    flash('Activation Link has expired or invalid activation code.') #Validation is to be done here.
    return render_template('signup.html', title = 'Sing up with your email ID', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('dashboard'))
    form = forms.LoginForm()
    if request.method == 'POST' and form.validate():

        user_rec = User.objects(email=form.email.data).first()
        if user_rec:
            if check_password_hash(user_rec['password'], form.password.data):
                login_user(user_rec)
                return redirect(url_for('dashboard'))
        flash('Invalid Credentials; Try again')
        return redirect(url_for('login'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.email)


@app.route('/getpassport', methods=['GET', 'POST'])
@login_required
def getpassport():
    form = forms.GetPassportForm()
    if request.method == 'POST' and form.validate():
        rep = Report(lab_name=form.lab_name.data, lab_city=form.lab_city.data, 
            lab_country=form.lab_country.data,lab_date=form.lab_date.data, lab_antibody_test=form.lab_testtype.data)
        f = form.lab_report.data
        filename = secure_filename(f.filename)

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

        tempFileObj = generate_idcard(current_user)
        response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
        return response

        #flash('Imunity Passport will download now')
        #return redirect(url_for('dashboard'))
    elif (current_user.name):  #User information already present; just ask for test/vaccination details 
         return redirect(url_for('update'))
    else:
        return render_template('getpassport.html', title = 'Immunity Passport Request', form=form)

@app.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    form = forms.UpdateCovidTestForm()
    if request.method == 'POST' and form.validate():
        rep = Report(lab_name=form.lab_name.data, lab_city=form.lab_city.data, 
            lab_country=form.lab_country.data,lab_date=form.lab_date.data, lab_antibody_test=form.lab_testtype.data)

        f = form.lab_report.data
        filename = secure_filename(f.filename)

        rep.lab_report.put(f) 

        current_user.reports.append(rep)  #Should there be limit on number of submissions ?
        current_user.save()

        tempFileObj = generate_idcard(current_user)
        response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
        return response

        #flash('Updated Imunity Passport will download now')
        #return redirect(url_for('dashboard'))
    else:
        return render_template('update.html', title = 'Immunity Passport Request', form=form)

@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = forms.EditProfileForm()
    if request.method == 'POST' and form.validate():
        current_user.name = form.username.data

        pf = form.picture.data
        filename = secure_filename(pf.filename)
        if(current_user.picture == None):  #First time updating
            current_user.picture.put(pf) 
        else:
            current_user.picture.replace(pf) 

        current_user.save()

        tempFileObj = generate_idcard(current_user)
        response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
        return response

        #flash('Profile is updated Successfully')
        #return redirect(url_for('dashboard'))
    return render_template('editprofile.html', title = 'Edit Profile Data', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/__verify")
def __verify():
    print("Here in Verify")
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
            return 'User Get New option and provide user/test data'
        else:
            tempFileObj = generate_idcard(current_user)
            response = send_file(tempFileObj, as_attachment=True, attachment_filename='immunity_passport.png')
            return response



import io
from tempfile import NamedTemporaryFile
from shutil import copyfileobj



def generate_idcard(current_user):

    card = Image.open(os.path.join(settings.APP_STATIC, 'Immunity Passport.png'))
    cardx, cardy = card.size

#   photo = Image.open('photo.jpg')
    im_stream = current_user.picture.get()
    photo = Image.open(im_stream)


    MAX_SIZE = (160,160)
    photo.thumbnail(MAX_SIZE, Image.ANTIALIAS) #Maintains the aspect ratio.; May be store small file itself in database once size is standardized
    photox, photoy = photo.size

    qrcode = generate_auth_qrcode(current_user)
    #qrcode = Image.open(os.path.join(settings.APP_STATIC, 'qrcode.png'))
    qrx, qry = qrcode.size


    card.paste(qrcode, ((cardx//2 - qrx//2), (cardy//2 - qry//2)-50))
    card.paste(photo, (cardx - photox - 30, cardy - photoy - 30))

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


