from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import db


class Waypoint(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    waypoint_group_id: Mapped[int] = mapped_column(ForeignKey('waypoint_group.id'))
    waypoint_group: Mapped["WaypointGroup"] = relationship(back_populates="waypoints")
    name: Mapped[str]
    lat: Mapped[float]
    long: Mapped[float]
    altitude: Mapped[float]
    description: Mapped[Optional[str]]
