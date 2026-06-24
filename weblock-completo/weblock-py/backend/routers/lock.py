import uuid
from datetime import datetime
from fastapi import APIRouter
from models.schemas import AccessRequest, LockEvent
from models.database import users, locations, access_logs, access_permissions

router = APIRouter(prefix="/lock", tags=["Lock"])


@router.post("/access")
def request_access(body: AccessRequest):
    start = datetime.utcnow()

    if not body.userId:
        log = _build_log(None, "Não identificado", None, body.locationId,
                         _get_location_name(body.locationId), "negado",
                         f"Cartão não cadastrado (ID lido: {body.cardId})", body.deviceIp)
        access_logs.insert(0, log)
        return {"allowed": False, "reason": "Cartão/usuário não cadastrado no sistema.", "response_time_ms": _ms(start)}

    user = next((u for u in users if u["id"] == body.userId and u["active"]), None)
    if not user:
        log = _build_log(body.userId, "Desconhecido", None, body.locationId, "Desconhecido", "negado", "Usuário não encontrado", body.deviceIp)
        access_logs.insert(0, log)
        return {"allowed": False, "reason": "Usuário não encontrado ou inativo.", "response_time_ms": _ms(start)}

    location = next((l for l in locations if l["id"] == body.locationId and l["active"]), None)
    if not location:
        log = _build_log(user["id"], user["name"], user["role"], body.locationId, "Desconhecido", "negado", "Local não encontrado", body.deviceIp)
        access_logs.insert(0, log)
        return {"allowed": False, "reason": "Local não encontrado.", "response_time_ms": _ms(start)}

    allowed_roles = access_permissions.get(body.locationId, [])
    allowed = user["role"] in allowed_roles

    log = _build_log(user["id"], user["name"], user["role"], location["id"], location["name"],
                     "permitido" if allowed else "negado",
                     None if allowed else "Sem permissão para este local",
                     body.deviceIp)
    access_logs.insert(0, log)

    return {
        "allowed": allowed,
        "reason": None if allowed else "Sem permissão para este local.",
        "user": {"id": user["id"], "name": user["name"], "role": user["role"]},
        "location": {"id": location["id"], "name": location["name"]},
        "response_time_ms": _ms(start),
    }


@router.post("/event")
def lock_event(body: LockEvent):
    print(f"[LOCK EVENT] {body.eventType} @ {body.locationId}    | {body.description}")
    return {"received": True, "timestamp": datetime.utcnow().isoformat() + "Z"}


def _build_log(user_id, user_name, user_role, location_id, location_name, result, reason, device_ip):
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id, "user_name": user_name, "user_role": user_role,
        "location_id": location_id, "location_name": location_name,
        "result": result, "reason": reason,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "device_ip": device_ip,
    }
def _get_location_name(location_id: str) -> str:
    loc = next((l for l in locations if l["id"] == location_id), None)
    return loc["name"] if loc else "Local desconhecido"

def _ms(start: datetime) -> int:
    return int((datetime.utcnow() - start).total_seconds() * 1000)
