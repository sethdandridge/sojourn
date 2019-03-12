from flask import render_template, g, request, url_for, redirect, flash, current_app

from ..db import get_db
from ..email import mail_password_reset
from . import bp

@bp.route("/send_password_reset", methods=("GET", "POST"))
def send_password_reset(): 
    if request.method == "POST":
        email = request.form["email"]

        error = None
        if not email:
            error = "Email is required"
        
        if not error:
            sql = ('SELECT * FROM "user" WHERE email ILIKE %s;')
            with get_db().cursor() as cursor:
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
            if not user:
                error = (
                    f"User {email} not found. Click register to create an account."
                )
        if not error:
            mail_password_reset(user)
            flash("Password reset instructions sent! Check your email to reset your password.", "success")
            current_app.logger.info(f'{user["id"]} ({user["email"]}) requested password reset')
            return redirect(url_for('auth.login'))
        else:
            current_app.logger.info(f'{request.form.get("email")} requested password reset error: {error}')
            flash(error)
    return render_template("auth/send_password_reset.jinja2")
