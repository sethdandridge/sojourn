import re

from flask import flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

#from flask import g

from ..db import get_db
from . import bp
from . import admin_required


@bp.route("/log")
@admin_required
def log():
    sql = (
        "SELECT TO_CHAR(logged, 'Dy FMMM/FMDD/YY') AS log_date, "
        " * FROM property_log "
        'JOIN "user" ON "user".id = property_log.user_id '
        'WHERE property_log.property_id = %s '
        'ORDER BY logged DESC; '
    )
    with get_db().cursor() as cursor:
        cursor.execute(sql, (g.property['id'],))
        results = cursor.fetchall()

    log_rows = [] 
    for result in results:
        log_row = {}
        log_row['user_id'] = result['user_id']
        log_row['name'] = result['first_name'] + " " + result['last_name']
  
        log_row['date'] = result['log_date']
        log_row['message'] = result['message']
        log_rows.append(log_row)
 
    return render_template('admin/log.jinja2', log_rows=log_rows)
