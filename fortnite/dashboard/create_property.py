from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort

from ..login import login_required
from ..db import get_db
from . import bp

@bp.route("/create_property", methods=("GET", "POST",))
@login_required
def create_property():
    if request.method == "POST":
        property_name = request.form.get("name")

        error = None
        if not property_name:
            error = "Please specify a property name."

        if error is None:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO property "
                "(owner_user_id, name) "
                "VALUES "
                "(?, ?);",
                (
                    g.user["id"],
                    property_name,
                ),
            )
            property_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO user_to_property "
                "(user_id, property_id, is_admin) "
                "VALUES "
                "(?, ?, ?);",
                (
                    g.user["id"],
                    property_id,
                    1,
                ),
            )
            db.commit()
            cursor.close()

            session['active_property_id'] = property_id
            return redirect(url_for('dashboard.index'))
        else:
            flash(error)
        
    return render_template("dashboard/create_property.jinja2")

@bp.route("/create_propery/success")
@login_required
def create_propery_success():
    #return "Congrats on booking your vacation! You will receive an email confirmation when you're approved."
    # check if user can access other users's confirmations
    return render_template("dashboard/book_success.jinja2")
