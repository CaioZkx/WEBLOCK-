"""Testes da consulta de logs de auditoria."""


def test_listar_logs_retorna_paginado(client, admin_headers):
    resp = client.get("/api/logs?page=1&limit=5", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["logs"]) <= 5
    assert body["page"] == 1


def test_filtrar_logs_por_resultado(client, admin_headers):
    resp = client.get("/api/logs?result=negado", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert all(l["result"] == "negado" for l in body["logs"])


def test_buscar_log_por_id(client, admin_headers):
    logs = client.get("/api/logs", headers=admin_headers).json()["logs"]
    log_id = logs[0]["id"]

    resp = client.get(f"/api/logs/{log_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == log_id


def test_buscar_log_inexistente_retorna_404(client, admin_headers):
    resp = client.get("/api/logs/nao-existe", headers=admin_headers)
    assert resp.status_code == 404


def test_logs_exige_autenticacao(client):
    resp = client.get("/api/logs")
    assert resp.status_code in (401, 403)


def test_aluno_pode_ver_logs(client, aluno_headers):
    """Logs não são restritos a admin/professor — qualquer logado pode auditar."""
    resp = client.get("/api/logs", headers=aluno_headers)
    assert resp.status_code == 200
