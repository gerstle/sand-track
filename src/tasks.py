from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint
from flask import render_template
from sqlalchemy import or_

from src import db
from src.models.task import Task

tasks_bp = Blueprint('task', __name__)

@tasks_bp.route('/tasks')
def index():
    now = datetime.now(tz=ZoneInfo("America/Los_Angeles"))
    now = datetime(now.year, now.month, now.day, 0, 0, 0)
    return render_template(
        'tasks/index.html',
        tasks=db.session.query(Task).order_by(Task.id).filter(or_(Task.start >= now, Task.end >= now))
    )

@tasks_bp.route('/tasks/<int:task_id>')
def detail(task_id: int):
    task = db.session.query(Task).get(task_id)
    task.turnpoints.sort(key=lambda it: it.order)
    task.entries.sort(key=lambda it: it.end - it.start)

    return render_template('tasks/detail.html', task=task)
