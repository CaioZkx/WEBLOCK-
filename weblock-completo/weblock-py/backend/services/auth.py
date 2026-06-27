import os
import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database_config import get_db
from models.orm_models import User

try:
    from jose import JWTError, jwt
except ImportError:
    class JWTError(Exception):
        pass

    def _b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode().rstrip("=")

    class _JWTCompat:
        @staticmethod
        def encode(payload: dict, key: str, algorithm: str = "HS256") -> str:
            if algorithm != "HS256":
                raise ValueError("Algoritmo não suportado.")
            header = {"alg": algorithm, "typ": "JWT"}
            header_segment = _b64url(json.dumps(header, separators=(",", ":")).encode())
            payload_segment = _b64url(json.dumps(payload, separators=(",", ":")).encode())
            signing_input = f"{header_segment}.{payload_segment}".encode()
            signature = _b64url(hmac.new(key.encode(), signing_input, hashlib.sha256).digest())
            return f"{header_segment}.{payload_segment}.{signature}"

        @staticmethod
        def decode(token: str, key: str, algorithms: list | None = None):
            if algorithms and algorithms != ["HS256"]:
                raise ValueError("Algoritmo não suportado.")
            parts = token.split(".")
            if len(parts) != 3:
                raise JWTError("Token inválido.")
            header_segment, payload_segment, signature_segment = parts
            signing_input = f"{header_segment}.{payload_segment}".encode()
            expected_signature = _b64url(hmac.new(key.encode(), signing_input, hashlib.sha256).digest())
            if not hmac.compare_digest(signature_segment, expected_signature):
                raise JWTError("Assinatura inválida.")
            payload_bytes = base64.urlsafe_b64decode(payload_segment + "=" * (-len(payload_segment) % 4))
            payload = json.loads(payload_bytes.decode())
            exp = payload.get("exp")
            if exp is not None and int(exp) < int(time.time()):
                raise JWTError("Token expirado.")
            return payload

    jwt = _JWTCompat()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "weblock_secret")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
EXPIRE_H   = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", 8))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer      = HTTPBearer()


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = int((datetime.utcnow() + timedelta(hours=EXPIRE_H)).timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    user = db.query(User).filter(User.id == user_id, User.active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário inativo ou não encontrado.")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")
    return current_user


def require_admin_or_professor(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("admin", "professor"):
        raise HTTPException(status_code=403, detail="Acesso negado.")
    return current_user


def safe_user(user: User) -> dict:
    return {
        "id": user.id, "name": user.name, "email": user.email, "role": user.role,
        "matricula": user.matricula, "active": user.active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }
