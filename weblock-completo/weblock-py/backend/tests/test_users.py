"""Testes de CRUD de usuários — inclui os bugs corrigidos durante o desenvolvimento."""
#OBS.: Testes unitários foram adicionados por Breno neste código. Eles estão indicados mais abaixo com comentários.
#      Testes Unitários feitos por Francisco Breno Gomes Melo 

#===============================================================================
# Teste Feitos Francisco Breno Gomes Melo - Lista 3 (Engenharia de Software)
#===============================================================================

# ── Permissões de acesso ──────────────────────────────────────────────────────

def test_aluno_nao_pode_listar_usuarios(client, aluno_headers):
    # Verifica que o aluno não possui permissão para listar usuários
    resp = client.get("/api/users", headers=aluno_headers)
    assert resp.status_code == 403


def test_terceirizado_nao_pode_listar_usuarios(client, terceirizado_headers):
    # Verifica que o terceirizado não possui permissão para listar usuários
    resp = client.get("/api/users", headers=terceirizado_headers)
    assert resp.status_code == 403


def test_professor_pode_listar_usuarios(client, professor_headers):
    # Verifica que o professor possui permissão para listar usuários
    resp = client.get("/api/users", headers=professor_headers)
    assert resp.status_code == 200


def test_admin_pode_listar_usuarios(client, admin_headers):
    #Verifica que o admin pode listar todos os usuários
    resp = client.get("/api/users", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 5  # 5 usuários do seed


def test_aluno_nao_pode_criar_usuario(client, aluno_headers):
    # Verifica que o aluno não possui permissão para criar usuários
    resp = client.post("/api/users", json={
        "name": "Novo", "email": "novo@ufc.br", "password": "123456", "role": "aluno"
    }, headers=aluno_headers)
    assert resp.status_code == 403


def test_professor_nao_pode_criar_usuario(client, professor_headers):
    # Verifica que o professor não possui permissão para criar usuários
    resp = client.post("/api/users", json={
        "name": "Novo", "email": "novo@ufc.br", "password": "123456", "role": "aluno"
    }, headers=professor_headers)
    assert resp.status_code == 403


# ── BUG: criação de usuário com campos vazios ─────────────────────────────────

def test_criar_usuario_com_nome_vazio_falha(client, admin_headers):
    # Verifica que não é possível criar um usuário com nome vazio
    resp = client.post("/api/users", json={
        "name": "", "email": "vazio@ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_usuario_com_nome_so_espacos_falha(client, admin_headers):
    # Verifica que não é possível criar um usuário com nome contendo apenas espaços
    resp = client.post("/api/users", json={
        "name": "   ", "email": "vazio2@ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_usuario_com_email_vazio_falha(client, admin_headers):
    # Verifica que não é possível criar um usuário com email vazio
    resp = client.post("/api/users", json={
        "name": "Fulano", "email": "", "password": "123456", "role": "aluno"
    }, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_usuario_com_senha_vazia_falha(client, admin_headers):
    # Verifica que não é possível criar um usuário com senha vazio
    resp = client.post("/api/users", json={
        "name": "Fulano", "email": "fulano@ufc.br", "password": "", "role": "aluno"
    }, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_usuario_com_role_invalida_falha(client, admin_headers):
    # Verifica que não é possível criar um usuário com role inválida
    resp = client.post("/api/users", json={
        "name": "Fulano", "email": "fulano2@ufc.br", "password": "123456", "role": "super-admin"
    }, headers=admin_headers)
    assert resp.status_code == 400


def test_criar_usuario_com_email_duplicado_falha(client, admin_headers):
    # Verifica que não é possível criar um usuário com email já existente
    resp = client.post("/api/users", json={
        "name": "Duplicado", "email": "admin@weblock.ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers)
    assert resp.status_code == 409


def test_criar_usuario_valido_funciona(client, admin_headers):
    # Verifica que é possível criar um usuário válido
    resp = client.post("/api/users", json={
        "name": "Pedro Santos", "email": "pedro.santos@ufc.br", "password": "123456",
        "role": "aluno", "matricula": "2024099"
    }, headers=admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Pedro Santos"
    assert body["active"] is True
    assert "password" not in body


# ── Atualização ────────────────────────────────────────────────────────────────

def test_admin_pode_atualizar_usuario(client, admin_headers):
    # Verifica que o admin pode atualizar um usuário existente
    create = client.post("/api/users", json={
        "name": "Editar Eu", "email": "editar@ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers).json()

    resp = client.put(f"/api/users/{create['id']}", json={"name": "Nome Editado"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Nome Editado"


def test_atualizar_usuario_inexistente_retorna_404(client, admin_headers):
    # Verifica que atualizar um usuário inexistente retorna 404
    resp = client.put("/api/users/id-que-nao-existe", json={"name": "X"}, headers=admin_headers)
    assert resp.status_code == 404


# ── BUG: exclusão de usuário ──────────────────────────────────────────────────

def test_admin_nao_pode_remover_o_proprio_usuario(client, admin_headers):
    # Verifica que o admin não pode remover o próprio usuário
    me = client.get("/api/auth/me", headers=admin_headers).json()
    resp = client.delete(f"/api/users/{me['id']}", headers=admin_headers)
    assert resp.status_code == 400


def test_desativar_usuario_soft_delete(client, admin_headers):
    # Verifica que o usuário é desativado, mas continua na lista de usuários
    """Sem o parâmetro permanent, o usuário só é desativado (continua na lista)."""
    create = client.post("/api/users", json={
        "name": "Desativar", "email": "desativar@ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers).json()

    resp = client.delete(f"/api/users/{create['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert "desativado" in resp.json()["message"].lower()

    check = client.get(f"/api/users/{create['id']}", headers=admin_headers)
    assert check.status_code == 200
    assert check.json()["active"] is False


def test_excluir_usuario_permanentemente(client, admin_headers):
    """Com permanent=true, o usuário deixa de existir de fato."""
    create = client.post("/api/users", json={
        "name": "Excluir De Vez", "email": "excluirdevez@ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers).json()

    resp = client.delete(f"/api/users/{create['id']}?permanent=true", headers=admin_headers)
    assert resp.status_code == 200
    assert "permanentemente" in resp.json()["message"].lower()

    check = client.get(f"/api/users/{create['id']}", headers=admin_headers)
    assert check.status_code == 404


def test_excluir_usuario_inexistente_retorna_404(client, admin_headers):
    # Verifica que excluir um usuário inexistente retorna 404
    resp = client.delete("/api/users/nao-existe", headers=admin_headers)
    assert resp.status_code == 404


def test_aluno_nao_pode_excluir_usuario(client, aluno_headers, admin_headers):
    # Verifica que o aluno não pode excluir um usuário
    create = client.post("/api/users", json={
        "name": "Vitima", "email": "vitima@ufc.br", "password": "123456", "role": "aluno"
    }, headers=admin_headers).json()

    resp = client.delete(f"/api/users/{create['id']}", headers=aluno_headers)
    assert resp.status_code == 403


# ── Filtros de listagem ────────────────────────────────────────────────────────

def test_filtrar_usuarios_por_role(client, admin_headers):
    # Verifica que é possível filtrar usuários por role
    resp = client.get("/api/users?role=professor", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert all(u["role"] == "professor" for u in body["users"])


def test_buscar_usuario_por_nome(client, admin_headers):
    # Verifica que é possível buscar usuários por nome
    resp = client.get("/api/users?search=Maria", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert any("Maria" in u["name"] for u in body["users"])

