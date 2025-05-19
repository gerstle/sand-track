from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import db


class WaypointGroup(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    waypoints: Mapped[List["Waypoint"]] = relationship(back_populates="waypoint_group")

    def __repr__(self):
        return f"<WaypointGroup('{self.name}')>"
