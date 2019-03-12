import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request
from flask.logging import default_handler

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

    # logging stuff
    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.path = request.path
            record.remote_addr = request.remote_addr
            return super().format(record)

    formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s %(path)s %(levelname)s %(module)s %(message)s'
    )
    rotating_file_handler = RotatingFileHandler(
        app.instance_path + '/log.txt',
        maxBytes = 1024 * 1024 * 10, #10 megabytes
        backupCount = 10
    )
    rotating_file_handler.setFormatter(formatter)
    app.logger.addHandler(rotating_file_handler)
    app.logger.removeHandler(default_handler)

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
        app.logger.info('Someone visited the Nadia page') 
        return "Hello nadia"

    return app
