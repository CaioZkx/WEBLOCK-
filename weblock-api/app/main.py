from fastapi import FastAPI
from app.core.database import Base
from app.core.database import engine
from app.api.auth import router as auth_router

app = FastAPI(
    title="WEBLOCK API"
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)


@app.get("/")
def home():
    return {
        "message": "WEBLOCK funcionando"
    }

Base.metadata.create_all(bind=engine)