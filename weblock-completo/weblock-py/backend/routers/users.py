import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from models.schemas import UserCreate, UserUpdate
from models.database import users
from services.auth import get_current_user, require_admin, require_admin_or_professor, hash_password, safe_user

router = APIRouter(prefix="/users", tags=["Users"])

VALID_ROLES = {"admin", "professor", "aluno", "terceirizado"}


@router.get("")
def list_users(
    role: str = Query(None),
    active: bool = Query(None),
    search: str = Query(None),
    current_user: dict = Depends(require_admin_or_professor)
):
    result = [safe_user(u) for u in users]
    if role:   result = [u for u in result if u["role"] == role]
    if active is not None: result = [u for u in result if u["active"] == active]
    if search:
        q = search.lower()
        result = [u for u in result if q in u["name"].lower() or q in u["email"].lower() or q in (u.get("matricula") or "").lower()]
    return {"total": len(result), "users": result}


@router.get("/{user_id}")
def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return safe_user(user)


@router.post("", status_code=201)
def create_user(body: UserCreate, current_user: dict = Depends(require_admin)):
    if not body.name or not body.name.strip():
        raise HTTPException(status_code=400, detail="Nome é obrigatório.")
    if not body.email or not body.email.strip():
        raise HTTPException(status_code=400, detail="Email é obrigatório.")
    if not body.password or not body.password.strip():
        raise HTTPException(status_code=400, detail="Senha é obrigatória.")
    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Role inválida. Use: {', '.join(VALID_ROLES)}")
    if any(u["email"] == body.email.lower().strip() for u in users):
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    new_user = {
        "id": str(uuid.uuid4()),
        "name": body.name.strip(),
        "email": body.email.lower().strip(),
        "password": hash_password(body.password),
        "role": body.role,
        "matricula": body.matricula,
        "active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    users.append(new_user)
    return safe_user(new_user)


@router.put("/{user_id}")
def update_user(user_id: str, body: UserUpdate, current_user: dict = Depends(require_admin)):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if body.email and body.email != user["email"]:
        if any(u["email"] == body.email.lower().strip() for u in users if u["id"] != user_id):
            raise HTTPException(status_code=409, detail="Email já em uso.")

    if body.name:     user["name"]     = body.name
    if body.email:    user["email"]    = body.email.lower().strip()
    if body.role:     user["role"]     = body.role
    if body.matricula is not None: user["matricula"] = body.matricula
    if body.active is not None:    user["active"]    = body.active
    if body.password: user["password"] = hash_password(body.password)
    user["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return safe_user(user)


@router.delete("/{user_id}")
def delete_user(user_id: str, permanent: bool = False, current_user: dict = Depends(require_admin)):
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Não é possível remover seu próprio usuário.")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if permanent:
        users.remove(user)
        return {"message": "Usuário excluído permanentemente."}

    user["active"] = False
    user["updated_at"] = datetime.utcnow().isoformat() 
    return {"message": "Usuário desativado com sucesso."}