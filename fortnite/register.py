from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint("register", __name__, url_prefix="/register")


@bp.route("/", methods=("GET", "POST"), strict_slashes=False)
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        db = get_db()
        cursor = db.cursor()
        error = None
        if not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        
        if not error:
            with get_db().cursor() as cursor:
                cursor.execute('SELECT * from "user" WHERE email ILIKE %s;', (email,))
                if cursor.fetchone():
                    error = f"This email is already registered to a user. Did you forget your password?" 

        if error is None:
            sql = (
                'INSERT INTO "user" (email, password, first_name, last_name) '
                "VALUES (%s, %s, %s, %s) RETURNING id"
            )
            with db.cursor() as cursor:
                cursor.execute(
                    sql,
                    (email, generate_password_hash(password), first_name, last_name),
                )
                user_id = cursor.fetchone()["id"]

            # if there are any invites, move them over
            sql_move_property_association = (
                "INSERT INTO user_to_property "
                "(user_id, property_id) "
                "SELECT %s, property_id "
                "FROM invite "
                "WHERE invite.email ILIKE %s; "
            )
            sql_move_rules = (
                "INSERT INTO user_to_property_reservation_limits "
                "(user_id, property_id, max_upcoming, max_duration, max_per_month, max_per_year, "
                "max_days_in_advance, min_days_between, is_owner_presence_required, is_owner_confirmation_required) "
                "SELECT %s, property_id, max_upcoming, max_duration, max_per_month, max_per_year, "
                "max_days_in_advance, min_days_between, is_owner_presence_required, is_owner_confirmation_required "
                "FROM invite_reservation_limits "
                "JOIN invite ON invite.id = invite_reservation_limits.invite_id "
                "WHERE invite.email ILIKE %s; "
            )
            sql_delete_invite =  (
                "DELETE FROM invite WHERE email ILIKE %s; "
            )
            with get_db().cursor() as cursor:
                cursor.execute(sql_move_property_association, (user_id, email))
                cursor.execute(sql_move_rules, (user_id, email))
                cursor.execute(sql_delete_invite, (email,))
                
            session["user_id"] = user_id
            print(url_for("register.register"))
            return redirect(url_for("dashboard.index"))

        flash(error)

    return render_template("register/register.jinja2")
