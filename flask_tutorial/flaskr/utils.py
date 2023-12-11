import os
from flask_mail import Message
from flask import current_app


def send_email(to, subject, template):
    mail = current_app.config['MAIL']
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=os.getenv('MAIL_DEFAULT_SENDER')
    )
    mail.send(msg)
