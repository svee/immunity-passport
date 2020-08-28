

from flask import render_template,redirect, url_for, request, flash

# .....


from ipass import app  #From this package. app is created in __init__
from ipass import forms #Notice forms.SignupForm, etc...  way to access object in other file. 


# ...

#If used is logged-in (active session); home page will have link/Buttons to Sign-out and Get Passport
#If used is NOT logged-in (inactive session); home page will have link/Buttons to Sign-up and Sign-in
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = forms.SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Check your email for activation link in')
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
    form = forms.LoginForm()
    if request.method == 'POST' and form.validate():
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/getpassport', methods=['GET', 'POST'])
def getpassport():
    form = forms.GetPassportForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Imunity Passport will download now')
        return redirect(url_for('home'))
    return render_template('getpassport.html', title = 'Immunity Passport Request', form=form)

@app.route('/update', methods=['GET', 'POST'])
def update():
    form = forms.UpdateCovidTestForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Updated Imunity Passport will download now')
        return redirect(url_for('home'))
    return render_template('update.html', title = 'Immunity Passport Request', form=form)

@app.route('/editprofile', methods=['GET', 'POST'])
def editprofile():
    form = forms.EditProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        flash('Profile is updated Successfully')
        return redirect(url_for('home'))
    return render_template('editprofile.html', title = 'Edit Profile Data', form=form)

