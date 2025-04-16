import datetime
import sys
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import and_, or_
from sqlalchemy.sql import func

from src import db


def remove_key(d, key):
    return dict((k, v) for (k, v) in d.items() if k != key)


class Entry(db.Model):
    __table_args__ = (db.UniqueConstraint('name', 'task_id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id'))
    task: Mapped["Task"] = relationship(back_populates="entries")
    name: Mapped[str]
    submitted: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=func.now(),
                                                         onupdate=func.now())
    start: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str]
    time_seconds: Mapped[Optional[int]]

    def elapsed(self):
        if self.time_seconds:
            return str(datetime.timedelta(seconds=self.time_seconds))
        else:
            return None

    def upsert(data):
        primary_keys = (Entry.task_id, Entry.name)
        insert_stmt = insert(Entry).values(data)

        start = data.get('start')
        end = data.get('end')
        if start and end:
            time = (end - start).total_seconds()
        else:
            time = sys.maxsize

        do_update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=primary_keys,
            where=and_(Entry.task_id == data.get('task_id'), Entry.name == data.get('name'), or_(Entry.time_seconds == None, Entry.time_seconds >= time)),
            set_=data
        )
        return do_update_stmt

    def __repr__(self):
        return f"<Entry(name='{self.name}', task_id='{self.task_id}', submitted={self.submitted}, start='{self.start}', end='{self.end}', status='{self.status}')>"
