#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# @author: vee
#
# both send email as well as worker thread functions.

from flask_mail import Message
from flask import url_for, render_template, flash

from im_pass import app, mail
from im_pass import enc_msg

from redis import Redis
from rq import Queue

# This gets executed in worker thread (rqworker in case of Redis).
# mail.send needs access to application context.
def worker_sendmail(msg):
    with app.app_context():
        mail.send(msg)

# Construct the message, include attachment and enque it so it can be executed by worker thread
# asynchronously
def send_email(to, subject, template,fp=None, filename=None, type=None):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    if(fp != None):
        if(type == "pdf"):
            msg.attach(filename,"application/pdf",fp.read())
        else: #image
            msg.attach(filename,"image/png",fp.read())
    
    # Using Redis task queue to execute send mail function in asynchronous mode.
    q = Queue(connection=Redis())
    q.enqueue(worker_sendmail,msg)
    #mail.send(msg)



# create url for password reset link and email to the registered user.
def generate_password_reset(email_id):
    token = enc_msg.gen_secret_key(email_id)
    reset_url = url_for('__reset', token=token, _external=True)
    html = render_template('password_reset_request.html', reset_url=reset_url)
    subject = "Password reset request - Immunity Passport"
    try:
       send_email(email_id, subject, html)  
    except Exception as e:
        flash("Error connecting to email server; try again later")


# create url for activating account and send email once signed-up.
def generate_confirmation(email_id):
    #Form email activation link and send
    token = enc_msg.gen_secret_key(email_id)
    confirm_url = url_for('__activate', token=token, _external=True)
    html = render_template('email_activation.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    try:
       send_email(email_id, subject, html) 
    except Exception as e:
        flash("Error connecting to email server; try again later")

def generate_report_approval(email_id, fattach, name, lab_name, lab_city, lab_country, lab_date, lab_report_type,report_index):
    token = enc_msg.gen_secret_key(email_id)
    confirm_url = url_for('__approve', token=token, report_index=report_index,_external=True)
    html = render_template('approval_request.html', confirm_url=confirm_url,
                            name=name, lab_name=lab_name, lab_city=lab_city, lab_country=lab_country, 
                            lab_date=lab_date, lab_report_type=lab_report_type)
    subject = "Please review attached report and click on the link to approve"
    try:
       send_email(app.config['APPROVER_EMAIL'], subject, html,fattach, "report.pdf","pdf")  #email integration is not done.
    except Exception as e:
        flash("Error connecting to email server; try again later")
        return
    flash('Report is sent for approval. Download once it is done')

# Once the report is approved, this is called to send immunity pass through e-mail
def generate_immunity_pass(email_id, fattach):
    html = render_template('passportby_mail.html')
    subject = "Your immunity pass is approved"
    try:
        send_email(email_id, subject, html,fattach,"immunity_passport.png", "png") 
    except Exception as e:
        return   #Silent here as user can later download always.


