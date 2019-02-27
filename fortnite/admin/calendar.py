import re

from flask import flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ..db import get_db
from . import bp
from . import admin_required


@bp.route("/calendar")
@admin_required
def calendar():
    show_past = request.args.get('show_past', 'false')
    show_canceled_and_denied = request.args.get('show_canceled_and_denied', 'false')
    show_past = True if show_past == 'true' else False
    show_canceled_and_denied = True if show_canceled_and_denied == 'true' else False  

    sql = (
        'SELECT *, '
        ' CONCAT("user".first_name, \' \', "user".last_name) AS guest, ' 
        ' departure - arrival AS nights, '
        ' CONCAT( '
        "  TO_CHAR(arrival, 'Dy FMMM/FMDD/YY'), "
        "  ' – ', "
        "  TO_CHAR(departure, 'Dy FMMM/FMDD/YY'), "
        "  CASE "
        "   WHEN (reservation.name != '') AND (reservation.name IS NOT NULL) "
        "    THEN CONCAT(' (', reservation.name, ')' ) "
        "  END " 
        ' ) AS reservation, '
        " CASE "
        "  WHEN reservation_status.status = 'canceled' THEN 'Canceled' "
        "  WHEN reservation_status.status = 'denied' THEN 'Denied' "
        "  WHEN reservation_status.status = 'pending approval' THEN 'Pending Approval' "
        "  WHEN reservation_status.status = 'approved' AND arrival <= NOW() "
        "   AND departure >= NOW() THEN 'Active' "
        "  WHEN reservation_status.status = 'approved' AND departure < NOW() THEN 'Past' "
        "  WHEN reservation_status.status = 'approved' AND arrival > NOW() THEN 'Upcoming' "
        "  ELSE NULL "
        " END AS status_string "
        'FROM reservation '
        'JOIN "user" ON "user".id = reservation.user_id '
        'JOIN reservation_status ON reservation_status.id = reservation.status_id '
        'WHERE property_id = %s '
    )
    if not show_past:
        sql += "AND departure >= NOW() "

    if not show_canceled_and_denied:
        sql += "AND status_id in (1, 2) "

    sql += "ORDER BY arrival ASC " 
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.property['id'],))
        reservations = cursor.fetchall()
    return render_template("admin/calendar.jinja2", reservations=reservations, show_canceled_and_denied=show_canceled_and_denied, show_past=show_past)

