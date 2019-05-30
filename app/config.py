import os

class Config(object):
    DEBUG = False
    TESTING = False
    APP_NAME = "Sojourn"
    APP_URL = "https://sojourn.house"
    DATABASE="dbname=book_app"
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('FLASK_SECURITY_PASSWORD_SALT')

    AWS_SES_ACCESS_KEY_ID = "AKIAV3IRXMPZ4CK5XCTF"
    AWS_SES_SECRET_ACCESS_KEY = "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"

class ProductionConfig(Config):
    PORT = 7000

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    #MAIL_DEBUG = False
