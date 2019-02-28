from flask import render_template, current_app
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from werkzeug.exceptions import abort

from .db import get_db

mail = Mail()

def init_mail(app):
    mail.init_app(app)

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
        msg = Message(f"Confirm your email to start using Fortnite!",
                  body=msg_body,
                  sender="accounts@fortnite.com",
                  recipients=["sethdan@gmail.com"])
    mail.send(msg)
    return msg_body

def mail_password_reset(user_id):
    return True

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
