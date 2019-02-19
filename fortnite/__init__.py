import os
from flask import Flask, g, session


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="corgiOrgy",
        DATABASE=os.path.join(app.instance_path, "fortnite.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        print("trying to load config")
    else:
        # load the test config if passed in
        print("didnt loads config")
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import register
    app.register_blueprint(register.bp)

    from . import login
    app.register_blueprint(login.bp)

    from . import logout
    app.register_blueprint(logout.bp)

    from . import dashboard
    app.register_blueprint(dashboard.bp)
    app.add_url_rule("/", endpoint="index")

    from . import admin
    app.register_blueprint(admin.bp, url_prefix="/admin")

    @app.route("/nadia")
    def nadia():
        return "Hello nadia"

    return app
