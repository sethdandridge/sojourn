from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort

from ..login import login_required
from ..db import get_db
from . import bp

@bp.route("/switch_property/<int:property_id>")
@login_required
def switch_property(property_id):
    db = get_db()
    # double check to make sure user has access to property (g.property logic does this as well)
    results = db.execute(
        "SELECT * FROM user_to_property "
        "WHERE property_id = ? AND user_id = ?;",
        (property_id, g.user['id'])
    ).fetchone()
    if not results: 
        abort(401)

    session['active_property_id'] = property_id

    if request.referrer:
        return redirect(request.referrer)
    else:
        return redirect(url_for('dashboard.index'))
