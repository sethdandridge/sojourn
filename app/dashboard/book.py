from datetime import datetime, date, timedelta

from flask import flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ..auth import login_required, email_confirmation_required
from ..db import get_db
from . import bp


def get_booked_dates(db):
    sql = "SELECT * FROM reservation WHERE property_id = %s AND status_id != 4;"
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
    if not g.property:
        abort(403)
    if request.method == "POST":
        arrival_date_str = request.form.get("arrival_date")
        departure_date_str = request.form.get("departure_date")
        reservation_name = request.form.get("name")

        errors = []
        # errors relating to input format
        if not arrival_date_str:
            errors.append("Please specify an arrival date.")
        if not departure_date_str:
            errors.append("Please specify a departure date.")
        if reservation_name and len(reservation_name) > 255:
            errors.append("Name of reservation too long (255 character max).")
        try:
            arrival_date = datetime.strptime(arrival_date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(
                "Invalid arrival date format. Please submit dates in YYYY-MM-DD format."
            )
        try:
            departure_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(
                "Invalid departure date format. Please submit dates in YYYY-MM-DD format."
            )
        if errors:
            for error in errors:
                flash(error)
            booked_dates = get_booked_dates(get_db())
            return render_template("dashboard/book.jinja2", booked_dates=booked_dates)

        # errors relating to date availability
        if arrival_date >= departure_date:  # this is also checked in db schema
            errors.append(
                "Arrival date must be prior to departure date. Make sure you are arriving before you are departing."
            )
        if arrival_date < datetime.now().date():
            errors.append(
                "Arrival date is in the past. Please select a future date for your arrival."
            )
        sql = (
            "SELECT * FROM reservation "
            "WHERE status_id = 1 "
            "AND property_id = %(property_id)s "
            "AND ( "
            "   (arrival <= %(arrival)s AND departure >= %(departure)s) "  # booker would arrive to find guests there
            "   OR (arrival >= %(arrival)s AND departure <= %(departure)s) "  # booker would arrive to empty house, but guests would show up
            "   OR (arrival <= %(arrival)s AND departure >= %(arrival)s) "  # booker would arrive to find guests there
            "   OR (arrival <= %(departure)s AND departure >= %(arrival)s) "  # guests would show up
            "); "
        )
        with get_db().cursor() as cursor:
            cursor.execute(
                sql,
                {
                    "property_id": g.property["id"],
                    "arrival": arrival_date,
                    "departure": departure_date,
                },
            )
            if cursor.fetchone():
                errors.append(
                    "These dates overlap with an existing reservation. Please choose different dates."
                )

        # errors relating to reservation limits
        sql = "SELECT * FROM user_to_property_reservation_limits WHERE user_id = %s AND property_id = %s"
        with get_db().cursor() as cursor:
            cursor.execute(sql, (g.user["id"], g.property["id"]))
            limits = cursor.fetchone()
        if limits:  # owners don't have limits

            if limits["max_upcoming"]:
                sql = (
                    "SELECT COUNT(*) AS upcoming FROM reservation "
                    "WHERE user_id = %s "
                    "AND property_id = %s "
                    "AND arrival > NOW() "
                    "AND status_id IN (1, 2); "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(sql, (g.user["id"], g.property["id"]))
                    upcoming = cursor.fetchone()["upcoming"]
                if upcoming + 1 > limits["max_upcoming"]:
                    errors.append(
                        f"Number of upcoming and pending reservations exceeds limit ({limits['max_upcoming']})."
                    )

            if limits["max_duration"]:
                stay_length = departure_date - arrival_date
                duration = stay_length.days
                if duration > limits["max_duration"]:
                    errors.append(
                        f"Duration of stay ({duration} nights) exceeds limit ({limits['max_duration']} nights)."
                    )

            if limits["max_per_month"]:
                sql = (
                    "SELECT * FROM reservation "
                    "WHERE status_id IN (1, 2) "
                    "AND property_id = %s "
                    "AND user_id = %s "
                    "AND departure >= %s - INTERVAL '30 DAYS' "
                    "ORDER BY departure ASC "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(sql, (g.property["id"], g.user["id"], arrival_date))
                    prior_month_stays = cursor.fetchall()
                if (
                    prior_month_stays
                    and len(prior_month_stays) + 1 > limits["max_per_month"]
                ):
                    next_available_arrival_date = prior_month_stays[0][
                        "departure"
                    ] + timedelta(31)
                    errors.append(
                        f"Number of reservations exceeds the monthly limit ({limits['max_per_month']}). Next "
                        f"available arrival date is {next_available_arrival_date.strftime('%A, %-m/%-e/%Y')}."
                    )

            if limits["max_per_year"]:
                sql = (
                    "SELECT * FROM reservation "
                    "WHERE status_id IN (1, 2) "
                    "AND property_id = %s "
                    "AND user_id = %s "
                    "AND departure >= %s - INTERVAL '365 DAYS' "
                    "ORDER BY departure ASC "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(sql, (g.property["id"], g.user["id"], arrival_date))
                    prior_year_stays = cursor.fetchall()
                if (
                    prior_year_stays
                    and len(prior_year_stays) + 1 > limits["max_per_year"]
                ):
                    next_available_arrival_date = prior_year_stays[0][
                        "departure"
                    ] + timedelta(366)
                    errors.append(
                        f"Number of reservations exceeds the yearly limit ({limits['max_per_year']}). Next "
                        f"available arrival date is {next_available_arrival_date.strftime('%A, %-m/%-e/%Y')}."
                    )

            if limits["max_days_in_advance"]:
                days_til_reservation = arrival_date - datetime.now().date()
                if days_til_reservation.days > limits["max_days_in_advance"]:
                    nearest_available_arrival = datetime.now().date() + timedelta(
                        limits["max_days_in_advance"]
                    )
                    errors.append(
                        f"You are trying to book a reservation too far in advance. Please choose an arrival date "
                        f"on or before {nearest_available_arrival.strftime('%A, %-m/%-e/%Y')}."
                    )

            if limits["min_days_between"]:
                sql = (
                    "SELECT * FROM reservation "
                    "WHERE status_id IN (1, 2) "
                    "AND property_id = %s "
                    "AND user_id = %s "
                    "AND ((departure > %s - INTERVAL '%s DAYS') "
                    "OR (arrival < %s + INTERVAL '%s DAYS')) "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            g.property["id"],
                            g.user["id"],
                            arrival_date,
                            limits["min_days_between"],
                            departure_date,
                            limits["min_days_between"],
                        ),
                    )
                    if cursor.fetchone():
                        errors.append(
                            f"The reservation you are trying to book is too close to one or more of your upcoming, "
                            f"pending, or past reservations. Please choose different departure and arrival dates so "
                            f"that there are at least {limits['min_days_between']} days between the reservation you "
                            f"are trying to book and your existing reservation(s)."
                        )

        if errors:
            for error in errors:
                flash(error)
            booked_dates = get_booked_dates(get_db())
            return render_template("dashboard/book.jinja2", booked_dates=booked_dates)

        if limits and limits["is_owner_confirmation_required"]:
            reservation_status_id = 2
        else:
            reservation_status_id = 1    
 
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

        return redirect(url_for("dashboard.book_success", reservation=reservation_id))

    booked_dates = get_booked_dates(get_db())
    return render_template("dashboard/book.jinja2", booked_dates=booked_dates)


@bp.route("/book/success")
@login_required
def book_success():
    # return "Congrats on booking your vacation! You will receive an email confirmation when you're approved."
    # check if user can access other users's confirmations
    return render_template("dashboard/book_success.jinja2")
