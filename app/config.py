import os

class Config(object):
    DEBUG = False
    TESTING = False
    APP_NAME = "Sojourn"
    DATABASE="dbname=book_app"
    APP_URL = "https://sojourn.house"
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('FLASK_SECURITY_PASSWORD_SALT')
    AWS_SES_ACCESS_KEY_ID = os.getenv('AWS_SES_ACCESS_KEY_ID')
    AWS_SES_SECRET_ACCESS_KEY = os.getenv('AWS_SES_SECRET_ACCESS_KEY')
    
class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    APP_NAME = "Sojourn (Dev)"
    DEBUG = True
    DEBUG_MAIL_RECIPIENT = 'sethdan@gmail.com'

class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "testkey"
    SECURITY_PASSWORD_SALT = "passwordsalt"
    DATABASE = "dbname=fortnite_test" 
