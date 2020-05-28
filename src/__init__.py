from flask import Flask

from config import Config

from src.route.api import api
from src.route.bot import bot

def create_app():
    app = Flask(__name__, template_folder="./../static/templates/")
    app.url_map.strict_slashes = False
    app.config.from_object(Config)

    app.register_blueprint(api)
    app.register_blueprint(bot)
    
    return app
