from flask import flash, redirect, render_template, request, session, url_for, current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, BadTimeSignature

from ..db import get_db
from . import bp


@bp.route("/confirm", methods=("GET", "POST"))
def confirm():
    code = request.args.get("code")

    errors = []
    if not code:
        errors.append("No code.")

    if not errors:
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
        
        sql = 'UPDATE "user" SET is_confirmed=TRUE WHERE id = %s;'
        with get_db().cursor() as cursor:
            cursor.execute(sql, (user_id,))
        
        session['user_id'] = user_id
        current_app.logger.info(f"{user_id} confirmed their email.")
        return render_template("auth/confirm_success.jinja2")
    else:
        current_app.logger.info(f"Email confirmation error.")
        return render_template("auth/confirm_fail.jinja2")

