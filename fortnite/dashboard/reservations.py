from flask import g, render_template, request
from werkzeug.exceptions import abort

from datetime import timedelta

from ..login import login_required
from ..db import get_db
from . import bp


@bp.route("/reservations")
@login_required
def reservations():
    sql = (
        "SELECT reservation.*, "
        "CASE WHEN reservation_status.status = 'canceled' THEN 'Canceled' "
        "WHEN reservation_status.status = 'denied' THEN 'Denied' "
        "WHEN reservation_status.status = 'pending approval' THEN 'Pending Approval' "
        "WHEN reservation_status.status = 'approved' AND arrival <= NOW() "
        " AND departure >= NOW() THEN 'Active' "
        "WHEN reservation_status.status = 'approved' AND departure < NOW() THEN 'Past' "
        "WHEN reservation_status.status = 'approved' AND arrival > NOW() THEN 'Upcoming' "
        "ELSE NULL END status_string,"
        "CASE WHEN reservation_status.status = 'canceled' OR arrival < NOW() THEN 0 "
        "ELSE 1 END is_cancelable "
        "FROM reservation "
        "LEFT JOIN reservation_status ON reservation.status_id = reservation_status.id "
        "WHERE reservation.user_id = %s "
        "AND reservation.property_id = %s "
        "ORDER BY reservation.created DESC; "
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.user["id"], g.property["id"]))
        results = cursor.fetchall()

    reservations = []
    for result in results:
        reservation = {}
        # Create reservation name string
        arrival_str = result["arrival"].strftime("%a %-m/%-e/%Y")
        departure_str = result["departure"].strftime("%a %-m/%-e/%Y")
        reservation_str = f"{arrival_str} - {departure_str}"
        if result["name"]:
            reservation_str += f" ({result['name']})"
        reservation["reservation"] = reservation_str
        # Calculate duration of stay
        tdelta = result["departure"] - result["arrival"]
        reservation["nights"] = tdelta.days
        # Reservation status
        reservation["status"] = result["status_string"]
        # Is cancelable
        reservation["is_cancelable"] = result["is_cancelable"]
        # id
        reservation["id"] = result["id"]

        reservations.append(reservation)

    return render_template("dashboard/reservations.jinja2", reservations=reservations)


@bp.route("/reservation/<int:reservation_id>", methods=("DELETE",))
@login_required
def reservation(reservation_id):

    # check to make sure user owns reservation
    sql = "SELECT * FROM reservation WHERE id = %s;"
    with get_db().cursor() as cursor:
        cursor.execute(sql, (reservation_id,))
        reservation = cursor.fetchone()
    if reservation["user_id"] != g.user["id"]:
        abort(401)

    # success, update reservation
    sql = "UPDATE reservation SET status_id = 4 WHERE id=%s;"
    with get_db().cursor() as cursor:
        cursor.execute(sql, (reservation_id,))
    return "success"


@bp.route("/cancellation_success")
@login_required
def cancellation_success():
    return render_template("dashboard/cancellation_success.jinja2")
