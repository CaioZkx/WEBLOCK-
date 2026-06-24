"""Testes do motor de decisão de acesso (fechadura) — POST /api/lock/access"""


def _get_user_id(client, admin_headers, email):
    users = client.get("/api/users", headers=admin_headers).json()["users"]
    return next(u for u in users if u["email"] == email)["id"]


def _get_location_id(client, admin_headers, name):
    locs = client.get("/api/locations", headers=admin_headers).json()
    return next(l for l in locs if l["name"] == name)["id"]


# ── Acesso permitido / negado por permissão de role ───────────────────────────

def test_admin_acessa_qualquer_local(client, admin_headers):
    admin_id = _get_user_id(client, admin_headers, "admin@weblock.ufc.br")
    loc_id = _get_location_id(client, admin_headers, "Sala dos Professores")

    resp = client.post("/api/lock/access", json={"userId": admin_id, "locationId": loc_id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is True
    assert body["reason"] is None


def test_aluno_negado_na_sala_dos_professores(client, admin_headers):
    aluno_id = _get_user_id(client, admin_headers, "maria.oliveira@ufc.br")
    loc_id = _get_location_id(client, admin_headers, "Sala dos Professores")

    resp = client.post("/api/lock/access", json={"userId": aluno_id, "locationId": loc_id})
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is False
    assert "permissão" in body["reason"].lower()


def test_terceirizado_negado_no_laboratorio(client, admin_headers):
    terc_id = _get_user_id(client, admin_headers, "ana.lima@ufc.br")
    loc_id = _get_location_id(client, admin_headers, "Laboratório de Informática 1")

    resp = client.post("/api/lock/access", json={"userId": terc_id, "locationId": loc_id})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


def test_terceirizado_permitido_na_biblioteca(client, admin_headers):
    terc_id = _get_user_id(client, admin_headers, "ana.lima@ufc.br")
    loc_id = _get_location_id(client, admin_headers, "Biblioteca")

    resp = client.post("/api/lock/access", json={"userId": terc_id, "locationId": loc_id})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_professor_permitido_no_laboratorio(client, admin_headers):
    prof_id = _get_user_id(client, admin_headers, "joao.silva@ufc.br")
    loc_id = _get_location_id(client, admin_headers, "Laboratório de Informática 2")

    resp = client.post("/api/lock/access", json={"userId": prof_id, "locationId": loc_id})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


# ── BUG: usuário não identificado / cartão desconhecido ───────────────────────

def test_acesso_sem_userid_eh_negado_como_nao_identificado(client):
    resp = client.post("/api/lock/access", json={"userId": None, "cardId": "CARD-99999", "locationId": "loc-001"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is False
    assert "não cadastrado" in body["reason"].lower()


def test_acesso_sem_userid_nem_cardid_ainda_eh_negado(client):
    resp = client.post("/api/lock/access", json={"locationId": "loc-001"})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


def test_acesso_com_userid_inexistente_eh_negado(client):
    resp = client.post("/api/lock/access", json={"userId": "id-fantasma", "locationId": "loc-001"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["allowed"] is False
    assert "usuário não encontrado" in body["reason"].lower()


def test_acesso_com_local_inexistente_eh_negado(client, admin_headers):
    admin_id = _get_user_id(client, admin_headers, "admin@weblock.ufc.br")
    resp = client.post("/api/lock/access", json={"userId": admin_id, "locationId": "local-fantasma"})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


def test_acesso_com_usuario_desativado_eh_negado(client, admin_headers):
    create = client.post("/api/users", json={
        "name": "Desativado Teste", "email": "desativadoteste@ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers).json()
    client.delete(f"/api/users/{create['id']}", headers=admin_headers)  # soft delete

    resp = client.post("/api/lock/access", json={"userId": create["id"], "locationId": "loc-001"})
    assert resp.status_code == 200
    assert resp.json()["allowed"] is False


# ── Cada tentativa gera um log de auditoria ───────────────────────────────────

def test_tentativa_de_acesso_gera_log(client, admin_headers):
    total_antes = client.get("/api/logs", headers=admin_headers).json()["total"]

    admin_id = _get_user_id(client, admin_headers, "admin@weblock.ufc.br")
    client.post("/api/lock/access", json={"userId": admin_id, "locationId": "loc-001"})

    total_depois = client.get("/api/logs", headers=admin_headers).json()["total"]
    assert total_depois == total_antes + 1


def test_log_de_acesso_negado_tem_motivo_preenchido(client, admin_headers):
    aluno_id = _get_user_id(client, admin_headers, "maria.oliveira@ufc.br")
    loc_id = _get_location_id(client, admin_headers, "Sala dos Professores")
    client.post("/api/lock/access", json={"userId": aluno_id, "locationId": loc_id})

    logs = client.get("/api/logs?result=negado", headers=admin_headers).json()["logs"]
    assert any(l["user_id"] == aluno_id and l["reason"] for l in logs)


# ── Evento genérico da fechadura ──────────────────────────────────────────────

def test_lock_event_eh_recebido(client):
    resp = client.post("/api/lock/event", json={
        "locationId": "loc-001", "eventType": "porta_forcada", "description": "Tentativa de arrombamento"
    })
    assert resp.status_code == 200
    assert resp.json()["received"] is True
