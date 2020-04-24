from flask import g, render_template
from flask_cors import CORS

from src import create_app
from src.tool import message
from src.db import db_session

app = create_app()

@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()


@app.route("/pair", methods=["GET"])
def intro_page():
    return render_template("pair.html")


@app.route("/wait", methods=["GET"])
def wait_page():
    return render_template("wait.html")


@app.route("/message", methods=["GET"])
def message_page():
    return render_template("message.html")


@app.route("/rule", methods=["GET"])
def rule_page():
    return render_template("rule.html")


if __name__ == "__main__":
    start = message.get_started()
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.run()
