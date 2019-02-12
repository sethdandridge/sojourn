import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from fortnite.login import login_required
from fortnite.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['is_admin']:
            return 'ACCESS DENIED'

        return view(**kwargs)

    return wrapped_view

@bp.route('/')
@login_required
@admin_required
def admin():
    return 'welcome to the admin screen'
