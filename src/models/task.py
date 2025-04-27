import logging
import sys
from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import db
from src.models.entry import Entry

logger = logging.getLogger(__name__)


class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    turnpoints: Mapped[List["Turnpoint"]] = relationship(back_populates="task", order_by="Turnpoint.order.asc()")
    entries: Mapped[List["Entry"]] = relationship(back_populates="task")

    def current_leader(self):
        if self.entries:
            self.entries.sort(key=Task.sort_entries)
            first = self.entries[0]
            return f"{first.name} in {first.elapsed()}"
        else:
            return None

    @staticmethod
    def sort_entries(entry: Entry):
        if entry.time_seconds:
            return entry.time_seconds
        else:
            return sys.maxsize

    @property
    def id_and_name(self):
        return f"({self.id}) {self.name}"

    def __repr__(self):
        return f"<Task(id='{self.id}' name='{self.name}')>"