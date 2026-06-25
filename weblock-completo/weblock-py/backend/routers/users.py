from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models.schemas import UserCreate, UserUpdate
from models.orm_models import User
from database_config import get_db
from services.auth import get_current_user, require_admin, require_admin_or_professor, hash_password, safe_user

router = APIRouter(prefix="/users", tags=["Users"])

VALID_ROLES = {"admin", "professor", "aluno", "terceirizado"}


@router.get("")
def list_users(
    role: str = Query(None),
    active: bool = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_professor),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if active is not None:
        query = query.filter(User.active == active)
    if search:
        q = f"%{search.lower()}%"
        query = query.filter(
            (User.name.ilike(q)) | (User.email.ilike(q)) | (User.matricula.ilike(q))
        )
    users = query.all()
    return {"total": len(users), "users": [safe_user(u) for u in users]}


@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return safe_user(user)


@router.post("", status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if not body.name or not body.name.strip():
        raise HTTPException(status_code=400, detail="Nome é obrigatório.")
    if not body.email or not body.email.strip():
        raise HTTPException(status_code=400, detail="Email é obrigatório.")
    if not body.password or not body.password.strip():
        raise HTTPException(status_code=400, detail="Senha é obrigatória.")
    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Role inválida. Use: {', '.join(VALID_ROLES)}")

    email = body.email.lower().strip()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email já cadastrado.")

    new_user = User(
        name=body.name.strip(),
        email=email,
        password=hash_password(body.password),
        role=body.role,
        matricula=body.matricula,
        active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return safe_user(new_user)


@router.put("/{user_id}")
def update_user(user_id: str, body: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if body.email and body.email.lower().strip() != user.email:
        new_email = body.email.lower().strip()
        if db.query(User).filter(User.email == new_email, User.id != user_id).first():
            raise HTTPException(status_code=409, detail="Email já em uso.")
        user.email = new_email

    if body.name:     user.name = body.name.strip()
    if body.role:     user.role = body.role
    if body.matricula is not None: user.matricula = body.matricula
    if body.active is not None:    user.active    = body.active
    if body.password: user.password = hash_password(body.password)

    db.commit()
    db.refresh(user)
    return safe_user(user)


@router.delete("/{user_id}")
def delete_user(user_id: str, permanent: bool = False, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é possível remover seu próprio usuário.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if permanent:
        db.delete(user)
        db.commit()
        return {"message": "Usuário excluído permanentemente."}

    user.active = False
    db.commit()
    return {"message": "Usuário desativado com sucesso."}
