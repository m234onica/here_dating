
import werkzeug.datastructures
from flask_cors import CORS

from src import create_app
from src.db import db_session
from src.tool import message

app = create_app()
start = message.get_started()

CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.teardown_request
def session_clear(exception):
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
