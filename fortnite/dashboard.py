from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from fortnite.login import login_required
from datetime import datetime, date, timedelta

from fortnite.db import get_db

bp = Blueprint("dashboard", __name__)


def get_booked_dates(db):
    reservations = db.execute(
        'SELECT * FROM reservation WHERE date(arrival) >= DATE("now");'
    ).fetchall()
    booked_dates = []
    for reservation in reservations:
        arrival_date = datetime.strptime(reservation["arrival"], "%Y-%m-%d").date()
        departure_date = datetime.strptime(reservation["departure"], "%Y-%m-%d").date()
        delta = departure_date - arrival_date
        for i in range(delta.days + 1):
            booked_dates.append(arrival_date + timedelta(i))
    js_fixed_dates = []
    for booked_date in booked_dates:
        year = booked_date.year
        month = booked_date.month
        date = booked_date.day
        js_fixed_dates.append(f"{year}, {month - 1}, {date}")
    return js_fixed_dates


@bp.route("/")
@login_required
def index():
    return render_template("dashboard/index.jinja2")


@bp.route("/book", methods=("GET", "POST"))
@login_required
def book():
    if request.method == "POST":
        arrival_date = request.form.get("arrival_date")
        departure_date = request.form.get("departure_date")
        reservation_name = request.form.get("name")
        print(arrival_date)
        print(departure_date)

        error = None
        if not arrival_date:
            error = "Please specify an arrival date."
        elif not departure_date:
            error = "Please specify a departure date."

        # departure before arrival
        # arrival same as departure
        # reservation is in the past
        # reservation_status id = whatever
        reservation_status_id = 1  # active

        if error is None:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO reservation"
                " (user_id, name, arrival, departure, status_id, created)"
                "VALUES"
                " (?, ?, ?, ?, ?, DATETIME('now'))",
                (
                    g.user["id"],
                    reservation_name,
                    arrival_date,
                    departure_date,
                    reservation_status_id,
                ),
            )
            db.commit()
            reservation_id = cursor.lastrowid
            cursor.close()

            return redirect(
                url_for("dashboard.book_success", reservation=reservation_id)
            )
        else:
            flash(error)

    db = get_db()
    booked_dates = get_booked_dates(db)

    return render_template("dashboard/book.jinja2", booked_dates=booked_dates)


@bp.route("/reservations", methods=("GET", "POST"))
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
        "ORDER BY DATETIME(reservation.created) DESC "
    ).fetchall()
    reservations = []
    for result in results:
        reservation = {}
        # Create reservation name string
        arrival = datetime.strptime(result["arrival"], "%Y-%m-%d")
        departure = datetime.strptime(result["departure"], "%Y-%m-%d")
        arrival_str = arrival.strftime("%a %-m/%e/%Y")
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
        
        reservations.append(reservation)
 
    return render_template("dashboard/reservations.jinja2", reservations=reservations)


@bp.route("/book/success")
@login_required
def book_success():
    return "Congrats on booking your vacation! You will receive an email confirmation when you're approved."
