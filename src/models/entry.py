from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src import db


class Entry(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id'))
    task: Mapped["Task"] = relationship(back_populates="entries")
    name: Mapped[str]
    submitted: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
