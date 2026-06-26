from distro import name
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.schemas import LocationCreate, LocationUpdate
from models.orm_models import Location, AccessPermission, User
from database_config import get_db
from services.auth import get_current_user, require_admin

router = APIRouter(prefix="/locations", tags=["Locations"])

VALID_ROLES = {"admin", "professor", "aluno", "terceirizado"}


def _with_roles(loc: Location, db: Session) -> dict:
    roles = [p.role for p in db.query(AccessPermission).filter(AccessPermission.location_id == loc.id).all()]
    return {
        "id": loc.id, "name": loc.name, "building": loc.building, "floor": loc.floor,
        "active": loc.active,
        "created_at": loc.created_at.isoformat() if loc.created_at else None,
        "roles": roles,
    }


@router.get("")
def list_locations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    locs = db.query(Location).filter(Location.active == True).all()
    return [_with_roles(l, db) for l in locs]


@router.post("", status_code=201)
def create_location(body: LocationCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if not body.name or not body.name.strip():
        raise HTTPException(status_code=400, detail="Nome do local é obrigatório.")

    name = body.name.strip()
    building = (body.building or "").strip()
    floor = (body.floor or "").strip()

    duplicado = db.query(Location).filter(
        Location.name == name,
        Location.building == building,
        Location.floor == floor,
        Location.active == True,
    ).first()
    if duplicado:
        raise HTTPException(status_code=409, detail="Já existe um local com esse nome, bloco e andar.")

    invalid = [r for r in body.roles if r not in VALID_ROLES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Perfis inválidos: {', '.join(invalid)}")

    loc = Location(name=name, building=building, floor=floor, active=True)
    db.flush()  # garante loc.id antes de criar as permissões

    for role in body.roles:
        db.add(AccessPermission(location_id=loc.id, role=role))

    db.commit()
    db.refresh(loc)
    return _with_roles(loc, db)


@router.put("/{loc_id}")
def update_location(loc_id: str, body: LocationUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    loc = db.query(Location).filter(Location.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Local não encontrado.")

    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(status_code=400, detail="Nome do local não pode ser vazio.")
        loc.name = body.name.strip()
    if body.building is not None: loc.building = body.building.strip()
    if body.floor is not None:    loc.floor    = body.floor.strip()
    if body.active is not None:   loc.active   = body.active

    if body.roles is not None:
        invalid = [r for r in body.roles if r not in VALID_ROLES]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Perfis inválidos: {', '.join(invalid)}")
        db.query(AccessPermission).filter(AccessPermission.location_id == loc_id).delete()
        for role in body.roles:
            db.add(AccessPermission(location_id=loc_id, role=role))

    db.commit()
    db.refresh(loc)
    return _with_roles(loc, db)
