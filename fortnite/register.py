from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("register", __name__, url_prefix="/register")


@bp.route("/", methods=("GET", "POST"), strict_slashes=False)
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        db = get_db()
        cursor = db.cursor()
        error = None
        if not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        elif cursor.execute('SELECT * from "user" WHERE email LIKE %s;', (email,)):
            error = f"Email {email} is already registered."
        cursor.close()

        if error is None:
            sql = (
                'INSERT INTO "user" (email, password, first_name, last_name) '
                "VALUES (%s, %s, %s, %s) RETURNING id"
            )
            with db.cursor() as cursor:
                cursor.execute(
                    sql,
                    (email, generate_password_hash(password), first_name, last_name),
                )
                user_id = cursor.fetchone()["id"]

            session["user_id"] = user_id
            print(url_for("register.register"))
            return redirect(url_for("dashboard.index"))

        flash(error)

    return render_template("register/register.jinja2")
