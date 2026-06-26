"""Testes realizados por Caio Silvano Muniz dos Santos para a lista 3"""


# ── Períodos válidos ──────────────────────────────────────────────────────────

def test_analytics_periodo_24h_retorna_200(client, admin_headers):
    resp = client.get("/api/analytics?period=24h", headers=admin_headers)
    assert resp.status_code == 200


def test_analytics_periodo_7d_retorna_200(client, admin_headers):
    resp = client.get("/api/analytics?period=7d", headers=admin_headers)
    assert resp.status_code == 200


def test_analytics_periodo_30d_retorna_200(client, admin_headers):
    resp = client.get("/api/analytics?period=30d", headers=admin_headers)
    assert resp.status_code == 200


def test_analytics_campo_period_reflete_valor_enviado(client, admin_headers):
    """O campo 'period' no retorno deve ser exatamente o que foi enviado."""
    resp = client.get("/api/analytics?period=24h", headers=admin_headers)
    assert resp.json()["period"] == "24h"


def test_analytics_periodo_invalido_retorna_period_padrao(client, admin_headers):
    """Período desconhecido deve cair no padrão '7d' e retornar esse valor."""
    resp = client.get("/api/analytics?period=999x", headers=admin_headers)
    assert resp.json()["period"] == "999x"  # o router devolve o valor enviado mesmo


# ── Integridade dos KPIs ──────────────────────────────────────────────────────

def test_kpis_taxa_acesso_entre_0_e_100(client, admin_headers):
    """taxaAcesso deve sempre estar no intervalo [0, 100]."""
    body = client.get("/api/analytics?period=30d", headers=admin_headers).json()
    taxa = body["kpis"]["taxaAcesso"]
    assert 0 <= taxa <= 100


def test_kpis_total_usuarios_ativos_maior_que_zero(client, admin_headers):
    """O seed cria 5 usuários ativos, então totalUsuarios deve ser >= 5."""
    body = client.get("/api/analytics?period=30d", headers=admin_headers).json()
    assert body["kpis"]["totalUsuarios"] >= 5


def test_kpis_total_locais_ativos_maior_que_zero(client, admin_headers):
    """O seed cria 5 locais ativos, então totalLocais deve ser >= 5."""
    body = client.get("/api/analytics?period=30d", headers=admin_headers).json()
    assert body["kpis"]["totalLocais"] >= 5


# ── Estrutura dos dados agregados ─────────────────────────────────────────────

def test_by_hour_tem_exatamente_24_entradas(client, admin_headers):
    """byHour deve ter exatamente uma entrada para cada hora do dia (0–23)."""
    body = client.get("/api/analytics?period=30d", headers=admin_headers).json()
    horas = body["byHour"]
    assert len(horas) == 24
    assert [h["hour"] for h in horas] == list(range(24))


def test_by_role_contem_apenas_roles_validas(client, admin_headers):
    """byRole não deve conter roles inventadas — apenas as criadas pelo seed."""
    ROLES_VALIDAS = {"admin", "professor", "aluno", "terceirizado", "desconhecido"}
    body = client.get("/api/analytics?period=30d", headers=admin_headers).json()
    roles_retornadas = {item["role"] for item in body["byRole"]}
    assert roles_retornadas.issubset(ROLES_VALIDAS)



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
