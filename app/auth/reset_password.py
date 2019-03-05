from flask import flash, redirect, render_template, request, session, url_for, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, BadTimeSignature

from ..db import get_db
from . import bp


@bp.route("/reset_password", methods=("GET", "POST"))
def reset_password():
    code = request.args.get("code")
    errors = []
    if not code:
        errors.append("No code.")

    if request.method == "POST":
        password = request.form['password']

        if not password:
            errors.append("Please enter a password")

        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serializer.loads(
                code, 
                salt=current_app.config["SECURITY_PASSWORD_SALT"], 
                max_age=60 * 60 * 24 * 7, # expires after 1 week
            )
        except BadSignature:
            errors.append("Invalid code.")
        except BadTimeSignature:
            errors.append("Code expired.")
 
        if not errors:
            user_id = int(user_id)
            
            sql = 'UPDATE "user" SET password=%s WHERE id = %s RETURNING id;'
            with get_db().cursor() as cursor:
                cursor.execute(sql, (generate_password_hash(password), user_id))
            
            session['user_id'] = user_id # there is a bug here if the user is deleted between sending password reset and resetting password

            flash("Password successfully reset!", "success")

            return redirect(url_for('dashboard.index'))


    for error in errors:
        flash(error)
    return render_template("auth/reset_password.jinja2")

