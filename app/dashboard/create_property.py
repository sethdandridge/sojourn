from flask import flash, g, redirect, render_template, request, url_for, session, current_app
from werkzeug.exceptions import abort

from ..auth import login_required, email_confirmation_required
from ..db import get_db
from . import bp


@bp.route("/create_property", methods=("GET", "POST"))
@login_required
@email_confirmation_required
def create_property():
    if request.method == "POST":
        property_name = request.form.get("name")

        error = None
        if not property_name:
            error = "Please specify a property name."

        if error is None:

            sql = (
                "INSERT INTO property "
                "(owner_user_id, name) "
                "VALUES (%s, %s) "
                "RETURNING id; "
            )
            with get_db().cursor() as cursor:
                cursor.execute(sql, (g.user["id"], property_name))
                property_id = cursor.fetchone()["id"]

            sql = (
                "INSERT INTO user_to_property "
                "(user_id, property_id, is_admin) "
                "VALUES (%s, %s, %s); "
            )
            with get_db().cursor() as cursor:
                cursor.execute(sql, (g.user["id"], property_id, True))

            session["active_property_id"] = property_id
            current_app.logger.info(f'{g.user["id"]} ({g.user["email"]}) created new property {property_id} ({property_name})')
            return redirect(url_for("dashboard.index"))
        else:
            current_app.logger.info(f'{g.user["id"]} ({g.user["email"]}) created new property error: {error}')
            flash(error)

    return render_template("dashboard/create_property.jinja2")


@bp.route("/create_property/success")
@login_required
@email_confirmation_required
def create_property_success():
    return render_template("dashboard/book_success.jinja2")
