from src import AuthenticatedModelView, Turnpoint, Entry


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
    inline_models = (Turnpoint, Entry)
