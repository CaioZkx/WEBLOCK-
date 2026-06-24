import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import LocationCreate, LocationUpdate
from models.database import locations, access_permissions
from services.auth import get_current_user, require_admin

router = APIRouter(prefix="/locations", tags=["Locations"])

VALID_ROLES = {"admin", "professor", "aluno", "terceirizado"}


def _with_roles(loc: dict) -> dict:
    return {**loc, "roles": access_permissions.get(loc["id"], [])}


@router.get("")
def list_locations(current_user: dict = Depends(get_current_user)):
    return [_with_roles(l) for l in locations if l["active"]]


@router.post("", status_code=201)
def create_location(body: LocationCreate, current_user: dict = Depends(require_admin)):
    if not body.name or not body.name.strip():
        raise HTTPException(status_code=400, detail="Nome do local é obrigatório.")

    invalid = [r for r in body.roles if r not in VALID_ROLES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Perfis inválidos: {', '.join(invalid)}")

    loc = {
        "id": str(uuid.uuid4()),
        "name": body.name.strip(),
        "building": (body.building or "").strip(),
        "floor": (body.floor or "").strip(),
        "active": True,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    locations.append(loc)
    access_permissions[loc["id"]] = body.roles
    return _with_roles(loc)


@router.put("/{loc_id}")
def update_location(loc_id: str, body: LocationUpdate, current_user: dict = Depends(require_admin)):
    loc = next((l for l in locations if l["id"] == loc_id), None)
    if not loc:
        raise HTTPException(status_code=404, detail="Local não encontrado.")

    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(status_code=400, detail="Nome do local não pode ser vazio.")
        loc["name"] = body.name.strip()
    if body.building is not None: loc["building"] = body.building.strip()
    if body.floor is not None:    loc["floor"]    = body.floor.strip()
    if body.active is not None:   loc["active"]   = body.active
    if body.roles is not None:
        invalid = [r for r in body.roles if r not in VALID_ROLES]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Perfis inválidos: {', '.join(invalid)}")
        access_permissions[loc_id] = body.roles

    return _with_roles(loc)