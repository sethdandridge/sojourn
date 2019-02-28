from flask import Blueprint, redirect, session, url_for

from ..db import get_db
from . import bp, login_required


@bp.route("/logout", strict_slashes=False)
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))
