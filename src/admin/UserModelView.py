from src import AuthenticatedModelView


class UserModelView(AuthenticatedModelView):
    """Waypoint model admin view"""
    form_excluded_columns = ("password",)
    column_list = ("name", "email")
