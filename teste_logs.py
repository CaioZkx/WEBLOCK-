"""
Testes da API de consulta de logs de auditoria.

Cobre a listagem paginada, filtros, busca por ID específico e 
as regras de autenticação e autorização do endpoint de logs.
"""

def test_listar_logs_retorna_paginado(client, admin_headers):
    """
    Verifica se a listagem de logs respeita os parâmetros de paginação ('page' e 'limit').
    Garante que a quantidade de logs retornados não exceda o limite solicitado 
    e que a página atual seja indicada corretamente no payload de resposta.
    """
    resp = client.get("/api/logs?page=1&limit=5", headers=admin_headers)
    
    assert resp.status_code == 200
    
    body = resp.json()
    assert len(body["logs"]) <= 5
    assert body["page"] == 1


def test_filtrar_logs_por_resultado(client, admin_headers):
    """
    Testa a funcionalidade de filtro de logs utilizando a query string 'result'.
    Assegura que, ao buscar por 'negado', absolutamente todos os registros 
    retornados na lista possuam esse mesmo status.
    """
    resp = client.get("/api/logs?result=negado", headers=admin_headers)
    
    assert resp.status_code == 200
    
    body = resp.json()
    assert all(log["result"] == "negado" for log in body["logs"])


def test_buscar_log_por_id(client, admin_headers):
    """
    Valida a busca detalhada de um único log de auditoria via path parameter (ID).
    Busca um log existente na listagem geral e verifica se o endpoint de 
    detalhes retorna exatamente o mesmo recurso solicitado.
    """
    # Arrange: Obtém um ID válido a partir da listagem geral
    logs = client.get("/api/logs", headers=admin_headers).json()["logs"]
    log_id = logs[0]["id"]

    # Act & Assert: Busca o log específico e valida os dados
    resp = client.get(f"/api/logs/{log_id}", headers=admin_headers)
    
    assert resp.status_code == 200
    assert resp.json()["id"] == log_id


def test_buscar_log_inexistente_retorna_404(client, admin_headers):
    """
    Garante que a API trata adequadamente a busca por recursos inexistentes.
    Deve retornar o status HTTP 404 (Not Found) quando um ID de log 
    inválido ou não cadastrado for fornecido.
    """
    resp = client.get("/api/logs/nao-existe", headers=admin_headers)
    
    assert resp.status_code == 404


def test_logs_exige_autenticacao(client):
    """
    Verifica a segurança básica do endpoint.
    Garante que requisições sem os cabeçalhos de autenticação apropriados 
    sejam bloqueadas retornando erro 401 (Unauthorized) ou 403 (Forbidden).
    """
    resp = client.get("/api/logs")
    
    assert resp.status_code in (401, 403)


def test_aluno_pode_ver_logs(client, aluno_headers):
    """
    Valida as regras de autorização (RBAC).
    Os logs de auditoria não são de uso exclusivo para administradores ou 
    professores. Garante que um usuário logado com perfil de 'aluno' também 
    possa acessar o endpoint com sucesso (HTTP 200).
    """
    resp = client.get("/api/logs", headers=aluno_headers)
    
    assert resp.status_code == 200
