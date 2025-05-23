from src import AuthenticatedModelView, Waypoint


class WaypointGroupModelView(AuthenticatedModelView):
    """Waypoint model admin view"""
    inline_models = (Waypoint,)
    form_widget_args = {
        'waypoints': {
            'disabled': True
        },
    }
