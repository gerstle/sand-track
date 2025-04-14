import logging

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.getLogger('src.tasks').setLevel(logging.INFO)

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    db.init_app(app)
    Migrate(app, db)
    Bootstrap5(app)

    # load models/DB
    from src.models import user, waypoint_group, waypoint, task, turnpoint, entry

    # load auth and routes
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from .auth import auth_bp
    from .main import main_bp
    from .tasks import tasks_bp
    from .setup import setup_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(setup_bp)

    return app
