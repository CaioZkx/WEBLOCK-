"""
Popula o banco com dados iniciais — só roda se as tabelas estiverem vazias.
Substitui o seed() em memória de models/database.py.
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models.orm_models import User, Location, AccessPermission, AccessLog

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_LOCATIONS = [
    {"name": "Laboratório de Informática 1", "building": "Bloco A", "floor": "1", "roles": ["admin", "professor", "aluno"]},
    {"name": "Laboratório de Informática 2", "building": "Bloco A", "floor": "2", "roles": ["admin", "professor", "aluno"]},
    {"name": "Sala de Aula 101",             "building": "Bloco B", "floor": "1", "roles": ["admin", "professor", "aluno", "terceirizado"]},
    {"name": "Biblioteca",                   "building": "Bloco C", "floor": "1", "roles": ["admin", "professor", "aluno", "terceirizado"]},
    {"name": "Sala dos Professores",         "building": "Bloco B", "floor": "2", "roles": ["admin", "professor"]},
]

DEFAULT_USERS = [
    {"name": "Administrador",    "email": "admin@weblock.ufc.br",  "password": "admin123", "role": "admin",        "matricula": "ADM0001"},
    {"name": "Prof. João Silva", "email": "joao.silva@ufc.br",     "password": "senha123", "role": "professor",    "matricula": "PROF001"},
    {"name": "Maria Oliveira",   "email": "maria.oliveira@ufc.br", "password": "senha123", "role": "aluno",        "matricula": "2021001"},
    {"name": "Carlos Souza",     "email": "carlos.souza@ufc.br",   "password": "senha123", "role": "aluno",        "matricula": "2022003"},
    {"name": "Ana Lima",         "email": "ana.lima@ufc.br",       "password": "senha123", "role": "terceirizado", "matricula": "TERC01"},
]


def seed(db: Session):
    if db.query(User).count() > 0:
        print("[DB] Seed ignorado: já existem dados.")
        return

    users = []
    for u in DEFAULT_USERS:
        user = User(
            name=u["name"], email=u["email"],
            password=pwd_context.hash(u["password"]),
            role=u["role"], matricula=u.get("matricula"), active=True,
        )
        db.add(user)
        users.append(user)
    db.flush()  # garante que os IDs já existem antes de criar os logs

    locations = []
    for loc_data in DEFAULT_LOCATIONS:
        loc = Location(name=loc_data["name"], building=loc_data["building"], floor=loc_data["floor"], active=True)
        db.add(loc)
        db.flush()
        for role in loc_data["roles"]:
            db.add(AccessPermission(location_id=loc.id, role=role))
        locations.append(loc)

# Mapeia location -> roles permitidos, pra gerar logs que respeitam a regra real
    loc_roles = {loc.id: data["roles"] for loc, data in zip(locations, DEFAULT_LOCATIONS)}

    now = datetime.utcnow()
    for _ in range(30):
        u = random.choice(users)
        loc = random.choice(locations)
        allowed = u.role == "admin" or u.role in loc_roles.get(loc.id, [])
        result = "permitido" if allowed else "negado"
        db.add(AccessLog(
            user_id=u.id, user_name=u.name, user_role=u.role,
            location_id=loc.id, location_name=loc.name,
            result=result,
            reason="Sem permissão para este local" if result == "negado" else None,
            timestamp=now - timedelta(seconds=random.randint(0, 172800)),
            device_ip=f"192.168.1.{random.randint(10, 60)}",
        ))

    db.commit()
    print(f"[DB] Seed concluído: {len(users)} usuários, {len(locations)} locais, 30 logs")
