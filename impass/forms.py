#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 10:56:59 2020

@author: vee
"""

from flask_wtf import FlaskForm
from wtforms import Form, BooleanField,DateField, StringField, PasswordField, SubmitField, validators 
#Note: Submit is currently handled inside jinja template.


from wtforms.validators import DataRequired,Email, Length, InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed



class SignupForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(min=6, max=30)])
    password = PasswordField('New Password', [
        validators.InputRequired(), validators.Length(min=8, max=20, message="Password length minimum 8 maximum 20"),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password') #Can be removed later if we have show/hide feature

class ActivateForm(FlaskForm):
    email = StringField('Email', [validators.Length(min=6, max=35)])

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(min=6, max=30)])
	password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20, message="Invalid Credentials")])
   
#Once the registration is done, user is redirected to give details
#to obtain QR Code that is 
class GetPassportForm(FlaskForm):

	username = StringField('Full Name', validators=[InputRequired(), Length(min=4, max=25)])


	picture = FileField('Your Passport Size Photo',
		validators=[FileRequired(),
		FileAllowed(['jpg', 'png'], 'Images only!')])

	lab_name = StringField('Lab Name', [validators.Length(min=4, max=25)])
	lab_city = StringField('City', [validators.Length(min=4, max=25)])
	lab_country = StringField('Country', [validators.Length(min=4, max=25)])
	lab_date = DateField('Date of Covid test', [validators.InputRequired()])
	lab_testtype = BooleanField("Slect if Antibody test",[validators.InputRequired()])
	lab_report = FileField('Covid test report (PDF)') #Have to make sure we validate.

	

class UpdateCovidTestForm(FlaskForm):
	lab_name = StringField('Lab Name', [validators.Length(min=4, max=25)])
	lab_city = StringField('City', [validators.Length(min=4, max=25)])
	lab_country = StringField('Country', [validators.Length(min=4, max=25)])
	lab_date = DateField('Date of Covid test', [validators.InputRequired()])
	lab_testtype = BooleanField("Slect if Antibody test",[validators.InputRequired()])
	lab_report = FileField('Covid test report (PDF)') #Have to make sure we validate.

class __VerifyForm(FlaskForm):
	key = StringField('key', [validators.Length(min=4, max=200)])


class EditProfileForm(FlaskForm):
	username = StringField('Full Name', [validators.Length(min=4, max=25)])
	picture = FileField('Your Passport Size Photo',
		validators=[FileRequired(),
		FileAllowed(['jpg', 'png'], 'Images only!')])

class TestForm(FlaskForm):
	username = StringField('Full Name', [validators.Length(min=4, max=25)])
	picture = FileField('Your Passport Size Photo',
		validators=[FileRequired("What happened to the file"),
		FileAllowed(['jpg', 'png'], 'Images only!')])



