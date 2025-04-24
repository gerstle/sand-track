import datetime
import logging
import os
import toml
from logging.config import dictConfig

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from tzlocal import get_localzone

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARN)

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    dictConfig({
        "version": 1,
        "formatters": {"default": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        }},
        "handlers": {"wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default"
        }},
        "root": {
            "level": "INFO",
            "handlers": ["wsgi"]
        }
    })
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    app.config.from_pyfile("config.py")
    app.context_processor(inject)

    db.init_app(app)
    Migrate(app, db)
    Bootstrap5(app)

    # load models/DB
    from src.models import user, waypoint_group, waypoint, task, turnpoint, entry

    # load auth and routes
    login_manager.login_view = "auth.login"
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


def inject():
    version = "-"
    pyproject_toml_file = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    if os.path.exists(pyproject_toml_file) and os.path.isfile(pyproject_toml_file):
        data = toml.load(pyproject_toml_file)
        version = data["project"]["version"]

    return {
        'now': datetime.datetime.now(datetime.timezone.utc).astimezone(get_localzone()),
        'version': version
    }
