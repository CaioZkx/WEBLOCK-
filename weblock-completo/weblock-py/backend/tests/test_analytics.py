"""Testes do dashboard/analytics — inclui o bug de acesso por perfil que corrigimos."""


# ── BUG: dashboard não aparecia para aluno/terceirizado ───────────────────────

def test_admin_acessa_dashboard(client, admin_headers):
    resp = client.get("/api/analytics", headers=admin_headers)
    assert resp.status_code == 200


def test_professor_acessa_dashboard(client, professor_headers):
    resp = client.get("/api/analytics", headers=professor_headers)
    assert resp.status_code == 200


def test_aluno_acessa_dashboard(client, aluno_headers):
    resp = client.get("/api/analytics", headers=aluno_headers)
    assert resp.status_code == 200


def test_terceirizado_acessa_dashboard(client, terceirizado_headers):
    resp = client.get("/api/analytics", headers=terceirizado_headers)
    assert resp.status_code == 200


def test_dashboard_sem_autenticacao_falha(client):
    resp = client.get("/api/analytics")
    assert resp.status_code in (401, 403)


# ── Estrutura dos dados retornados ────────────────────────────────────────────

def test_analytics_tem_estrutura_esperada(client, admin_headers):
    resp = client.get("/api/analytics?period=30d", headers=admin_headers)
    body = resp.json()
    assert "kpis" in body
    assert "byLocation" in body
    assert "byRole" in body
    assert "byHour" in body
    assert "byDay" in body
    assert "topUsers" in body
    assert len(body["byHour"]) == 24


def test_analytics_kpis_consistentes(client, admin_headers):
    body = client.get("/api/analytics?period=30d", headers=admin_headers).json()
    kpis = body["kpis"]
    assert kpis["total"] == kpis["permitidos"] + kpis["negados"]


def test_analytics_periodo_invalido_usa_padrao(client, admin_headers):
    """Período não reconhecido cai no padrão (7d) em vez de quebrar."""
    resp = client.get("/api/analytics?period=periodo-bizarro", headers=admin_headers)
    assert resp.status_code == 200
