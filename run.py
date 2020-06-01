from flask import g, render_template
from flask_cors import CORS

from src import create_app
from src.tool import message
from src.db import db_session

app = create_app()

@app.teardown_request
def session_clear(exception=None):
    db_session.remove()
    if exception and db_session.is_active:
        db_session.rollback()


@app.route("/pair.html", methods=["GET"])
def intro_page():
    return render_template("pair.html")


@app.route("/wait.html", methods=["GET"])
def wait_page():
    return render_template("wait.html")


@app.route("/message.html", methods=["GET"])
def message_page():
    return render_template("message.html")


@app.route("/rule.html", methods=["GET"])
def rule_page():
    return render_template("rule.html")


if __name__ == "__main__":
    start = message.get_started()
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.run()
