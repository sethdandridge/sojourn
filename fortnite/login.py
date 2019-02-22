import functools

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    g,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("login", __name__, url_prefix="/login")


@bp.route("/", methods=("GET", "POST"), strict_slashes=False)
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        error = None

        db = get_db()
        sql = "SELECT * FROM user WHERE email LIKE %s"
        with db.cursor() as cursor:
            user = cursor.execute(sql, (email,)).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("login/login.jinja2")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        sql = 'SELECT * FROM "user" WHERE id = %s'
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            if cursor.rowcount > 0:
                g.user = cursor.fetchone()
            else:
                # in case the user id in the session cookie no longer exists
                session.clear()
                g.user = None


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("login.login"))

        return view(**kwargs)

    return wrapped_view
