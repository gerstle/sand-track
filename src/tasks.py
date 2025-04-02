from flask import Flask, render_template, request, url_for, flash, redirect
from flask import Blueprint
from flask_login import login_required, current_user
from src import db
from src.models.task import Task
from datetime import datetime
import pytz

tasks = Blueprint('task', __name__)
PST = pytz.timezone("US/Pacific")

@tasks.route('/tasks')
def index():
    now = datetime.utcnow().astimezone(PST)
    now = datetime(now.year, now.month, now.day, 0, 0, 0)
    print(f"----------------------------- time: {now}")
    return render_template(
        'tasks/index.html',
        tasks=db.session.query(Task).order_by(Task.id).filter(Task.start <= now, Task.end > now)
    )

@tasks.route('/tasks/<int:task_id>')
def detail(task_id: int):
    return render_template('tasks/detail.html', task=db.session.query(Task).get(task_id))
