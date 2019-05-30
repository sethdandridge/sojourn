from flask import render_template, current_app, g
from itsdangerous import URLSafeTimedSerializer
from werkzeug.exceptions import abort
import boto3
from botocore.exceptions import ClientError

from .db import get_db

def get_ses_client():
    if "ses_client" not in g:
        g.ses_client = boto3.client(
            service_name = 'ses',
            region_name='us-east-1',
            aws_access_key_id=current_app.config['AWS_SES_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SES_SECRET_ACCESS_KEY'],
        )
    return g.ses_client

def send(sender, recipient, subject, message_html):
    try:
        response = get_ses_client().send_email(
            Source=sender,
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Subject': {'Charset': "UTF-8", 'Data': subject},
                'Body': {
                    'Html': {'Charset': "UTF-8", 'Data': message_html},
                    #'Text': {'Charset': "UTF-8", 'Data': message_text},  
                }, 
            },
        )
    except ClientError as e:
        current_app.logger.error(e.response['Error']['Message'])
    else:
        current_app.logger.info(f"Sent email: {subject} to {recipient}! message_id: {response['MessageId']}")

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

    message_html = render_template('email/registration_confirmation.jinja2', user=user)
    subject = f"Confirm your email to start using {current_app.config['APP_NAME']}!"
    sender = f"{current_app.config['APP_NAME']} <accounts@sojourn.house>"
    recipient = f"{user['first_name']} {user['last_name']} <{user['email']}>"

    send(sender, recipient, subject, message_html)

def mail_password_reset(user):
    user = dict(user)
    user['password_reset_token'] = generate_confirmation_token(user['id'])

    message_html = render_template('email/reset_password.jinja2', user=user)
    subject = f"Password reset"
    sender = f"{current_app.config['APP_NAME']} <accounts@sojourn.house>"
    recipient = f"{user['first_name']} {user['last_name']} <{user['email']}>"

    send(sender, recipient, subject, message_html)

# invitation

def mail_invitation_existing_user(guest):
    message_html = render_template('email/invitation_existing_user.jinja2', guest=guest)
    subject = f"{g.user['first_name']} {g.user['last_name']} invited you to {g.property['name']}"
    sender = f"{current_app.config['APP_NAME']} <invites@sojourn.house>"
    recipient = f"{guest['first_name']} {guest['last_name']} <{guest['email']}>"
    
    send(sender, recipient, subject, message_html)


def mail_invitation_new_user(invite_email):
    message_html = render_template('email/invitation_new_user.jinja2', invite_email=invite_email)
    subject = f"{g.user['first_name']} {g.user['last_name']} invited you to {g.property['name']}"
    sender = f"{current_app.config['APP_NAME']} <invites@sojourn.house>"
    recipient = invite_email

    send(sender, recipient, subject, message_html)

# booking
def mail_reservation_confirmation(reservation):
    message_html = render_template('email/reservation_confirmation.jinja2', reservation=reservation)
    subject = f"{g.property['name']} reservation confirmation"
    sender = f"{current_app.config['APP_NAME']} <reservations@sojourn.house>"
    recipient = f"{g.user['first_name']} {g.user['last_name']} <{g.user['email']}>"

    send(sender, recipient, subject, message_html)

def mail_reservatation_owner_notification(reservation):
    return True

def mail_reservation_approval_request(reservation):
    sql = (
        'SELECT * FROM "user" '
        'JOIN user_to_property ON user_to_property.user_id = "user".id '
        'WHERE user_to_property.is_admin = TRUE '
        'AND user_to_property.property_id = %s'
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.property['id'],))
        admins = cursor.fetchall()
    
    subject = f"{g.user['first_name']} {g.user['last_name']}'s reservation at {g.property['name']} is pending approval"
    sender = f"{current_app.config['APP_NAME']} <reservations@sojourn.house>"
    for admin in admins:
        recipient = f"{admin['first_name']} {admin['last_name']} <{admin['email']}>"
        message_html = render_template('email/reservation_approval_request.jinja2', admin=admin, reservation=reservation)
        send(sender, recipient, subject, message_html)

def mail_reservation_approved(reservation):
    message_html = render_template('email/reservation_approval.jinja2', reservation=reservation)
    subject = f"Your stay at {g.property['name']} has been approved!"
    sender = f"{current_app.config['APP_NAME']} <reservations@sojourn.house>"
    recipient = f"{reservation['first_name']} {reservation['last_name']} <{reservation['email']}>"

    send(sender, recipient, subject, message_html)

def mail_reservation_denied(user_owner_id, reservation_id):
    return True

def mail_cancellation_notification(reservation_id):
    return True
