from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import seed
from routers import auth, users, lock, logs, analytics, locations

app = FastAPI(
    title="WebLock API",
    description="Sistema de Controle de Acesso — UFC Sobral",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,      prefix="/api")
app.include_router(users.router,     prefix="/api")
app.include_router(lock.router,      prefix="/api")
app.include_router(logs.router,      prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(locations.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}


@app.on_event("startup")
def startup():
    seed()
    print("\n🔒 WebLock API (FastAPI) rodando!")
    print("   Docs: http://localhost:8000/docs")
    print("   Credenciais: admin@weblock.ufc.br / admin123\n")
