from flask import (
    Blueprint, redirect, session, url_for
)

from fortnite.db import get_db
from fortnite.login import login_required

bp = Blueprint('logout', __name__, url_prefix='/logout')

@bp.route('/')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))
