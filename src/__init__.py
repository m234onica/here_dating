from flask import Flask

from src.route.api import api
from src.route.webview import webview

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object("config")

    app.register_blueprint(api)
    app.register_blueprint(webview)
    
    return app
