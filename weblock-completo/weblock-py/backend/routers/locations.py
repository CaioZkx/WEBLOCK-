import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import LocationCreate, LocationUpdate
from models.database import locations
from services.auth import get_current_user, require_admin

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.get("")
def list_locations(current_user: dict = Depends(get_current_user)):
    return [l for l in locations if l["active"]]


@router.post("", status_code=201)
def create_location(body: LocationCreate, current_user: dict = Depends(require_admin)):
    loc = {"id": str(uuid.uuid4()), "name": body.name, "building": body.building or "", "floor": body.floor or "", "active": True, "created_at": datetime.utcnow().isoformat()}
    locations.append(loc)
    return loc


@router.put("/{loc_id}")
def update_location(loc_id: str, body: LocationUpdate, current_user: dict = Depends(require_admin)):
    loc = next((l for l in locations if l["id"] == loc_id), None)
    if not loc:
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    if body.name is not None:     loc["name"]     = body.name
    if body.building is not None: loc["building"] = body.building
    if body.floor is not None:    loc["floor"]    = body.floor
    if body.active is not None:   loc["active"]   = body.active
    return loc
