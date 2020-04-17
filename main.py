import werkzeug.datastructures
import time
from flask import g

from src import create_app
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


def main(request):
    print(request)
    with app.app_context():
        headers = werkzeug.datastructures.Headers()
        for key, value in request.headers.items():
            headers.add(key, value)
        with app.test_request_context(method=request.method, base_url=request.base_url, path=request.path, query_string=request.query_string, headers=headers, data=request.data):
            try:
                rv = app.preprocess_request()
                if rv is None:
                    rv = app.dispatch_request()
            except Exception as e:
                rv = app.handle_user_exception(e)
            response = app.make_response(rv)
            return app.process_response(response)
