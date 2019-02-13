from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from fortnite.db import get_db

bp = Blueprint("register", __name__, url_prefix="/register")


@bp.route("/", methods=("GET", "POST"), strict_slashes=False)
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        db = get_db()

        error = None
        if not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        elif db.execute("SELECT id from user WHERE email = ?", (email,)).fetchone():
            error = f"Email {email} is already registered."

        if error is None:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO user (email, password, first_name, last_name) VALUES (?, ?, ?, ?)",
                (email, generate_password_hash(password), first_name, last_name),
            )
            db.commit()
            user_id = cursor.lastrowid
            cursor.close()

            session["user_id"] = user_id
            print(url_for("register.register"))
            return redirect(url_for("dashboard.index"))

        flash(error)

    return render_template("register/register.jinja2")
