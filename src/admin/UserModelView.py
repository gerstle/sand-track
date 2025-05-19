from src import AuthenticatedModelView


class UserModelView(AuthenticatedModelView):
    """Waypoint model admin view"""
    form_excluded_columns = ("password",)
    list_columns = ("name", "email")
