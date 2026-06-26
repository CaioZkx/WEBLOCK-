"""
Fixtures compartilhadas para os testes do WebLock.

Agora os testes rodam contra um banco SQLite separado (arquivo test.db),
NUNCA contra o Supabase de produção. Cada teste começa com o banco
limpo e repovoado (seed), igual fazíamos antes com as listas em memória.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Usa SQLite em arquivo só para os testes — não toca no Postgres de produção
TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from database_config import Base, get_db
from models import orm_models
from models.seed import seed
import main as main_module

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


main_module.app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


@pytest.fixture
def client():
    return TestClient(main_module.app)


@pytest.fixture
def auth_headers(client):
    def _get(email: str, password: str) -> dict:
        resp = client.post("/api/auth/login", json={"email": email, "password": password})
        assert resp.status_code == 200, resp.text
        token = resp.json()["token"]
        return {"Authorization": f"Bearer {token}"}
    return _get


@pytest.fixture
def admin_headers(auth_headers):
    return auth_headers("admin@weblock.ufc.br", "admin123")


@pytest.fixture
def professor_headers(auth_headers):
    return auth_headers("joao.silva@ufc.br", "senha123")


@pytest.fixture
def aluno_headers(auth_headers):
    return auth_headers("maria.oliveira@ufc.br", "senha123")


@pytest.fixture
def terceirizado_headers(auth_headers):
    return auth_headers("ana.lima@ufc.br", "senha123")
