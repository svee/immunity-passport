#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:56:59 2020

@author: vee
"""

from flask_wtf import FlaskForm
from wtforms import Form, DateField, StringField, PasswordField, SubmitField, validators #Note: Submit is currently handled inside jinja template.
from wtforms.validators import DataRequired

from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class


class SignupForm(FlaskForm):
    email = StringField('Email', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password') #Can be removed later if we have show/hide feature

class ActivateForm(FlaskForm):
    email = StringField('Email', [validators.Length(min=6, max=35)])

class LoginForm(FlaskForm):
	email = StringField('Email', [validators.Length(min=6, max=35)])
	password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
   
#Once the registration is done, user is redirected to give details
#to obtain QR Code that is 
class GetPassportForm(FlaskForm):
	username = StringField('Full Name', [validators.Length(min=4, max=25)])
	dob = DateField('Date of Birth', [validators.InputRequired()])
	lab = StringField('Lab Name', [validators.Length(min=4, max=25)])
	country = StringField('Country', [validators.Length(min=4, max=25)])
	test_date = DateField('Date of Covid test', [validators.InputRequired()])
	test_result = FileField('Covid test report (PDF)')

	photos = UploadSet('photos', IMAGES)

	#Validation will do in the end 
	#picture = FileField('Your Photo', validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
	picture = FileField('Your Photo')


class UpdateCovidTestForm(FlaskForm):
	lab = StringField('Lab Name', [validators.Length(min=4, max=25)])
	country = StringField('Country', [validators.Length(min=4, max=25)])
	test_date = DateField('Date of Covid test', [validators.InputRequired()])
	test_result = FileField('Covid test report (PDF)') #Have to make sure we validate.

class EditProfileForm(FlaskForm):
	username = StringField('Full Name', [validators.Length(min=4, max=25)])
	dob = DateField('Date of Birth', [validators.InputRequired()])
	photos = UploadSet('photos', IMAGES)

	#Validation will do in the end 
	#picture = FileField('Your Photo', validators=[FileAllowed(photos, 'Image only!'), FileRequired('File was empty!')])
	picture = FileField('Your Photo')



