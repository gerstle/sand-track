from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import db
from src.models.entry import Entry
from src.models.turnpoint import Turnpoint


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    turnpoints: Mapped[List["Turnpoint"]] = relationship(back_populates="task", order_by="Turnpoint.order.asc()")
    entries: Mapped[List["Entry"]] = relationship(back_populates="task")
