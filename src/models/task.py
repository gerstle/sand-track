from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src import db

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
