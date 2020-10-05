from flask_mail import Message

from im_pass import app, mail

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


