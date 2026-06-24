"""
WebLock - Banco de dados em memória
Em produção substituir por SQLAlchemy + PostgreSQL/SQLite
"""
import uuid
import random
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Tabelas ────────────────────────────────────────────────────────────────────
users: list[dict] = []
locations: list[dict] = []
access_logs: list[dict] = []

access_permissions: dict[str, list[str]] = {
    "loc-001": ["admin", "professor", "aluno"],
    "loc-002": ["admin", "professor", "aluno"],
    "loc-003": ["admin", "professor", "aluno", "terceirizado"],
    "loc-004": ["admin", "professor", "aluno", "terceirizado"],
    "loc-005": ["admin", "professor"],

}


def seed():
    global users, locations, access_logs

    locations.extend([
        {"id": "loc-001", "name": "Laboratório de Informática 1", "building": "Bloco A", "floor": "1", "active": True, "created_at": datetime.utcnow().isoformat() + "Z"},
        {"id": "loc-002", "name": "Laboratório de Informática 2", "building": "Bloco A", "floor": "2", "active": True, "created_at": datetime.utcnow().isoformat() + "Z"},
        {"id": "loc-003", "name": "Sala de Aula 101",             "building": "Bloco B", "floor": "1", "active": True, "created_at": datetime.utcnow().isoformat() + "Z"},
        {"id": "loc-004", "name": "Biblioteca",                   "building": "Bloco C", "floor": "1", "active": True, "created_at": datetime.utcnow().isoformat() + "Z"},
        {"id": "loc-005", "name": "Sala dos Professores",         "building": "Bloco B", "floor": "2", "active": True, "created_at": datetime.utcnow().isoformat() + "Z"},
    ])

    seed_users = [
        {"name": "Administrador",    "email": "admin@weblock.ufc.br",       "password": "admin123",  "role": "admin",        "matricula": "ADM0001"},
        {"name": "Prof. João Silva", "email": "joao.silva@ufc.br",          "password": "senha123",  "role": "professor",    "matricula": "PROF001"},
        {"name": "Maria Oliveira",   "email": "maria.oliveira@ufc.br",      "password": "senha123",  "role": "aluno",        "matricula": "2021001"},
        {"name": "Carlos Souza",     "email": "carlos.souza@ufc.br",        "password": "senha123",  "role": "aluno",        "matricula": "2022003"},
        {"name": "Ana Lima",         "email": "ana.lima@ufc.br",            "password": "senha123",  "role": "terceirizado", "matricula": "TERC01"},
    ]

    for u in seed_users:
        users.append({
            "id": str(uuid.uuid4()),
            "name": u["name"],
            "email": u["email"],
            "password": pwd_context.hash(u["password"]),
            "role": u["role"],
            "matricula": u.get("matricula"),
            "active": True,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        })

    # Logs de exemplo (últimas 48h)
    results = ["permitido", "permitido", "permitido", "negado"]
    now = datetime.utcnow()
    for _ in range(30):
        u = random.choice(users)
        loc = random.choice(locations)
        result = random.choice(results)
        access_logs.append({
            "id": str(uuid.uuid4()),
            "user_id": u["id"],
            "user_name": u["name"],
            "user_role": u["role"],
            "location_id": loc["id"],
            "location_name": loc["name"],
            "result": result,
            "reason": "Sem permissão para este local" if result == "negado" else None,
            "timestamp": (now - timedelta(seconds=random.randint(0, 172800))).isoformat(),
            "device_ip": f"192.168.1.{random.randint(10, 60)}",
        })

    access_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    print(f"[DB] Seed concluído: {len(users)} usuários, {len(access_logs)} logs")
