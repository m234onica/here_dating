from flask import g, render_template
from flask_cors import CORS

from src import create_app
from src.tool import message
from src.db import init_db, db_session
from src.models import Place

app = create_app()

@app.teardown_request
def session_clear(exception):
    db_session.remove()


@app.before_first_request
def seed():
    init_db()
    place_count = Place.query.filter().count()
    if place_count == 0:
        db_session.add(Place(
            id="1111",
            name="木木卡的黑店",
            longitude="25.066765",
            latitude="121.526336"
        ))
        db_session.commit()


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
