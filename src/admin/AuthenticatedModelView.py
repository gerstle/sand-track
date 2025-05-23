import logging

from flask import redirect, url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

logger = logging.getLogger(__name__)

class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.index"))