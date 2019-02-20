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
            is_admin = True
        else:
            is_admin = False

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
        max_upcoming = request.form.get('max_upcoming') 
        max_duration = request.form.get('max_duration')
        max_per_month = request.form.get('max_per_month')
        max_per_year = request.form.get('max_per_year')
        max_days_in_advance = request.form.get('max_days_in_advance')
        min_days_between = request.form.get('min_days_between')
        is_owner_presence_required = request.form.get('is_owner_presence_required')
        is_owner_confirmation_required = request.form.get('is_owner_confirmation_required')


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
                    (email, g.property['id'],)
                )

            db.commit()

            flash(f"Invited {email}" + str(request.form))
            return redirect(url_for('admin.guests'))

    return render_template("admin/invite_guest.jinja2")

@bp.route("/guests/invites", methods=("GET", "POST"))
@login_required
@admin_required
def invites():
    db = get_db()
    invites = db.execute(
        "SELECT * FROM invite "
        "WHERE invite.property_id = ?; ",
        (g.property['id'],)
    ).fetchall()
    return render_template('admin/invites.jinja2', invites=invites)


@bp.route("/guests/remove/<int:guest_id>", methods=("GET", "POST"))
@login_required
@admin_required
def remove_guest(guest_id):
    db = get_db()
    if request.method == "POST":

        db.execute(
            "UPDATE reservation "
            "SET status_id = 4 "
            "WHERE user_id = ? "
            "AND property_id = ? "
            "AND departure >= DATE('now'); ",
            (guest_id, g.property['id'],),
        )
        db.commit()

        db.execute(
            "DELETE FROM user_to_property "
            "WHERE user_id = ? "
            "AND property_id = ?; ",
            (guest_id, g.property['id'],),
        )
        db.commit()

        # user is deleting themselves
        if g.user['id'] == guest_id:
            return redirect(url_for('dashboard.index'))
        
        return redirect(url_for('admin.guests'))

    guest = db.execute(
        "SELECT * FROM user "
        "JOIN user_to_property ON user_to_property.user_id = user.id "
        "WHERE user_to_property.property_id = ? "
        "AND user.id = ? ",
        (g.property['id'], guest_id,),
    ).fetchone()
    return render_template('admin/remove_guest.jinja2', guest=guest)
    
