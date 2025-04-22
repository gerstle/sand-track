from flask import Blueprint
import random
from src.models.task import Task
from src.models.turnpoint import Turnpoint
from src.models.waypoint import Waypoint
from src.models.waypoint_group import WaypointGroup
from src.models.entry import Entry
from typing import List
from src import db
from datetime import datetime
from faker import Faker

fake = Faker()

setup_bp = Blueprint("setup", __name__)


@setup_bp.cli.command("seed")
def seed_db():
    groups = _waypoint_groups()
    _add(groups)

    waypoints = _waypoints(groups)
    _add(waypoints)

    if True:
        tasks = _real_tasks()
        _add(tasks)
        _add(_real_turnpoints(tasks[0], waypoints))
    else:
        tasks = _tasks()
        _add(tasks)
        _add(_turnpoints(tasks, waypoints))
        _add(_entries(tasks))

    print("done.")


def _add(records: []):
    for it in records:
        db.session.add(it)
    db.session.commit()


def _waypoint_groups() -> List[WaypointGroup]:
    return [
        WaypointGroup(name="sand-city-v1", description="1 may 2025 sand city waypoints")
    ]


def _waypoints(groups: List[WaypointGroup]) -> List[Waypoint]:
    group_id = groups[0].id
    return [
        Waypoint(
            waypoint_group_id=group_id,
            name="SC-LAUNCH",
            lat=36.62526344882413,
            long=-121.844044848486,
            altitude=28.31566161661727,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="SC-LAUNCH",
            lat=36.62526344882413,
            long=-121.844044848486,
            altitude=28.31566161661727,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="LC-LAUNCH",
            lat=36.68388407784444,
            long=-121.8120426767962,
            altitude=30.72202769120279,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="BUNKERS",
            lat=36.64303442014818,
            long=-121.8322100638915,
            altitude=24.21054577202324,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="OCEAN",
            lat=36.63509183543911,
            long=-121.8382441545987,
            altitude=3.524216491979791,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="MARINA",
            lat=36.69820566255434,
            long=-121.8091238415216,
            altitude=12.15525801694708,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="DIRTY-GAP",
            lat=36.69280009140028,
            long=-121.8106859736226,
            altitude=7.027623540868831,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="LC",
            lat=36.68377139276167,
            long=-121.8135198529752,
            altitude=4.96567189587477,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="FORT-ORD",
            lat=36.65932303200422,
            long=-121.823376529724,
            altitude=3.943375720066011,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="SK8-PARK",
            lat=36.62846425439145,
            long=-121.8420680608944,
            altitude=15.87972780005227,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="TIOGA",
            lat=36.6187960676154,
            long=-121.8508424717575,
            altitude=10.9290397723054,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="GOON-DUNE",
            lat=36.6559294577638,
            long=-121.8246396131506,
            altitude=21.63161004710833,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="SARLACC-PIT",
            lat=36.625867749685,
            long=-121.8431407862103,
            altitude=6.4732170843956,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="BENCHES",
            lat=36.62235747331974,
            long=-121.847499539895,
            altitude=23.68826407858447,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="FACES",
            lat=36.64796771747011,
            long=-121.8288106085237,
            altitude=6.144915751607567,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="NORTH-DUNE-RELAUNCH",
            lat=36.69174631178981,
            long=-121.8107945914495,
            altitude=10.05336799007576,
        ),
        Waypoint(
            waypoint_group_id=group_id,
            name="SOUTH-DUNE-RELAUNCH",
            lat=36.68999757442087,
            long=-121.8112110760218,
            altitude=12.2777651960416,
        ),
    ]


def _real_tasks() -> List[Task]:
    format = "%Y-%m-%d %H:%M:%S%z"
    return [
        Task(
            name="May 2025",
            description="First task of the season! Run out to Lake Court, hit the bunkers, and home.",
            start=datetime.strptime("2025-05-01 00:00:00-0700", format),
            end=datetime.strptime("2025-06-01 00:00:00-0700", format),
        ),
    ]


def _tasks() -> List[Task]:
    format = "%Y-%m-%d %H:%M:%S%z"
    return [
        Task(
            name="jan 2025",
            start=datetime.strptime("2025-01-01 00:00:00-0700", format),
            end=datetime.strptime("2025-02-01 00:00:00-0700", format),
        ),
        Task(
            name="apr 2025",
            start=datetime.strptime("2025-04-01 00:00:00-0700", format),
            end=datetime.strptime("2025-05-01 00:00:00-0700", format),
        ),
        Task(
            name="may 2025",
            start=datetime.strptime("2025-05-01 00:00:00-0700", format),
            end=datetime.strptime("2025-06-01 00:00:00-0700", format),
        ),
    ]


def _find_waypoint(waypoints: List[Waypoint], name: str) -> Waypoint | None:
    for waypoint in waypoints:
        if waypoint.name == name:
            return waypoint

    return None


def _real_turnpoints(task: Task, waypoints: List[Waypoint]) -> List[Turnpoint]:
    rv = []
    task_points = [
        Turnpoint(
            task_id=task.id,
            order=1,
            waypoint_id=_find_waypoint(waypoints, "SC-LAUNCH").id,
            radius=50,
        ),
        Turnpoint(
            task_id=task.id,
            order=2,
            waypoint_id=_find_waypoint(waypoints, "LC").id,
            radius=100,
        ),
        Turnpoint(
            task_id=task.id,
            order=3,
            waypoint_id=_find_waypoint(waypoints, "BUNKERS").id,
            radius=25,
        ),
        Turnpoint(
            task_id=task.id,
            order=4,
            waypoint_id=_find_waypoint(waypoints, "SC-LAUNCH").id,
            radius=50,
        ),
    ]
    print(f"task_points: {task_points}")
    task_points[0].tag = "SSS"
    task_points[-2].tag = "ESS"
    task_points[-1].tag = "GOAL"
    rv.extend(task_points)

    return rv


def _turnpoints(tasks: List[Task], waypoints: List[Waypoint]) -> List[Turnpoint]:
    rv = []
    for task in tasks:
        task_points = []
        for index in range(1, random.randint(3, 8)):
            task_points.append(
                Turnpoint(
                    task_id=task.id,
                    order=index,
                    waypoint_id=random.choice(waypoints).id,
                    radius=random.randint(25, 1000),
                )
            )
        print(f"task_points: {task_points}")
        task_points[0].tag = "SSS"
        task_points[-2].tag = "ESS"
        task_points[-1].tag = "GOAL"
        rv.extend(task_points)

    return rv


def _entries(tasks: List[Task]) -> List[Entry]:
    rv = []
    for task in tasks:
        for index in range(random.randint(3, 8)):
            start = fake.date_between_dates(date_start=task.start, date_end=task.end)
            end = fake.date_between_dates(date_start=start, date_end=task.end)
            rv.append(
                Entry(
                    task_id=task.id,
                    name=fake.name(),
                    license=fake.port_number(),
                    glider=fake.company(),
                    glider_class=random.choice(["EN-A", "EN-B", "EN-C", "EN-D", "EN-CCC", "Mini", "Parakite"]),
                    start=start,
                    end=end,
                    time_seconds=(end - start).total_seconds(),
                    status=random.choice(["goal", "missed goal"])
                )
            )

    return rv
