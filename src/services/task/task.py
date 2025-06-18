"""
Service for generating QR codes for tasks. Based on the "task definition format 2" defined
here: https://xctrack.org/Competition_Interfaces.html
"""
import io
import json
import logging

import qrcode
from qrcode.image.pure import PyPNGImage
from flask import render_template

import src.services.polyline as polyline
from src.models.task import Task
from src.models.turnpoint import Turnpoint

logger = logging.getLogger(__name__)

def generate_qrcode(task: Task) -> bytes:
    """generate qrcode for a set of turnpoints"""
    logger.debug(f"generating qrcode for task {task.id}")
    b = io.BytesIO()
    img = qrcode.make(generate_doc(task), image_factory=PyPNGImage)
    img.save(b, "png")
    return b.getvalue()

def generate_doc(task: Task) -> str:
    """generate the json for a task definition"""
    logger.debug(f"generating qrcode content for task {task.id}")

    tp = []
    for it in task.turnpoints:
        t = {"z": _polyline(it), "n": it.waypoint.name}
        tag = _tag(it)
        if tag:
            t["t"] = tag

        tp.append(t)

    logger.debug(f"turnpoints: {tp}")
    tp_json = json.dumps(tp)
    rv = render_template("task.task", turnpoint_json=tp_json)
    logger.info(f"task {task.id} task doc: {rv}")
    return rv

def _polyline(turnpoint: Turnpoint) -> str:
    encoded = polyline.encode(turnpoint.waypoint.long, turnpoint.waypoint.lat, turnpoint.radius)

    benches_encoded = "ziufVwxo~Eo@od@"
    logger.debug(f"static benches: {benches_encoded} --> {polyline.decode(benches_encoded)}")
    logger.debug(f"{turnpoint.waypoint.name}: {turnpoint.waypoint.long} {turnpoint.waypoint.lat} {turnpoint.radius} --> {encoded}")
    logger.debug(f"{encoded} --> {polyline.decode(encoded)}")

    return encoded

def _tag(turnpoint: Turnpoint) -> int|None:
    tag = turnpoint.tag
    if tag:
        if tag == "SSS":
            return 2
        elif tag == "ESS":
            return 3

    return None