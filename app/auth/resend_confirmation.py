from flask import render_template, g

from ..email import mail_registration_confirmation
from . import bp
from . import login_required

@bp.route("/confirm/resend")
@login_required
def resend_confirmation():
    mail_registration_confirmation(g.user['id'])
    return render_template("auth/resend_confirmation.jinja2")
