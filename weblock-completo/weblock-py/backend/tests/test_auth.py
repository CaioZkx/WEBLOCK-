"""Testes de login e validação de token JWT."""


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
