from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from src import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    password: Mapped[str]
