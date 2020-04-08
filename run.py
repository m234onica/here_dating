import time
from flask import g
from src import create_app
from src.tool import message
from src.db import db_session

app = create_app()
BASE_URL = app.config.get("BASE_URL")
APP_ID = app.config.get("APP_ID")

@app.context_processor
def url():
    return {
        "base_url": g.url, 
        "version": g.version,
        "app_id": g.app_id
        }


@app.before_request
def before_req():
    g.url = BASE_URL
    g.app_id = APP_ID
    g.version = time.time()


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == "__main__":
    start = message.get_started()
    app.run()
