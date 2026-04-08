from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    BASE_DIR = os.path.dirname(__file__)

    db_path = os.path.abspath(os.path.join(BASE_DIR, '..', 'market.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models

    # 블루프린트
    from .views import main_view
    app.register_blueprint(main_view.bp)


    return app