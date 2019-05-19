import os

class Config(object):
    DEBUG = False
    TESTING = False
    APP_NAME = "Sojourn"
    DATABASE="dbname=book_app"
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('FLASK_SECURITY_PASSWORD_SALT')
    MAIL_SERVER = 'email-smtp.us-east-1.amazonaws.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'AKIAV3IRXMPZ3MJ2V4CL'
    MAIL_PASSWORD = 'BMaed9HZGH+DVHp0aJjJh64xiTKFn4fmtwgBJQTDWxR3'
    MAIL_DEBUG = False

#class ProductionConfig(Config):
#    DATABASE_U = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    MAIL_DEBUG = False
