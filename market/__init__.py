from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'hihi'

    @app.route('/detail')
    def detail():
        return render_template('detail.html', product=None)

    return app

