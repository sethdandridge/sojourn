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
                " (user_id, name, arrival, departure, reservation_status_id)"
                "VALUES"
                " (?, ?, ?, ?, ?)",
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
    reservations = db.execute(
        'SELECT * FROM reservation WHERE date(arrival) >= DATE("now");'
    ).fetchall()
    return render_template("dashboard/reservations.jinja2", reservations=reservations)

@bp.route("/book/success")
@login_required
def book_success():
    return "Congrats on booking your vacation! You will receive an email confirmation when you're approved."
