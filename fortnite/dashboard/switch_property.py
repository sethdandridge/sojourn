from flask import redirect, url_for, session, g, request
from werkzeug.exceptions import abort

from ..login import login_required
from ..db import get_db
from . import bp


@bp.route("/switch_property/<int:property_id>")
@login_required
def switch_property(property_id):
    # double check  user is a guest of property (g.property logic does this as well)
    sql = "SELECT * FROM user_to_property WHERE property_id = %s AND user_id = %s; "
    with get_db().cursor() as cursor:
        cursor.execute(sql, (property_id, g.user["id"]))
        results = cursor.fetchone()

    if not results:
        abort(401)

    session["active_property_id"] = property_id

    if request.referrer and 'admin' not in request.referrer:
        return redirect(request.referrer)
    else:
        return redirect(url_for("dashboard.index"))
