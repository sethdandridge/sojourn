from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from fortnite.login import login_required
from fortnite.db import get_db

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    db = get_db()
    users = db.execute("SELECT * FROM user;").fetchall()
    return_string = ""
    for user in users:
        for key in user.keys():
            return_string += f"{key}: {user[key]} "
        return_string += "<br />"
    return return_string
