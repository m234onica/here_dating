import os

mysql = {
    "username": "",
    "password": "",
    "host": "",
    "database": "",
}

class Config:
    DEBUG = True
    # your cecret key
    SECRET_KEY = ''
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')

    JSON_AS_ASCII = False
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_POOL_RECYCLE = 5

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}?charset=utf8mb4".format(
        USER=mysql["username"],
        PASSWORD=mysql["password"],
        HOST=mysql["host"],
        DATABASE=mysql["database"]
    )

    # 尋找配對的時間到期
    EXPIRED_TIME = 1

    # 配對聊天的時間到期
    END_TIME = 3

    # 可在 Messenger setting 取得
    APP_ID = ""
    PAGE_ACCESS_TOKEN = ""

    # 用在驗證webhook
    PAGE_VERIFY_TOKEN = ""

    FB_API_URL = "https://graph.facebook.com/v6.0"

    # front-end call api's url
    BASE_URL = ""

    # webview link
    STATIC_URL = ""
