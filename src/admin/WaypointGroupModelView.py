from src import AuthenticatedModelView


class WaypointGroupModelView(AuthenticatedModelView):
    """Waypoint model admin view"""
    form_widget_args = {
        'waypoints': {
            'disabled': True
        },
    }
