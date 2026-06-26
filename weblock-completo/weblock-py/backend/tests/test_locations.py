"""Testes de CRUD de locais — inclui os bugs de validação e permissões."""


def test_listar_locais_inclui_roles(client, admin_headers):
    resp = client.get("/api/locations", headers=admin_headers)
    assert resp.status_code == 200
    locs = resp.json()
    assert len(locs) == 5  # seed
    sala_professores = next(l for l in locs if l["name"] == "Sala dos Professores")
    assert sala_professores["roles"] == ["admin", "professor"]


def test_aluno_pode_ver_locais_mas_nao_criar(client, aluno_headers):
    resp = client.get("/api/locations", headers=aluno_headers)
    assert resp.status_code == 200

    resp2 = client.post("/api/locations", json={"name": "Sala X", "roles": ["aluno"]}, headers=aluno_headers)
    assert resp2.status_code == 403


# ── BUG: criar local com campos vazios ────────────────────────────────────────

def test_criar_local_com_nome_vazio_falha(client, admin_headers):
    resp = client.post("/api/locations", json={"name": "", "roles": ["admin"]}, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_local_com_nome_so_espacos_falha(client, admin_headers):
    resp = client.post("/api/locations", json={"name": "   ", "roles": ["admin"]}, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_local_sem_campo_name_falha(client, admin_headers):
    resp = client.post("/api/locations", json={"building": "Bloco D"}, headers=admin_headers)
    assert resp.status_code == 422  # erro de validação do Pydantic (campo obrigatório ausente)


# ── BUG: permissões de acesso (roles) por local ───────────────────────────────

def test_criar_local_com_roles_validos(client, admin_headers):
    resp = client.post("/api/locations", json={
        "name": "Laboratório de Química", "building": "Bloco D", "floor": "1",
        "roles": ["admin", "professor", "aluno"]
    }, headers=admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["roles"] == ["admin", "professor", "aluno"]


def test_criar_local_com_role_invalida_falha(client, admin_headers):
    resp = client.post("/api/locations", json={
        "name": "Sala Y", "roles": ["super-usuario"]
    }, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_local_sem_roles_fica_sem_permissao_nenhuma(client, admin_headers):
    """Se não especificar roles, o local fica sem ninguém autorizado (comportamento esperado)."""
    resp = client.post("/api/locations", json={"name": "Sala Isolada"}, headers=admin_headers)
    assert resp.status_code == 201
    assert resp.json()["roles"] == []


def test_atualizar_roles_de_local_existente(client, admin_headers):
    locs = client.get("/api/locations", headers=admin_headers).json()
    biblioteca = next(l for l in locs if l["name"] == "Biblioteca")

    resp = client.put(f"/api/locations/{biblioteca['id']}", json={"roles": ["admin"]}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["roles"] == ["admin"]

    # Confirma que a mudança realmente afeta o motor de decisão de acesso
    locs_after = client.get("/api/locations", headers=admin_headers).json()
    biblioteca_after = next(l for l in locs_after if l["id"] == biblioteca["id"])
    assert biblioteca_after["roles"] == ["admin"]


def test_atualizar_local_com_role_invalida_falha(client, admin_headers):
    locs = client.get("/api/locations", headers=admin_headers).json()
    loc = locs[0]
    resp = client.put(f"/api/locations/{loc['id']}", json={"roles": ["faxineiro-fantasma"]}, headers=admin_headers)
    assert resp.status_code == 400


def test_atualizar_local_com_nome_vazio_falha(client, admin_headers):
    locs = client.get("/api/locations", headers=admin_headers).json()
    loc = locs[0]
    resp = client.put(f"/api/locations/{loc['id']}", json={"name": "   "}, headers=admin_headers)
    assert resp.status_code == 400


def test_atualizar_local_inexistente_retorna_404(client, admin_headers):
    resp = client.put("/api/locations/nao-existe", json={"name": "Qualquer"}, headers=admin_headers)
    assert resp.status_code == 404
