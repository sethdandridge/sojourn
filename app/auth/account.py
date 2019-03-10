from flask import Blueprint, flash, redirect, render_template, request, session, url_for, g
from werkzeug.security import check_password_hash, generate_password_hash


from ..db import get_db
from . import login_required
from . import bp

@login_required
@bp.route("/account", methods=("GET", "POST"))
def account():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        error = None
        if password1 != password2:
            error = "Passwords don't match"
        if password1 and password2 and password1 == password2:
            password = password1 
        else:
            password = None

        if not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        
        if error is None:
            if password is None:
                sql = (
                    'UPDATE "user" '
                    ' SET first_name = %s, '
                    ' last_name = %s '
                    'WHERE id = %s; '
                )
                with get_db().cursor() as cursor:
                    cursor.execute(
                        sql,
                        (first_name, last_name, g.user['id']),
                    ) 
            else:
                sql = (
                    'UPDATE "user" '
                    ' SET first_name = %s, '
                    ' last_name = %s, '
                    ' password = %s '
                    'WHERE id = %s; '
                )
                with get_db().cursor() as cursor:
                    cursor.execute(
                        sql,
                        (first_name, last_name, generate_password_hash(password), g.user['id']),
                    )

            flash("Account information successfully updated!", "success")

            return redirect(url_for('index'))

        else: 
            flash(error)
 
    return render_template("auth/account.jinja2")

@login_required
@bp.route("/account/delete", methods=("GET", "POST"))
def delete_account():
    if request.method == "POST":
        sql = (
            'DELETE FROM "user" '
            'WHERE "user".id = %s; ' 
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql, (g.user['id'],))
 
        flash("Account deleted :(", "success")
        return redirect(url_for('dashboard.index')) 

    return render_template('auth/delete_account.jinja2')
