import time
from flask import g, current_app
from src import create_app
from src.tool import message
from config import EXPIRED_TIME, END_TIME
from src.db import db_session

app = create_app()
BASE_URL = app.config.get("BASE_URL")

@app.context_processor
def url():
    return {"base_url": g.url, "version": g.version}


@app.before_request
def before_req():
    db_session.remove()
    
    g.url = BASE_URL
    g.version = time.time()

if __name__ == "__main__":
    start = message.get_started()
    app.run()
