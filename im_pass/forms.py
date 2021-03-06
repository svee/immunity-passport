#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 
# @author: vee
#
# File contains definition for various forms.
  
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import Form, BooleanField,DateField, StringField, SelectField, PasswordField, SubmitField, validators, IntegerField
#Note: Submit is currently handled inside jinja template.


from wtforms.validators import DataRequired,Email, Length, InputRequired, ValidationError
from flask_wtf.file import FileField, FileRequired, FileAllowed

import pycountry

class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha_3, country.name) for country in pycountry.countries]

# Covid- Real Time PCR is used to generate Covid Pass - that is someone is currently clear of Covid
# Antibody Test is used to generate Immunity Pass for prescribed period 
# Antibody Test is used to generate Immunity Pass for prescribed period as per vaccination recoddemdations
# If this is to be changed in future to add more test types, corresponding expiry time needs to be set
# in app_settings.py
REPORT_TYPE = [
        ("Covid- Real Time PCR","Covid- Real Time PCR"),
        ("Antibody Test","Antibody Test"),
        ("Vaccination","Vaccination"),
        ]


class SignupForm(FlaskForm):
    email = StringField('Email address', validators=[InputRequired(), Email(message='Invalid email'), Length(min=6, max=30)])
    password = PasswordField('New Password', [
        validators.InputRequired(), validators.Length(min=8, max=20, message="Password length minimum 8 maximum 30"),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password') #Can be removed later if we have show/hide feature
    recaptcha = RecaptchaField()

class ActivateForm(FlaskForm):
    email = StringField('Email', [validators.Length(min=6, max=35)])

class LoginForm(FlaskForm):
    email = StringField('', render_kw={"placeholder": "Email address"}, 
            validators=[InputRequired(), Email(message='Invalid email'), Length(min=6, max=30)])
    password = PasswordField('', render_kw={"placeholder": "Password"}, 
            validators=[InputRequired(), Length(min=8, max=30, message="Invalid Credentials")])

class ForgotPasswordForm(FlaskForm):
    email = StringField('', render_kw={"placeholder": "Email address"}, 
            validators=[InputRequired(), Email(message='Invalid email'), Length(min=6, max=30)])

    recaptcha = RecaptchaField()

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', [
        validators.InputRequired(), validators.Length(min=8, max=20, message="Password length minimum 8 maximum 30"),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password') #Can be removed later if we have show/hide feature

class GetPassportForm(FlaskForm):

    username = StringField('Full Name', validators=[InputRequired(), Length(min=4, max=25)])

    picture = FileField('Passport Photo',
        validators=[FileRequired(),
        FileAllowed(['jpg', 'png'], 'Images only!')])

    lab_name = StringField('Lab Name', [validators.Length(min=4, max=25)])
    lab_city = StringField('City', [validators.Length(min=4, max=25)])
    lab_country = CountrySelectField("Country")
    lab_date = DateField('Date of Covid test', 
            render_kw={"placeholder": "yyyy-mm-dd"}, 
            validators=[InputRequired()])
    lab_report_type = SelectField(choices=REPORT_TYPE,default="Antibody Test", validators=[InputRequired()])
    lab_report = FileField('Covid test/vaccination report (PDF)', validators=[FileRequired(),
        FileAllowed(['pdf'], 'PDF Format only!')])

    

class UpdateCovidTestForm(FlaskForm):
    lab_name = StringField('Lab Name', [validators.Length(min=8, max=40)])
    lab_city = StringField('City', [validators.Length(min=4, max=25)])
    lab_country = CountrySelectField("Country")
    lab_date = DateField('Date of Covid test', 
            render_kw={"placeholder": "yyyy-mm-dd"}, 
            validators=[InputRequired()])
    lab_report_type = SelectField(choices=REPORT_TYPE,default="Antibody Test",validators=[InputRequired()])
    lab_report = FileField('Covid test report (PDF)', validators=[FileRequired(),
        FileAllowed(['pdf'], 'PDF Format only!')])

class __VerifyForm(FlaskForm):
    key = StringField('key', [validators.Length(min=4, max=200)])

# For password reset link. Not required as it is handled as token itself
#class __ResetForm(FlaskForm):
#    key = StringField('key', [validators.Length(min=4, max=200)])

# Email activation
class __ActivateForm(FlaskForm):
    token = StringField('key', [validators.Length(min=4, max=500)])

# Report approval
class __ApproveForm(FlaskForm):
    token = StringField('key', [validators.Length(min=4, max=500)])
    report_index = IntegerField('index')

class AddProfileForm(FlaskForm):
   username = StringField('Full Name',  [validators.Length(min=4, max=25)])
   picture = FileField('Your Passport Size Photo',
   validators=[FileRequired(),
   FileAllowed(['jpg', 'png'], 'Images only!')])

# As profile already exists, FileRequired validator is removed in update form.
class UpdateProfileForm(FlaskForm):
    username = StringField('', render_kw={"placeholder": "Enter Name to change to"}, 
            validators=[validators.Length(max=25)])
    picture = FileField('Upload new picture:',
        validators=[FileAllowed(['jpg', 'png'], 'Jpeg/PNG Images only!')])

