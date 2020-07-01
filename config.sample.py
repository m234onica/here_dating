
import os

mysql = {
    "username": "",
    "password": "",
    "host": "",
    "database": "",
}

class Config:
    def url_trailing_slash(url: str):
        if not url.endswith("/"):
            return url + "/"
        return url

    # delete timing
    EXPIRED_TIME = 2
    END_TIME = 3
    RESET_PAIRING_TIME = 15

    DEBUG = True

    # here_dating messenger settings
    PAGE_VERIFY_TOKEN = ""
    PAGE_ACCESS_TOKEN = ""
    BASE_URL = url_trailing_slash("")
    STATIC_URL = url_trailing_slash("")

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{NAME}?charset=utf8mb4".format(
        USER=mysql["username"],
        PASSWORD=mysql["password"],
        HOST=mysql["host"],
        NAME=mysql["database"]
    )
