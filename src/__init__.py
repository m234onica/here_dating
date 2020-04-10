from flask import Flask
from flask_cors import CORS

from src.route.api import api
from src.route.bot import bot

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.url_map.strict_slashes = False
    app.config.from_object("config")

    app.register_blueprint(api)
    app.register_blueprint(bot)
    
    return app
