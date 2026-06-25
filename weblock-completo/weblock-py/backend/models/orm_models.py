"""
Modelos ORM (SQLAlchemy) — definem as tabelas reais no PostgreSQL.
Substitui as listas em memória de models/database.py.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database_config import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id         = Column(String, primary_key=True, default=gen_uuid)
    name       = Column(String, nullable=False)
    email      = Column(String, unique=True, nullable=False, index=True)
    password   = Column(String, nullable=False)
    role       = Column(String, nullable=False)
    matricula  = Column(String, nullable=True)
    active     = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Location(Base):
    __tablename__ = "locations"

    id         = Column(String, primary_key=True, default=gen_uuid)
    name       = Column(String, nullable=False)
    building   = Column(String, default="")
    floor      = Column(String, default="")
    active     = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    permissions = relationship("AccessPermission", back_populates="location", cascade="all, delete-orphan")


class AccessPermission(Base):
    """Define quais roles podem acessar qual local. Uma linha por (local, role)."""
    __tablename__ = "access_permissions"

    id          = Column(String, primary_key=True, default=gen_uuid)
    location_id = Column(String, ForeignKey("locations.id"), nullable=False)
    role        = Column(String, nullable=False)

    location = relationship("Location", back_populates="permissions")


class AccessLog(Base):
    __tablename__ = "access_logs"

    id            = Column(String, primary_key=True, default=gen_uuid)
    user_id       = Column(String, nullable=True)   # pode ser None (cartão não cadastrado)
    user_name     = Column(String, nullable=True)
    user_role     = Column(String, nullable=True)
    location_id   = Column(String, nullable=True)
    location_name = Column(String, nullable=True)
    result        = Column(String, nullable=False)  # "permitido" | "negado"
    reason        = Column(Text, nullable=True)
    timestamp     = Column(DateTime, default=datetime.utcnow, index=True)
    device_ip     = Column(String, nullable=True)
