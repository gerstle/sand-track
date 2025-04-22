import datetime
import os
import sys
from enum import Enum
from typing import Tuple
from zoneinfo import ZoneInfo

from flask import Blueprint, request, render_template, flash, redirect, url_for, current_app
from geopy import distance
from sqlalchemy import or_, text
from werkzeug.utils import secure_filename

from src import db
from src.models.entry import Entry
from src.models.task import Task
from src.models.turnpoint import Turnpoint

ALLOWED_EXTENSIONS = {'igc'}

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/')
def index():
    now = datetime.datetime.now(tz=ZoneInfo('America/Los_Angeles'))
    now = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    return render_template(
        'tasks/index.html',
        tasks=db.session.query(Task).order_by(Task.id).filter(or_(Task.start >= now, Task.end >= now)))


@tasks_bp.route('/<int:task_id>')
def detail(task_id: int):
    task = db.session.query(Task).get(task_id)
    task.entries.sort(key=_sort_entries)

    entry = None
    entry_id = request.args.get('entry_id')
    if entry_id:
        entry = db.session.query(Entry).get(entry_id)

    ab_entries=db.session.query(Entry).from_statement(text(f"SELECT * FROM entry WHERE task_id={task.id} AND (glider_class='EN-A' OR glider_class='EN-B')")).all()
    ab_entries.sort(key=_sort_entries)

    ab_entries=_get_entries(f"SELECT * FROM entry WHERE task_id={task.id} AND (glider_class='EN-A' OR glider_class='EN-B')")
    c_entries=_get_entries(f"SELECT * FROM entry WHERE task_id={task.id} AND glider_class='EN-C'")
    hot_entries=_get_entries(f"SELECT * FROM entry WHERE task_id={task.id} AND (glider_class='EN-D' OR glider_class='EN-CCC')")
    special_entries=_get_entries(f"SELECT * FROM entry WHERE task_id={task.id} AND (glider_class='Mini' OR glider_class='Parakite')")

    return render_template('tasks/detail.html', task=task, entry=entry, category_entries=[
        {"id": "ab", "name": "EN-A / EN-B", "entries": ab_entries},
        {"id": "c", "name": "EN-C", "entries": c_entries},
        {"id": "dccc", "name": "EN-D / EN-CCC", "entries": hot_entries},
        {"id": "cool", "name": "Cool Kids", "entries": special_entries}
    ])


def _get_entries(query: str) -> list[Entry]:
    entries = db.session.query(Entry).from_statement(text(query)).all()
    entries.sort(key=_sort_entries)
    return entries


def _sort_entries(entry: Entry):
    if entry.time_seconds:
        return entry.time_seconds
    else:
        return sys.maxsize


@tasks_bp.route('/<int:task_id>/tracklog', methods=['POST'])
def submit_tracklog(task_id: int):
    task = db.session.query(Task).get(task_id)

    if not task:
        flash('Invalid task!', category='danger')
        return redirect(url_for('tasks.detail', task_id=task_id))

    if 'tracklogFile' not in request.files:
        flash('No file part', category='danger')
        return redirect(url_for('tasks.detail', task_id=task_id))
    file = request.files['tracklogFile']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        flash('No file selected', category='danger')
        return redirect(url_for('tasks.detail', task_id=task_id))
    if file and _allowed_file(file.filename):
        filename = secure_filename(file.filename)

        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        current_app.logger.info("file upload path: {path}")
        file.save(path)
        try:
            state, entry = _process_flight(
                task,
                path=path,
                name=request.form['name'],
                license=request.form['license'],
                glider=request.form['glider'],
                glider_class=request.form['gliderClass'],
            )
            message = ''
            if state == 'new':
                message = f'New Entry Created!'
            elif state == 'updated':
                message = f'Updated your previous entry!'
            elif state == 'ignored':
                message = f'Your previous entry was better!'

            flash(message, category='info')
            os.remove(path)

            current_app.logger.info(f"redirecting with entry_id: {entry.id}")
            return redirect(url_for('tasks.detail', task_id=task_id, entry_id=entry.id))
        except ValueError as e:
            flash(str(e), category='danger')
            return redirect(url_for('tasks.detail', task_id=task_id))
    return None


def _allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _process_flight(
        task: Task,
        name: str,
        license: str,
        glider: str,
        glider_class: str,
        path: str,
) -> Tuple[str, Entry]:
    flight = _parse_trackfile(path)
    start_time = datetime.datetime(
        flight['year'], flight['month'], flight['day'],
        flight['breadcrumbs'][0]['hour'], flight['breadcrumbs'][0]['minute'], flight['breadcrumbs'][0]['second']
    )

    current_app.logger.info(f"flight start: {start_time} task: {task.start} --> {task.end}")
    if task.start <= start_time <= task.end:
        current_app.logger.info("flight within task window")
    else:
        current_app.logger.info("flight outside task window")
        raise ValueError('Flight outside of task window')

    new_entry = _flight_to_entry(task, flight)
    new_entry.name = name
    new_entry.license = license
    new_entry.glider = glider
    new_entry.glider_class = glider_class
    existing = db.session.query(Entry).filter_by(
        task_id=task.id,
        name=new_entry.name,
        glider_class=new_entry.glider_class
    ).first()

    state = None
    if existing:
        if existing.time_seconds is None or (new_entry.time_seconds and existing.time_seconds > new_entry.time_seconds):
            state = "updated"
            current_app.logger.info("updating existing entry")
            existing.submitted = datetime.datetime.now()
            existing.start = new_entry.start
            existing.end = new_entry.end
            existing.time_seconds = new_entry.time_seconds
            existing.status = new_entry.status
        else:
            state = "ignored"
            current_app.logger.info("existing entry is better")
        entry = existing
    else:
        state = "new"
        current_app.logger.info("creating new entry")
        db.session.add(new_entry)
        entry = new_entry
    db.session.commit()

    current_app.logger.info(f"entry_id: {entry.id}")
    return state, entry


def _parse_trackfile(path: str) -> dict[str, list[dict[str, int | float]] | str | int]:
    breadcrumbs = []
    track = {'breadcrumbs': breadcrumbs}
    with open(path, 'r') as file:
        for line in file:
            if line.startswith('HFPLTPILOTINCHARGE'):
                track['pilot'] = line.split(':')[1].strip()
            if line.startswith('HFDTEDATE'):
                date = line.split(':')[1].strip()
                track['day'] = int(date[0:2])
                track['month'] = int(date[2:4])
                track['year'] = 2000 + int(date[4:6])
            if line.startswith('B'):
                timestamp, lat, long = _process_gps_line(line)
                breadcrumbs.append({
                    'hour': timestamp[0],
                    'minute': timestamp[1],
                    'second': timestamp[2],
                    'lat': lat,
                    'long': long
                })

    return track


def _process_gps_line(line: str) -> Tuple[Tuple[int, int, int], float, float]:
    time_str = line[1:7]  # HHMMSS
    lat_str = line[7:14]  # Latitude
    lat_hemisphere = line[14:15]
    long_str = line[15:23]  # Longitude
    long_hemisphere = line[23:24]

    # Convert latitude
    lat_deg = int(lat_str[:2])
    lat_min = float(lat_str[2:7]) / 1000
    lat = lat_deg + (lat_min / 60)
    if lat_hemisphere == 'S':
        lat = -lat

    # Convert longitude
    long_deg = int(long_str[:3])
    long_min = float(long_str[3:8]) / 1000
    long = long_deg + (long_min / 60)
    if long_hemisphere == 'W':
        long = -long

    # Convert time to datetime format
    hours = int(time_str[:2])
    minutes = int(time_str[2:4])
    seconds = int(time_str[4:6])

    return (hours, minutes, seconds), lat, long


STATE = Enum(
    'State',
    [
        ('STARTING', 1),  # looking for start cylinder
        ('IN_START', 2),  # In the start cylinder, looking for an exit
        ('STARTED', 3),  # start the clock have exited the start cylinder
        ('ESS', 4),  # Stop the clock, all turnpoints before and including ESS were tagged
        ('GOAL', 5)  # Made goal, task complete
    ]
)


def _flight_to_entry(task: Task, flight: dict[str, list[dict[str, int | float]] | str | int]) -> Entry:
    start_time, end_time = None, None

    state = STATE.STARTING
    turnpoints = task.turnpoints
    current_turnpoint = 0
    for i, breadcrumb in enumerate(flight['breadcrumbs']):
        in_current_turnpoint = _is_in_turnpoint(turnpoints[current_turnpoint], breadcrumb['lat'], breadcrumb['long'])

        # TODO: this makes some assumptions about SSS, ESS, GOAL... might be fine, just gotta make sure we create
        # tasks that match. Ie:
        # - always have SSS as first turnpoint
        # - always have ESS as second to last turnpoint
        # - always have GOAL as last turnpoint
        if state == STATE.STARTING:
            # we are looking for the start cylinder
            if in_current_turnpoint:
                _log_flight_event(i, current_turnpoint, turnpoints[current_turnpoint], 'tagged --> STATE.IN_START')
                state = STATE.IN_START
        if state == STATE.IN_START:
            # we are in the start cylinder and looking for an exit
            if not in_current_turnpoint:
                _log_flight_event(i, current_turnpoint, turnpoints[current_turnpoint], 'left --> STATE.STARTED')
                state = STATE.STARTED
                start_time = datetime.datetime(flight['year'], flight['month'], flight['day'], breadcrumb['hour'],
                                               breadcrumb['minute'], breadcrumb['second'])
                current_turnpoint += 1
        if state == STATE.STARTED:
            # we are now racing and looking for entering the current turnpoint
            if in_current_turnpoint:
                if turnpoints[current_turnpoint].tag == 'ESS':
                    _log_flight_event(i, current_turnpoint, turnpoints[current_turnpoint], 'tagged --> STATE.STARTED')
                    state = STATE.ESS
                    end_time = datetime.datetime(flight['year'], flight['month'], flight['day'], breadcrumb['hour'],
                                                 breadcrumb['minute'], breadcrumb['second'])
                else:
                    _log_flight_event(i, current_turnpoint, turnpoints[current_turnpoint], 'tagged')
                current_turnpoint += 1
        if state == STATE.ESS:
            # we have hit ESS and are looking for goal
            if in_current_turnpoint:
                _log_flight_event(i, current_turnpoint, turnpoints[current_turnpoint], 'tagged goal')
                state = STATE.GOAL
                break

    status = None
    time = None
    if state == STATE.STARTING:
        status = 'no SSS'
    if state == STATE.IN_START:
        status = 'never left SSS'
    if state == STATE.STARTED:
        status = f'missed turnpoint {current_turnpoint + 1}: {turnpoints[current_turnpoint].waypoint.name} {turnpoints[current_turnpoint].tag or ""}'
    if state == STATE.ESS:
        status = f'missed goal. turnpoint {current_turnpoint + 1}: {turnpoints[current_turnpoint].waypoint.name} {turnpoints[current_turnpoint].tag or ""}'
    if state == STATE.GOAL:
        status = 'goal'
        time = (end_time - start_time).total_seconds()
    current_app.logger.debug(f'final status: {status} time: {time}')

    return Entry(task_id=task.id, name=flight['pilot'], start=start_time, end=end_time, time_seconds=time,
                 status=status)


def _log_flight_event(breadcrumb_index: int, turnpoint_index: int, turnpoint: Turnpoint, message: str) -> None:
    current_app.logger.debug(
        f'[{breadcrumb_index}] turnpoint {turnpoint_index + 1}: {turnpoint.waypoint.name} {turnpoint.tag or ""} - {message}')


def _is_in_turnpoint(turnpoint: Turnpoint, lat: float, long: float) -> bool:
    distance_meters = distance.distance(
        (turnpoint.waypoint.lat, turnpoint.waypoint.long),
        (lat, long)
    ).meters

    return distance_meters <= turnpoint.radius
