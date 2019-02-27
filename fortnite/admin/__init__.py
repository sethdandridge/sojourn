from flask import Blueprint, g, redirect, render_template, session
from werkzeug.exceptions import abort
import functools

from ..login import login_required
from ..db import get_db


def admin_required(view):
    @login_required
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.property["is_admin"]:
            abort(401)

        #if reservation_id:
        #    sql = (
        #        "SELECT * FROM reservation "
        #        "WHERE reservation.id = %s; "
        #    )
        #    with get_db().cursor() as cursor:
        #        cursor.execute(sql, (reservation_id,))
        #        reservation = cursor.fetchone()
        #    if reservation and reservation['property_id'] != g.property['id']:
        #        abort(404)

        return view(**kwargs)

    return wrapped_view


bp = Blueprint("admin", __name__)

from . import guests
from . import calendar
from . import reservations
