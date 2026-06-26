from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.schemas import LoginRequest
from models.orm_models import User
from database_config import get_db
from services.auth import verify_password, create_token, get_current_user, safe_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower().strip(), User.active == True).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    token = create_token({"id": user.id, "email": user.email, "role": user.role})
    return {"token": token, "user": safe_user(user)}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return safe_user(current_user)
