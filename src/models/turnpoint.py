from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from src import db
from sqlalchemy import ForeignKey

class Turnpoint(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id'))
    task: Mapped["Task"] = relationship(back_populates="turnpoints")
    order: Mapped[int]
    waypoint_id: Mapped[int] = mapped_column(ForeignKey('waypoint.id'))
    waypoint: Mapped["Waypoint"] = relationship()
    radius: Mapped[int]
    tag: Mapped[Optional[str]]
