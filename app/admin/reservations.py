import re

from flask import flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ..db import get_db
from . import bp
from . import admin_required

@bp.route('/reservations/edit/<int:reservation_id>', methods=("GET", "POST"))
@admin_required
def edit_reservation(reservation_id):
    sql = (
        'SELECT *, '
        ' CONCAT("user".first_name, \' \', "user".last_name) AS guest, '
        " TO_CHAR(arrival, 'Dy FMMM/FMDD/YY') as arrival, "
        " TO_CHAR(departure, 'Dy FMMM/FMDD/YY') as departure, "
        " departure - arrival AS nights, "
        " name AS guest_note, "
        " reservation.status_id AS status_id "
        'FROM reservation '
        'JOIN "user" on "user".id = reservation.user_id '
        'WHERE reservation.id = %s; '
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (reservation_id,))
        reservation = cursor.fetchone()
    if not reservation or reservation['property_id'] != g.property['id']:
        abort(404)

    if request.method == "POST":
        status_str = request.form.get("status")

        error = None
        if status_str and status_str.isdigit() and int(status_str) in [1, 2, 3, 4]:
            status = int(status_str)
        else:
            error = "Invalid status. What are you doing?"

        if error:
            flash(error)
        else:
            sql = (
                "UPDATE reservation "
                "SET status_id = %s "
                "WHERE id = %s; "
            )
            with get_db().cursor() as cursor:
                cursor.execute(sql, (status, reservation_id))

            return redirect(url_for('admin.calendar'))

    return render_template('admin/edit_reservation.jinja2', reservation=reservation)
