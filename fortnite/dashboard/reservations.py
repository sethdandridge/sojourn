from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from datetime import datetime, date, timedelta

from ..login import login_required
from ..db import get_db
from . import bp

@bp.route("/reservations")
@login_required
def reservations():
    db = get_db()
    results = db.execute(
        "SELECT reservation.*, "
        "CASE WHEN reservation_status.status = 'canceled' THEN 'Canceled' "
        "WHEN reservation_status.status = 'denied' THEN 'Denied' "
        "WHEN reservation_status.status = 'pending approval' THEN 'Pending Approval' "
        "WHEN reservation_status.status = 'approved' AND DATE(arrival) <= DATE('now') "
        " AND DATE(departure) >= DATE('now') THEN 'Active' "
        "WHEN reservation_status.status = 'approved' AND DATE(departure) < DATE('now') THEN 'Past' "
        "WHEN reservation_status.status = 'approved' AND DATE(arrival) > DATE('now') THEN 'Upcoming' "
        "ELSE NULL END status_string,"
        "CASE WHEN reservation_status.status = 'canceled' OR DATE(arrival) < DATE('now') THEN 0 "
        "ELSE 1 END is_cancelable "
        "FROM reservation "
        "LEFT JOIN reservation_status ON reservation.status_id = reservation_status.id "
        "WHERE reservation.user_id = ? "
        "AND reservation.property_id = ?"
        "ORDER BY DATETIME(reservation.created) DESC ",
        (g.user['id'], g.property['id']),
    ).fetchall()
    reservations = []
    for result in results:
        reservation = {}
        # Create reservation name string
        arrival = datetime.strptime(result["arrival"], "%Y-%m-%d")
        departure = datetime.strptime(result["departure"], "%Y-%m-%d")
        arrival_str = arrival.strftime("%a %-m/%-e/%Y")
        departure_str = departure.strftime("%a %-m/%-e/%Y")
        reservation_str = f"{arrival_str} - {departure_str}"
        if result['name']:
            reservation_str += f" ({result['name']})"
        reservation["reservation"] = reservation_str
        # Calculate duration of stay
        tdelta = departure - arrival
        reservation["nights"] = tdelta.days
        # Reservation status
        reservation["status"] = result["status_string"]
        # Is cancelable
        reservation["is_cancelable"] = result["is_cancelable"]
        # id 
        reservation["id"] = result["id"] 
        
        reservations.append(reservation)
 
    return render_template("dashboard/reservations.jinja2", reservations=reservations)

@bp.route("/reservation/<int:reservation_id>", methods=('DELETE',))
@login_required
def reservation(reservation_id):
    # NEEDS AUTH!!!!!!
    db = get_db()
    # check to make sure user owns reservation
    reservation = db.execute(
        "SELECT * FROM reservation "
        "WHERE id = ?;",
        (reservation_id,)
    ).fetchone()
    if reservation["user_id"] != g.user['id']:
        abort(401)
    # success, update reservation
    db.execute(
        "UPDATE reservation SET status_id = 4 WHERE id=?; ",
        (reservation_id,)
    )
    db.commit()
    return 'success'

@bp.route("/cancellation_success")
@login_required
def cancellation_success(): 
    return render_template("dashboard/cancellation_success.jinja2")
