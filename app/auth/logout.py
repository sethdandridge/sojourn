from flask import Blueprint, redirect, session, url_for, current_app, g

from ..db import get_db
from . import bp, login_required


@bp.route("/logout", strict_slashes=False)
@login_required
def logout():
    current_app.logger.info(f'{g.user["id"]} ({g.user["email"]}) logged out')
    session.clear()
    return redirect(url_for("index"))
