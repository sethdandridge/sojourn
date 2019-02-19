from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from ..login import login_required
from ..db import get_db
from . import bp
from . import admin_required

@bp.route("/guests")
@login_required
@admin_required
def guests():
    db = get_db()
    guests = db.execute(
        "SELECT * FROM user "
        "JOIN user_to_property ON user_to_property.user_id = user.id "
        "WHERE user_to_property.property_id = ?; ",
        (g.property['id'],)
    ).fetchall()
    return render_template("admin/guests.jinja2", guests=guests)

@bp.route("/guests/edit/<int:guest_id>", methods=("GET", "POST"))
@login_required
@admin_required
def edit_guest(guest_id):
    db = get_db()
    if request.method == "POST":
        is_admin_input = request.form.get('is_admin')
        note_input = request.form.get('note')

        error = None
        if guest_id == g.user['id']:
            error = "You cannot edit yourself."

        if is_admin_input == '1':
            is_admin = 1
        else:
            is_admin = 0

        if error:
            flash(error)
            return redirect(url_for('admin.edit_guest', guest_id=guest_id)) 

        if note_input and note_input.strip():
            note = note_input.strip()
        else:
            note = None

        db.execute(
            "UPDATE user_to_property "
            "SET is_admin = ?, "
            "note = ? "
            "WHERE user_id = ? "
            "AND property_id = ?; ",
            (is_admin, note, guest_id, g.property['id'],)
        )
        db.commit()

        return redirect(url_for('admin.guests'))

    guest = db.execute(
        "SELECT * FROM user "
        "JOIN user_to_property ON user_to_property.user_id = user.id "
        "WHERE user_to_property.property_id = ? "
        "AND user.id = ? ",
        (g.property['id'], guest_id,)
    ).fetchone()

    return render_template("admin/edit_guest.jinja2", guest=guest)

@bp.route("/guests/invite", methods=("GET", "POST"))
@login_required
@admin_required
def invite_guest():
    db = get_db()
    if request.method == "POST":
        email = request.form.get('email')

        error = None
        if not email:
            error = "Please enter the email address of the guest you wish to invite."

        if db.execute(
            "SELECT * FROM user "
            "JOIN user_to_property ON user_to_property.user_id = user.id "
            "WHERE user_to_property.property_id = ? "
            "AND user.email = ? ",
            (g.property['id'], email,)
        ).fetchone():
            error = "User is already a guest at this property."

        if db.execute(
            "SELECT * FROM invite " 
            "WHERE invite.property_id = ? "
            "AND invite.email = ? ",
            (g.property['id'], email,)
        ).fetchone():
            error = "Invite has already been sent to this user."

        if error:
            flash(error)
        else:
            user = db.execute(
                "SELECT * FROM user "
                "WHERE user.email = ?; ",
                (email,)
            ).fetchone()

            if user:
                db.execute(
                    "INSERT INTO user_to_property "
                    "(user_id, property_id) "
                    "VALUES "
                    "(?, ?); ",
                    (user['id'], g.property['id'],)
                ) 
            else:
                db.execute(
                    "INSERT INTO invite "
                    "(email, property_id) "
                    "VALUES "
                    "(?, ?); ",
                    (user['id'], g.property['id'],)
                )

            db.commit()

            flash(f"Invited {email}")
            return redirect(url_for('admin.guests'))

    return render_template("admin/invite_guest.jinja2")
