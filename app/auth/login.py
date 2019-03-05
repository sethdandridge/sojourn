from urllib.parse import urlparse

from flask import flash, redirect, render_template, request, session, url_for, g
from werkzeug.security import check_password_hash, generate_password_hash

from ..db import get_db
from . import bp


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        next = request.args.get("next")
        if next and urlparse(next).netloc:
            next = None
 
        error = None
 
        sql = 'SELECT * FROM "user" WHERE email ILIKE %s;'
        with get_db().cursor() as cursor:
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

        if user is None:
            error = "Incorrect username. Click 'Register' to create an account."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password. Click 'Forgot Password' to reset your password"

        if error is None:
            session.clear()
            session["user_id"] = user["id"]

            
            return redirect(next or url_for("index"))

        flash(error)

    return render_template("auth/login.jinja2")
