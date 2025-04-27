import datetime
import logging
import os
from logging.config import dictConfig

import toml
from flask import Flask
from flask_admin import Admin
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_migrate import Migrate
from tzlocal import get_localzone

from src.admin.AuthenticatedModelView import AuthenticatedModelView
from src.admin.TaskModelView import TaskModelView
from src.admin.UserModelView import UserModelView
from src.admin.WaypointGroupModelView import WaypointGroupModelView
from src.db import db
from src.models.entry import Entry
from src.models.task import Task
from src.models.turnpoint import Turnpoint
from src.models.user import User
from src.models.waypoint import Waypoint
from src.models.waypoint_group import WaypointGroup

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

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

    admin = Admin(app, name="Sand Track")
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(WaypointGroupModelView(WaypointGroup, db.session, category="Waypoints"))
    admin.add_view(AuthenticatedModelView(Waypoint, db.session, category="Waypoints"))
    admin.add_view(TaskModelView(Task, db.session, category="Task"))
    admin.add_view(AuthenticatedModelView(Turnpoint, db.session, category="Task"))
    admin.add_view(AuthenticatedModelView(Entry, db.session, category="Task"))

    return app


def inject():
    version = "-"
    pyproject_toml_file = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    if os.path.exists(pyproject_toml_file) and os.path.isfile(pyproject_toml_file):
        data = toml.load(pyproject_toml_file)
        version = data["project"]["version"]

    return {
        "now": datetime.datetime.now(datetime.timezone.utc).astimezone(get_localzone()),
        "version": version
    }
