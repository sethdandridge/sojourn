import logging
from logging.handlers import RotatingFileHandler

from flask import render_template, current_app
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.exceptions import abort

from .db import get_db

mail = Mail()
logger = logging.getLogger(__name__)

class EmailFormatter(logging.Formatter):
    def format(self, record):
        record.sender = msg.sender
        record.date = msg.date
        record.recipients = msg.recipients
        record.body = msg.body
        record.subject = msg.subject
        return super().format(record)

def init_mail(app):
    mail.init_app(app)
    rotating_file_handler = RotatingFileHandler(
        app.instance_path + '/email.txt',
        maxBytes = 1024 * 1024 * 10, #10 megabytes
        backupCount = 10
    )
    formatter = EmailFormatter(
        'From: %(sender)s\nSubject: %(subject)s'
    )
    rotating_file_handler.setFormatter(formatter)
    logger.addHandler(rotating_file_handler)
    logger.setLevel("INFO")

# auth
def generate_confirmation_token(user_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def mail_registration_confirmation(user_id):
    with get_db().cursor() as cursor:
        cursor.execute('SELECT * FROM "user" WHERE id = %s;', (user_id,))
        user = cursor.fetchone()
        if not user:
            abort(500)

    user = dict(user)
    user['confirmation_token'] = generate_confirmation_token(user_id)

    msg_body = render_template('email/registration_confirmation.jinja2', user=user)
    msg = Message(f"Confirm your email to start using {current_app.config['APP_NAME']}!",
              html=msg_body,
              #sender=(current_app.config['APP_NAME'], "accounts@sojourn.house"),
              sender="accounts@sojourn.house",
              recipients=[user['email']]) 
    mail.send(msg, envelope_from='accounts@sojourn.house')

def mail_password_reset(user): 
    user = dict(user)
    user['password_reset_token'] = generate_confirmation_token(user['id']) 

    msg_body = render_template('email/reset_password.jinja2', user=user)
    msg = Message(f"Confirm your email to start using {current_app.config['APP_NAME']}!",
          html=msg_body,
          sender="accounts@sojourn.house",
          recipients=[user['email']]) 
    mail.send(msg, envelope_from='accounts@sojourn.house')

# invitation
def mail_invitation_existing_user(invite_id, owner_user_id, property_id):
    return True

def mail_invitation_existing_user(user_id, owner_user_id, property_id): 
    return True

# booking
def mail_reservation_notification(reservation_id):
    return True

def mail_reservatation_owner_notification(reservation_id):
    return True

def mail_reservation_approval_request(reservation_id):
    return True

def mail_reservation_approved(user_owner_id, reservation_id):
    return True

def mail_reservation_denied(user_owner_id, reservation_id):
    return True

def mail_cancellation_notification(reservation_id):
    return True
