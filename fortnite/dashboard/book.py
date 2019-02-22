from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from fortnite.login import login_required
from datetime import datetime, date, timedelta

from fortnite.db import get_db

from . import bp


def get_booked_dates(db):
    sql = "SELECT * FROM reservation " "WHERE property_id = %s " "AND status_id != 4;"
    with db.cursor() as cursor:
        cursor.execute(sql, (g.property["id"],))
        reservations = cursor.fetchall()

    booked_dates = []
    for reservation in reservations:
        delta = reservation["departure"] - reservation["arrival"]
        for i in range(delta.days + 1):
            booked_date = reservation["arrival"] + timedelta(i)
            booked_dates.append(
                f"{booked_date.year}, {booked_date.month - 1}, {booked_date.day}"
            )

    return booked_dates


@bp.route("/book", methods=("GET", "POST"))
@login_required
def book():
    if request.method == "POST":
        arrival_date = request.form.get("arrival_date")
        departure_date = request.form.get("departure_date")
        reservation_name = request.form.get("name")

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
            sql = (
                "INSERT INTO reservation "
                "(user_id, property_id, name, arrival, departure, status_id, created) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW()) "
                "RETURNING id; "
            )
            with get_db().cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        g.user["id"],
                        g.property["id"],
                        reservation_name,
                        arrival_date,
                        departure_date,
                        reservation_status_id,
                    ),
                )
                reservation_id = cursor.fetchone()["id"]

            return redirect(
                url_for("dashboard.book_success", reservation=reservation_id)
            )
        else:
            flash(error)

    booked_dates = get_booked_dates(get_db())

    return render_template("dashboard/book.jinja2", booked_dates=booked_dates)


@bp.route("/book/success")
@login_required
def book_success():
    # return "Congrats on booking your vacation! You will receive an email confirmation when you're approved."
    # check if user can access other users's confirmations
    return render_template("dashboard/book_success.jinja2")
