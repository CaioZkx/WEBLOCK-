"""Testes de login e validação de token JWT."""
"""Testes realizados por Emilly Bezerra Ximenes para a lista 3"""


def test_login_com_credenciais_corretas_retorna_token(client):
    resp = client.post("/api/auth/login", json={"email": "admin@weblock.ufc.br", "password": "admin123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "token" in body
    assert body["user"]["email"] == "admin@weblock.ufc.br"
    assert body["user"]["role"] == "admin"
    assert "password" not in body["user"]  # nunca deve devolver o hash da senha


def test_login_com_senha_errada_falha(client):
    resp = client.post("/api/auth/login", json={"email": "admin@weblock.ufc.br", "password": "senhaerrada"})
    assert resp.status_code == 401


def test_login_com_email_inexistente_falha(client):
    resp = client.post("/api/auth/login", json={"email": "naoexiste@weblock.ufc.br", "password": "qualquer"})
    assert resp.status_code == 401


def test_login_usuario_inativo_falha(client, admin_headers):
    # Cria e desativa um usuário, depois tenta logar com ele
    client.post("/api/users", json={
        "name": "Temp", "email": "temp@ufc.br", "password": "123456", "role": "aluno",
        "matricula": "2024101"
    }, headers=admin_headers)
    users_resp = client.get("/api/users", headers=admin_headers).json()["users"]
    temp = next(u for u in users_resp if u["email"] == "temp@ufc.br")
    client.delete(f"/api/users/{temp['id']}", headers=admin_headers)

    resp = client.post("/api/auth/login", json={"email": "temp@ufc.br", "password": "123456"})
    assert resp.status_code == 401


def test_me_com_token_valido_retorna_usuario(client, admin_headers):
    resp = client.get("/api/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@weblock.ufc.br"


def test_me_sem_token_retorna_401(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)  # depende de como o HTTPBearer reage sem header


def test_me_com_token_invalido_retorna_401(client):
    resp = client.get("/api/auth/me", headers={"Authorization": "Bearer token.invalido.aqui"})
    assert resp.status_code == 401

def test_login_sem_email_retorna_erro(client):
    resp = client.post("/api/auth/login", json={"password": "admin123"})
    assert resp.status_code == 422


def test_login_sem_senha_retorna_erro(client):
    resp = client.post("/api/auth/login", json={"email": "admin@weblock.ufc.br"})
    assert resp.status_code == 422


def test_login_payload_vazio_retorna_erro(client):
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 422


def test_login_retorna_token_nao_vazio(client):
    resp = client.post("/api/auth/login", json={"email": "admin@weblock.ufc.br", "password": "admin123"})
    token = resp.json()["token"]
    assert isinstance(token, str)
    assert len(token) > 20


def test_login_cada_perfil_recebe_token(client):
    credenciais = [
        ("admin@weblock.ufc.br",  "admin123"),
        ("joao.silva@ufc.br",     "senha123"),
        ("maria.oliveira@ufc.br", "senha123"),
        ("carlos.souza@ufc.br",   "senha123"),
        ("ana.lima@ufc.br",       "senha123"),
    ]
    for email, senha in credenciais:
        resp = client.post("/api/auth/login", json={"email": email, "password": senha})
        assert resp.status_code == 200
        assert "token" in resp.json()


def test_me_retorna_role_correto_para_aluno(client, aluno_headers):
    resp = client.get("/api/auth/me", headers=aluno_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "aluno"


def test_me_retorna_role_correto_para_terceirizado(client, terceirizado_headers):
    resp = client.get("/api/auth/me", headers=terceirizado_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "terceirizado"


def test_login_email_case_insensitive(client):
    resp = client.post("/api/auth/login", json={"email": "ADMIN@WEBLOCK.UFC.BR", "password": "admin123"})
    assert resp.status_code == 200
    assert "token" in resp.json()


def test_login_retorna_campos_obrigatorios_do_usuario(client):
    resp = client.post("/api/auth/login", json={"email": "admin@weblock.ufc.br", "password": "admin123"})
    user = resp.json()["user"]
    for campo in ("id", "name", "email", "role", "matricula", "active"):
        assert campo in user
    assert "password" not in user


def test_me_retorna_mesmo_usuario_do_login(client):
    login_resp = client.post("/api/auth/login", json={"email": "joao.silva@ufc.br", "password": "senha123"})
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    token = login_data["token"]
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["id"] == login_data["user"]["id"]
    assert me_data["email"] == login_data["user"]["email"]
    assert me_data["role"] == "professor"
