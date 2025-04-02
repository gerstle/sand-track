from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    db.init_app(app)
    Migrate(app, db)
    Bootstrap5(app)

    from src.models import user, task, turnpoint

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return user.User.query.get(int(user_id))

    from .auth import auth
    from .main import main
    from .tasks import tasks
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(tasks)

    return app
