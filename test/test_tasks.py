import logging
import os
import unittest
from datetime import datetime

from src import tasks
from src.models.task import Task
from src.models.turnpoint import Turnpoint
from src.models.waypoint import Waypoint

base = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
igc_path = os.path.join(base, "examples", "sand-city-example-1.igc")

logger = logging.getLogger()
logger.level = logging.DEBUG

waypoints = {
    'SC-LAUNCH': Waypoint(
        name='SC-LAUNCH',
        lat=36.62526344882413,
        long=-121.844044848486,
        altitude=28.31566161661727,
    ),
    'BUNKERS': Waypoint(
        name='BUNKERS',
        lat=36.64303442014818,
        long=-121.8322100638915,
        altitude=24.21054577202324,
    ),
    'SK8-PARK': Waypoint(
        name='SK8-PARK',
        lat=36.62846425439145,
        long=-121.8420680608944,
        altitude=15.87972780005227,
    ),
    'BENCHES': Waypoint(
        name='BENCHES',
        lat=36.62235747331974,
        long=-121.847499539895,
        altitude=23.68826407858447,
    ),
    'NORTH-DUNE-RELAUNCH': Waypoint(
        name='NORTH-DUNE-RELAUNCH',
        lat=36.69174631178981,
        long=-121.8107945914495,
        altitude=10.05336799007576,
    ),
    'MARINA':
        Waypoint(
            name='MARINA',
            lat=36.69820566255434,
            long=-121.8091238415216,
            altitude=12.15525801694708,
        ),
}


class Test(unittest.TestCase):
    def test_process_gps_line(self):
        time, lat, long = tasks._process_gps_line('B2029453637507N12150627WA000000003390')

        self.assertEqual(20, time[0])
        self.assertEqual(29, time[1])
        self.assertEqual(45, time[2])
        self.assertEqual(36.62511666666666, lat)
        self.assertEqual(-121.84378333333333, long)

    def test_parse_trackfile(self):
        track = tasks._parse_trackfile(igc_path)

        self.assertEqual('casey gerstle', track['pilot'])
        self.assertEqual(15, track['day'])
        self.assertEqual(4, track['month'])
        self.assertEqual(2024, track['year'])

        breadcrumbs = track['breadcrumbs']
        self.assertEqual(7276, len(breadcrumbs))

        first = breadcrumbs[0]
        self.assertEqual(20, first['hour'])
        self.assertEqual(29, first['minute'])
        self.assertEqual(37, first['second'])
        self.assertEqual(36.62518333333333, first['lat'])
        self.assertEqual(-121.8438, first['long'])

        last = breadcrumbs[-1]
        self.assertEqual(22, last['hour'])
        self.assertEqual(31, last['minute'])
        self.assertEqual(10, last['second'])
        self.assertEqual(36.62531666666667, last['lat'])
        self.assertEqual(-121.844, last['long'])

    def test_flight_to_entry_goal(self):
        task = Task(
            turnpoints=[
                Turnpoint(waypoint=waypoints['SC-LAUNCH'], radius=100, tag='SSS'),
                Turnpoint(waypoint=waypoints['BENCHES'], radius=100, tag=''),
                Turnpoint(waypoint=waypoints['MARINA'], radius=100, tag=''),
                Turnpoint(waypoint=waypoints['NORTH-DUNE-RELAUNCH'], radius=100, tag=''),
                Turnpoint(waypoint=waypoints['SK8-PARK'], radius=4, tag='ESS'),
                Turnpoint(waypoint=waypoints['BUNKERS'], radius=100, tag='GOAL'),
            ]
        )

        flight = tasks._parse_trackfile(igc_path)
        entry = tasks._flight_to_entry(task, flight)

        self.assertEqual('casey gerstle', entry.name)
        self.assertEqual(datetime(2024, 4, 15, 20, 30, 18), entry.start)
        self.assertEqual(datetime(2024, 4, 15, 21, 50, 39), entry.end)
        self.assertEqual('goal', entry.status)

    def test_flight_to_entry_missed_ess(self):
        task = Task(
            turnpoints=[
                Turnpoint(waypoint=waypoints['SC-LAUNCH'], radius=100, tag='SSS'),
                Turnpoint(waypoint=waypoints['BENCHES'], radius=100, tag=''),
                Turnpoint(waypoint=waypoints['MARINA'], radius=100, tag=''),
                Turnpoint(waypoint=waypoints['NORTH-DUNE-RELAUNCH'], radius=100, tag=''),
                Turnpoint(waypoint=waypoints['SK8-PARK'], radius=3, tag='ESS'),
                Turnpoint(waypoint=waypoints['BUNKERS'], radius=1, tag='GOAL'),
            ]
        )

        flight = tasks._parse_trackfile(igc_path)
        entry = tasks._flight_to_entry(task, flight)

        self.assertEqual('casey gerstle', entry.name)
        self.assertEqual(datetime(2024, 4, 15, 20, 30, 18), entry.start)
        self.assertEqual(None, entry.end)
        self.assertEqual('missed turnpoint 5: SK8-PARK ESS', entry.status)

    # TODO: more tests


if __name__ == '__main__':
    unittest.main()
