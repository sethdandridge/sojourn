import os

class Config(object):
    DEBUG = False
    TESTING = False
    APP_NAME = "Seth's Booking App"
    DATABASE="dbname=book_app"
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('FLASK_SECURITY_PASSWORD_SALT')
    MAIL_DEBUG = False

#class ProductionConfig(Config):
#    DATABASE_U = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    MAIL_DEBUG = True
