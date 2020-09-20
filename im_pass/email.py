from flask_mail import Message

from im_pass import app, mail


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
            
    mail.send(msg)
