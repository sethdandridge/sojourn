from flask import Blueprint, g, redirect, render_template, session
from werkzeug.exceptions import abort
import functools

from ..login import login_required
from ..db import get_db


def admin_required(view):
    @login_required
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.property["is_admin"]:
            abort(401)
        return view(**kwargs)

    return wrapped_view


bp = Blueprint("admin", __name__)

from . import guests
