import os
from flask import Flask, g, session

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True) 

    app.config.from_object('app.config.DevelopmentConfig')

    if test_config:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import email
    email.init_mail(app)

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp) 

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule("/", endpoint="index")

    from . import admin
    app.register_blueprint(admin.bp, url_prefix="/admin")

    @app.route("/nadia")
    def nadia():
        return "Hello nadia"

    return app
