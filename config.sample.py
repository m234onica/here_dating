import os

DEBUG = True

SECRET_KEY = ''
FLASK_APP = os.environ.get('FLASK_APP')
FLASK_ENV = os.environ.get('FLASK_ENV')

JSON_AS_ASCII = False
TEMPLATES_AUTO_RELOAD = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{passwword}@{host}/{db_name}'
BASE_URL = ""
