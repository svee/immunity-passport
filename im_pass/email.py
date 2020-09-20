from flask_mail import Message

from im_pass import app, mail


def send_email(to, subject, template,fp=None):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    if(fp != None):
        msg.attach("report.pdf","application/pdf",fp.read())
    mail.send(msg)
