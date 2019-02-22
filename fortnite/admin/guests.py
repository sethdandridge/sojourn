import re

from flask import flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ..login import login_required
from ..db import get_db
from . import bp
from . import admin_required


@bp.route("/guests")
@admin_required
def guests():
    sql = (
        'SELECT * FROM "user"  '
        'JOIN user_to_property ON user_to_property.user_id = "user".id '
        "WHERE user_to_property.property_id = %s; "
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.property["id"],))
        guests = cursor.fetchall()

    return render_template("admin/guests.jinja2", guests=guests)


@bp.route("/guests/edit/<int:guest_id>", methods=("GET", "POST"))
@admin_required
def edit_guest(guest_id):
    if request.method == "POST":
        is_admin_input = request.form.get("is_admin")
        note_input = request.form.get("note")

        error = None
        if guest_id == g.user["id"]:
            error = "You cannot edit yourself."

        if is_admin_input == "1":
            is_admin = True
        else:
            is_admin = False

        if error:
            flash(error)
            return redirect(url_for("admin.edit_guest", guest_id=guest_id))

        if note_input and note_input.strip():
            note = note_input.strip()
        else:
            note = None

        sql = (
            "UPDATE user_to_property "
            "SET is_admin = %s, "
            "note = %s "
            "WHERE user_id = %s "
            "AND property_id = %s; "
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql, (is_admin, note, guest_id, g.property["id"]))

        return redirect(url_for("admin.guests"))

    sql = (
        'SELECT * FROM "user" '
        'JOIN user_to_property ON user_to_property.user_id = "user".id '
        "WHERE user_to_property.property_id = %s "
        'AND "user".id = %s '
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.property["id"], guest_id))
        guest = cursor.fetchone()

    return render_template("admin/edit_guest.jinja2", guest=guest)


@bp.route("/guests/remove/<int:guest_id>", methods=("GET", "POST"))
@admin_required
def remove_guest(guest_id):
    if request.method == "POST":
        error = None
        if guest_id == g.property["owner_user_id"]:
            error = "HEY! You are not allowed to remove the property owner's account."
        if error:
            flash(error)
        else:
            # cancel all future reservations and remove guest
            sql_cancel_rezzies = (
                "UPDATE reservation "
                "SET status_id = 4 "
                "WHERE user_id = %s "
                "AND property_id = %s "
                "AND departure >= NOW(); "
            )
            sql_remove_reservation_limits = (
                "DELETE FROM user_to_property_reservation_limits "
                "WHERE user_id = %s"
                "AND property_id = %s; "
            )
            sql_remove_guest = (
                "DELETE FROM user_to_property "
                "WHERE user_id = %s "
                "AND property_id = %s; ",
            )
            with get_db().cursor() as cursor:
                cursor.execute(sql_cancel_rezzies, (guest_id, g.property["id"]))
                cursor.execute(sql_remove_reservation_limits, (guest_id, g.property["id"]))
                cursor.execute(sql_remove_guest, (guest_id, g.property["id"]))

            # user is deleting themselves
            if g.user["id"] == guest_id:
                return redirect(url_for("dashboard.index"))

        return redirect(url_for("admin.guests"))

    sql = (
        'SELECT * FROM "user" '
        'JOIN user_to_property ON user_to_property.user_id = "user".id '
        "WHERE user_to_property.property_id = %s "
        'AND "user".id = %s; '
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.property["id"], guest_id))
        guest = cursor.fetchone()

    return render_template("admin/remove_guest.jinja2", guest=guest)


def validate_reservation_limits(form):
    errors = []
    max_upcoming = form.get("max_upcoming", "").strip()
    max_duration = form.get("max_duration", "").strip()
    max_per_month = form.get("max_per_month", "").strip()
    max_per_year = form.get("max_per_year", "").strip()
    max_days_in_advance = form.get("max_days_in_advance", "").strip()
    min_days_between = form.get("min_days_between", "").strip()

    if max_upcoming:
        if not max_upcoming.isdigit() or int(max_upcoming) < 0 or int(max_upcoming) > 2_147_483_647:
            errors.append("Invalid Max Upcoming Stays. Please enter a reasonable number of stays.")

    if max_duration:
        if not max_duration.isdigit() or int(max_duration) < 0 or int(max_duration) > 2_147_483_647:
            errors.append(
                "Invalid Max Stay Duration. Please enter a reasonable number of days."
            )

    if max_per_month:
        if not max_per_month.isdigit() or int(max_per_month) < 0 or int(max_per_month) > 2_147_483_647:
            errors.append(           
                "Invalid Max Stays Per Month. Please enter a reasonable number of stays."
            )

    if max_per_year:
        if not max_per_year.isdigit() or int(max_per_year) < 0 or int(max_per_year) > 2_147_483_647:
            errors.append(
                "Invalid Max Stays Per Year. Please enter a reasonable number of stays."
            )

    if max_days_in_advance:
        if not max_days_in_advance.isdigit() or int(max_days_in_advance) < 0 or int(max_days_in_advance) > 2_147_483_647:
            errors.append(
                "Invalid Max Days In Advance. Please enter a reasonable number of days."
            )

    if min_days_between:
        if not min_days_between.isdigit() or int(min_days_between) < 0 or int(min_days_between) > 2_147_483_647:
            errors.append(
                "Invalid Minimum Nights Between Stays. Please enter a reasonable number of days."
            )

    return errors


def normalize_reservation_limits(form):
    reservation_limits = {}
    max_upcoming = form.get("max_upcoming", "").strip()
    max_duration = form.get("max_duration", "").strip()
    max_per_month = form.get("max_per_month", "").strip()
    max_per_year = form.get("max_per_year", "").strip()
    max_days_in_advance = form.get("max_days_in_advance", "").strip()
    min_days_between = form.get("min_days_between", "").strip()
    is_owner_presence_required = form.get("is_owner_presence_required", "").strip()
    is_owner_confirmation_required = form.get(
        "is_owner_confirmation_required", ""
    ).strip()

    reservation_limits["max_upcoming"] = int(max_upcoming) if max_upcoming else None
    reservation_limits["max_duration"] = int(max_duration) if max_duration else None
    reservation_limits["max_per_month"] = int(max_per_month) if max_per_month else None
    reservation_limits["max_per_year"] = int(max_per_year) if max_per_year else None
    reservation_limits["max_days_in_advance"] = (
        int(max_days_in_advance) if max_days_in_advance else None
    )
    reservation_limits["min_days_between"] = (
        int(min_days_between) if min_days_between else None
    )
    reservation_limits["is_owner_presence_required"] = (
        True if is_owner_presence_required else False
    )
    reservation_limits["is_owner_confirmation_required"] = (
        True if is_owner_confirmation_required else False
    )

    return reservation_limits


@bp.route("/guests/invite", methods=("GET", "POST"))
@admin_required
def invite_guest():
    if request.method == "POST":
        errors = validate_reservation_limits(request.form)
        email = request.form.get("email")

        if not email:
            errors.append(
                "Please enter the email address of the guest you wish to invite."
            )

        sql = (
            'SELECT * FROM "user" '
            'JOIN user_to_property ON user_to_property.user_id = "user".id '
            "WHERE user_to_property.property_id = %s "
            'AND "user".email LIKE %s '
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql, (g.property["id"], email))
            if cursor.fetchone():
                errors.append("User is already a guest at this property.")

        sql = (
            "SELECT * FROM invite "
            "WHERE invite.property_id = %s "
            "AND invite.email LIKE %s; "
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql, (g.property["id"], email))
            if cursor.fetchone():
                errors.append("Invite has already been sent to this user.")

        if errors:
            for error in errors:
                flash(error)
        else:
            reservation_limits = normalize_reservation_limits(request.form)

            sql = 'SELECT * FROM "user" WHERE "user".email LIKE %s;'
            with get_db().cursor() as cursor:
                cursor.execute(sql, (email,))
                guest = cursor.fetchone()

            if guest:
                sql = (
                    "INSERT INTO user_to_property "
                    "(user_id, property_id) "
                    "VALUES (%s, %s); "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(sql, (guest["id"], g.property["id"]))

                sql = (
                    "INSERT INTO user_to_property_reservation_limits "
                    "(user_id, property_id, max_upcoming, max_duration, max_per_month, "
                    "max_per_year, max_days_in_advance, min_days_between, "
                    "is_owner_presence_required, is_owner_confirmation_required) "
                    "VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s); "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            guest["id"],
                            g.property["id"],
                            reservation_limits["max_upcoming"],
                            reservation_limits["max_duration"],
                            reservation_limits["max_per_month"],
                            reservation_limits["max_per_year"],
                            reservation_limits["max_days_in_advance"],
                            reservation_limits["min_days_between"],
                            reservation_limits["is_owner_presence_required"],
                            reservation_limits["is_owner_confirmation_required"],
                        ),
                    )
            else:
                sql = (
                    "INSERT INTO invite (email, property_id) "
                    "VALUES (%s, %s) "
                    "RETURNING id "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(sql, (email, g.property["id"]))
                    invite_id = cursor.fetchone()["id"]

                sql = (
                    "INSERT INTO invite_reservation_limits "
                    "(invite_id, max_upcoming, max_duration, max_per_month, "
                    "max_per_year, max_days_in_advance, min_days_between, "
                    "is_owner_presence_required, is_owner_confirmation_required) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s); "
                )
                with get_db().cursor() as cursor:
                    cursor.execute(
                        sql,
                        (
                            invite_id,
                            reservation_limits["max_upcoming"],
                            reservation_limits["max_duration"],
                            reservation_limits["max_per_month"],
                            reservation_limits["max_per_year"],
                            reservation_limits["max_days_in_advance"],
                            reservation_limits["min_days_between"],
                            reservation_limits["is_owner_presence_required"],
                            reservation_limits["is_owner_confirmation_required"],
                        ),
                    )

            flash(f"Invited {email}")

            return redirect(url_for("admin.guests"))

    return render_template("admin/invite_guest.jinja2")


@bp.route("/guests/invites")
@admin_required
def invites():
    sql = "SELECT * FROM invite WHERE invite.property_id = %s;"
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.property["id"],))
        invites = cursor.fetchall()

    return render_template("admin/invites.jinja2", invites=invites)


@bp.route("/guests/invites/edit/<int:invite_id>", methods=("GET", "POST"))
@admin_required
def edit_invite(invite_id):
    if request.method == "POST":

        # Find any errors or auth issues
        errors = validate_reservation_limits(request.form)
        sql = "SELECT * FROM invite WHERE invite.id = %s;"
        with get_db().cursor() as cursor:
            cursor.execute(sql, (invite_id,))
            invite = cursor.fetchone()
        if not invite:
            errors.append("This invite does not exist.")
        elif invite["property_id"] != invite["property_id"]:
            errors.append("You do not have permission to edit this invite.")
        if errors:
            for error in errors:
                flash(error)
        else:
            # I guess we're okay? This is getting complicated.
            reservation_limits = normalize_reservation_limits(request.form)
            sql = (
                "UPDATE invite_reservation_limits "
                "SET "
                " max_upcoming = %s, "
                " max_duration = %s, "
                " max_per_month = %s, "
                " max_per_year = %s, "
                " max_days_in_advance = %s, "
                " min_days_between = %s, "
                " is_owner_presence_required = %s, "
                " is_owner_confirmation_required = %s "
                " WHERE invite_reservation_limits.invite_id = %s; "
            )
            with get_db().cursor() as cursor:
                cursor.execute(sql, 
                    (
                        reservation_limits["max_upcoming"],
                        reservation_limits["max_duration"],
                        reservation_limits["max_per_month"],
                        reservation_limits["max_per_year"],
                        reservation_limits["max_days_in_advance"],
                        reservation_limits["min_days_between"],
                        reservation_limits["is_owner_presence_required"],
                        reservation_limits["is_owner_confirmation_required"],
                        invite_id,
                    )
                )
            return redirect(url_for('admin.invites'))

    sql = (
        "SELECT * FROM invite "
        "JOIN invite_reservation_limits ON invite_reservation_limits.invite_id = invite.id "
        "WHERE invite.id = %s; "
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (invite_id,))
        invite = cursor.fetchone()
    if invite:
        return render_template("admin/edit_invite.jinja2", invite=invite)
    else:
        abort(404)


@bp.route("/guests/invites/remove/<int:invite_id>", methods=("GET", "POST"))
@admin_required
def remove_invite(invite_id):

    if request.method == "POST":
        sql = (
            "SELECT * FROM invite "
            "WHERE invite.id = %s "
            "AND invite.property_id = %s; "
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql, (invite_id, g.property['id']))
            has_access = cursor.fetchone()

        if not has_access:
            abort(401)

        sql_remove_invite = (
            "DELETE FROM invite "
            "WHERE id = %s; " 
        )
        sql_delete_invite_reservation_limits = (
            "DELETE FROM invite_reservation_limits "
            "WHERE invite_id = %s; "
        )
        with get_db().cursor() as cursor:
            cursor.execute(sql_delete_invite_reservation_limits, (invite_id,))
            cursor.execute(sql_remove_invite, (invite_id,))

        return redirect(url_for('admin.invites'))

    sql = (
        "SELECT * FROM invite "
        "WHERE invite.id = %s "
        "AND invite.property_id = %s; "
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (invite_id, g.property['id']))
        invite = cursor.fetchone()
    if invite: 
        return render_template("admin/remove_invite.jinja2", invite=invite)
    else:
        abort(404)
