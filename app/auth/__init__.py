from flask import Blueprint, g, redirect, render_template, session, url_for, request
from werkzeug.exceptions import abort
import functools

from ..db import get_db

bp = Blueprint("auth", __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None: 
            if request.path != "/" and request.path != "/logout":
                requested_path = request.full_path
            else:
                requested_path = None
 
            return redirect(url_for("auth.login", next=requested_path))

        return view(**kwargs)

    return wrapped_view

def email_confirmation_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['is_confirmed']:

            return render_template('auth/confirmation_required.jinja2')

        return view(**kwargs)

    return wrapped_view

from . import login
from . import logout
from . import register
from . import confirm
from . import resend_confirmation
from . import send_password_reset
from . import reset_password

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        sql = 'SELECT * FROM "user" WHERE id = %s'
        with get_db().cursor() as cursor:
            cursor.execute(sql, (user_id,))
            g.user = cursor.fetchone()
        # in case the user id in the session cookie no longer exists
        if not g.user:
            session.clear()
