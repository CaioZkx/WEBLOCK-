from fastapi import APIRouter, HTTPException, Depends
from models.schemas import LoginRequest
from models.database import users
from services.auth import verify_password, create_token, get_current_user, safe_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(body: LoginRequest):
    user = next((u for u in users if u["email"] == body.email.lower().strip() and u["active"]), None)
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    token = create_token({"id": user["id"], "email": user["email"], "role": user["role"]})
    return {"token": token, "user": safe_user(user)}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return safe_user(current_user)
