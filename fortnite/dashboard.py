from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from fortnite.login import login_required
from fortnite.db import get_db

bp = Blueprint("dashboard", __name__)


@bp.route("/")
@login_required
def index():
    return render_template("dashboard/index.jinja2")


@bp.route("/book")
@login_required
def book(methods=("GET", "POST")):
    return render_template("dashboard/book.jinja2")
