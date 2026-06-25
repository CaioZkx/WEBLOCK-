from pydantic import BaseModel, EmailStr
from typing import Optional

# ── Auth ──────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    token: str
    user: dict

# ── Users ─────────────────────────────────────────────────────────────────────
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str
    matricula: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    matricula: Optional[str] = None
    active: Optional[bool] = None

# ── Locations ─────────────────────────────────────────────────────────────────
class LocationCreate(BaseModel):
    name: str
    building: Optional[str] = ""
    floor: Optional[str] = ""
    roles: list[str] = []

class LocationUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    active: Optional[bool] = None
    roles: Optional[list[str]] = None

# ── Lock ──────────────────────────────────────────────────────────────────────
class AccessRequest(BaseModel):
    userId: Optional[str] = None
    cardId: Optional[str] = None
    locationId: str
    deviceIp: Optional[str] = None

class LockEvent(BaseModel):
    locationId: str
    eventType: str
    deviceIp: Optional[str] = None
    description: Optional[str] = None
