import os

class Config:
    DEBUG = True

    SECRET_KEY = ''
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')

    JSON_AS_ASCII = False
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    USER = ""
    PASSWORD = ""
    HOST = ""
    PORT = ""
    NAME = ""

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}?charset=utf8mb4".format(
        USER=USER, PASSWORD=PASSWORD, HOST=HOST, PORT=PORT, NAME=NAME)

    BASE_URL = ""

    # delete timing
    EXPIRED_TIME = 1
    END_TIME = 3

    # Facebook messenger
    APP_ID = ""
    PAGE_ACCESS_TOKEN = ""
    PAGE_VERIFY_TOKEN = ""
    FB_API_URL = "https://graph.facebook.com/v6.0"

    BASE_URL = ""
    STATIC_URL = ""
