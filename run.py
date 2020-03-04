from flask import g, current_app
from src import create_app

app = create_app()
BASE_URL = app.config.get('BASE_URL')

@app.context_processor
def url():
    return {'base_url': g.url}


@app.before_request
def before_req():
    g.url = BASE_URL

if __name__ == '__main__':
    app.run()
