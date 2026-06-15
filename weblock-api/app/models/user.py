import enum

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Enum

from app.core.database import Base


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    PROFESSOR = "PROFESSOR"
    ALUNO = "ALUNO"
    TERCEIRIZADO = "TERCEIRIZADO"


class User(Base):
    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String,
        nullable=False
    )

    role = Column(
        Enum(UserRole),
        nullable=False
    )