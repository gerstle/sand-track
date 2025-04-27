from src import AuthenticatedModelView


class TaskModelView(AuthenticatedModelView):
    """Task Model Admin View"""
    form_widget_args = {
        'turnpoints': {
            'disabled': True
        },
        'entries': {
            'disabled': True
        },
    }
