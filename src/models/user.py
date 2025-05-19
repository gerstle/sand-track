import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column
from flask_login import UserMixin

from src.db import db


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=sqlalchemy.sql.expression.literal(False), nullable=False)
