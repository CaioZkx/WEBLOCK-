from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.schemas import AccessRequest, LockEvent
from models.orm_models import User, Location, AccessLog, AccessPermission
from database_config import get_db

router = APIRouter(prefix="/lock", tags=["Lock"])


@router.post("/access")
def request_access(body: AccessRequest, db: Session = Depends(get_db)):
    start = datetime.utcnow()

    if not body.userId:
        log = AccessLog(
            user_id=None, user_name="Não identificado", user_role=None,
            location_id=body.locationId, location_name=_get_location_name(db, body.locationId),
            result="negado", reason=f"Cartão não cadastrado (ID lido: {body.cardId})",
            device_ip=body.deviceIp,
        )
        db.add(log); db.commit()
        return {"allowed": False, "reason": "Cartão/usuário não cadastrado no sistema.", "response_time_ms": _ms(start)}

    user = db.query(User).filter(User.id == body.userId, User.active == True).first()
    if not user:
        log = AccessLog(
            user_id=body.userId, user_name="Desconhecido", user_role=None,
            location_id=body.locationId, location_name="Desconhecido",
            result="negado", reason="Usuário não encontrado", device_ip=body.deviceIp,
        )
        db.add(log); db.commit()
        return {"allowed": False, "reason": "Usuário não encontrado ou inativo.", "response_time_ms": _ms(start)}

    location = db.query(Location).filter(Location.id == body.locationId, Location.active == True).first()
    if not location:
        log = AccessLog(
            user_id=user.id, user_name=user.name, user_role=user.role,
            location_id=body.locationId, location_name="Desconhecido",
            result="negado", reason="Local não encontrado", device_ip=body.deviceIp,
        )
        db.add(log); db.commit()
        return {"allowed": False, "reason": "Local não encontrado.", "response_time_ms": _ms(start)}

    allowed_roles = [p.role for p in db.query(AccessPermission).filter(AccessPermission.location_id == location.id).all()]
    allowed = user.role == "admin" or user.role in allowed_roles

    log = AccessLog(
        user_id=user.id, user_name=user.name, user_role=user.role,
        location_id=location.id, location_name=location.name,
        result="permitido" if allowed else "negado",
        reason=None if allowed else "Sem permissão para este local",
        device_ip=body.deviceIp,
    )
    db.add(log); db.commit()

    return {
        "allowed": allowed,
        "reason": None if allowed else "Sem permissão para este local.",
        "user": {"id": user.id, "name": user.name, "role": user.role},
        "location": {"id": location.id, "name": location.name},
        "response_time_ms": _ms(start),
    }


@router.post("/event")
def lock_event(body: LockEvent):
    print(f"[LOCK EVENT] {body.eventType} @ {body.locationId} | {body.description}")
    return {"received": True, "timestamp": datetime.utcnow().isoformat() + "Z"}


def _get_location_name(db: Session, location_id: str) -> str:
    loc = db.query(Location).filter(Location.id == location_id).first()
    return loc.name if loc else "Local desconhecido"


def _ms(start: datetime) -> int:
    return int((datetime.utcnow() - start).total_seconds() * 1000)
