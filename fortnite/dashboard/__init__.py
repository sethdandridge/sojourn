from flask import Blueprint, g, redirect, render_template, session
from werkzeug.exceptions import abort
import functools

from ..login import login_required
from ..db import get_db

bp = Blueprint("dashboard", __name__)

from . import book
from . import reservations
from . import create_property
from . import switch_property


@bp.route("/")
@login_required
def index():
    return render_template("dashboard/index.jinja2")


@bp.before_app_request
def load_user_properties():
    if g.user:
        sql = (
            "SELECT property.*, user_to_property.is_admin FROM user_to_property "
            "JOIN property ON property.id = user_to_property.property_id "
            "WHERE user_to_property.user_id = %s; "
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql, (g.user["id"],))
            g.properties = cursor.fetchall()


@bp.before_app_request
def load_active_property():
    active_property_id = session.get("active_property_id")
    if g.user and g.properties:
        if active_property_id is None:
            g.property = g.properties[0]
        else:
            sql = (
                "SELECT property.*, user_to_property.is_admin FROM user_to_property "
                "JOIN property ON property.id = user_to_property.property_id "
                "WHERE user_to_property.user_id = %s "
                "AND property.id = %s; "
            )

            with get_db().cursor() as cursor:
                cursor.execute(sql, (g.user["id"], active_property_id))
                g.property = cursor.fetchone()

            session["active_property_id"] = g.property["id"]
            # else:
            #    g.property = g.properties[0]
