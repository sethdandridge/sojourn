import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from fortnite.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/register')

@bp.route('/', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name'] 
        last_name = request.form['last_name']
        db = get_db()
        
        error = None
        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not first_name:
            error = 'First name is required.'
        elif not last_name:
            error = 'Last name is required.'
        elif db.execute(
            'SELECT id from user WHERE email = ?', (email,)
        ).fetchone():
            error = f'Email {email} is already registered'

        if error is None:
            db.execute(
                'INSERT INTO user (email, password, first_name, last_name) VALUES (?, ?, ?, ?)',
                (email, generate_password_hash(password), first_name, last_name)
            )
            db.commit()
 
            return redirect(url_for('login.login'))

        flash(error)

    return render_template('register/register.jinja2')
