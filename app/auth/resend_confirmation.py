from flask import render_template, g, current_app

from ..email import mail_registration_confirmation
from . import bp
from . import login_required

@bp.route("/confirm/resend")
@login_required
def resend_confirmation():
    mail_registration_confirmation(g.user['id'])
    current_app.logger.info(f'{g.user["id"]} ({g.user["email"]}) resent email confirmation')
    return render_template("auth/resend_confirmation.jinja2")
