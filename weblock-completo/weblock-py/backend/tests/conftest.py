"""
Fixtures compartilhadas para os testes do WebLock.

IMPORTANTE: o "banco de dados" é formado por listas Python em memória
(models/database.py). Como os testes rodam no mesmo processo, é preciso
limpar e re-popular essas listas antes de CADA teste — senão um teste
contamina o próximo (ex: um usuário criado em test_users.py apareceria
em test_logs.py).
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

# Garante que o pacote backend é importável quando o pytest roda da raiz do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models import database as db


@pytest.fixture(autouse=True)
def reset_database():
    """Limpa e repovoa o banco em memória antes de cada teste."""
    db.users.clear()
    db.locations.clear()
    db.access_logs.clear()
    db.access_permissions.clear()
    db.access_permissions.update({
        "loc-001": ["admin", "professor", "aluno"],
        "loc-002": ["admin", "professor", "aluno"],
        "loc-003": ["admin", "professor", "aluno", "terceirizado"],
        "loc-004": ["admin", "professor", "aluno", "terceirizado"],
        "loc-005": ["admin", "professor"],
    })
    db.seed()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Retorna uma função que faz login e devolve os headers Authorization prontos."""
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
