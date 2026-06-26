# Testes Unitários — WebLock Backend

## Como rodar

Dentro da pasta `backend/`:

```powershell
pip install -r requirements.txt
pytest
```

Saída esperada: `68 passed`.

Para ver mais detalhes de cada teste:
```powershell
pytest -v
```

Para rodar só um arquivo específico:
```powershell
pytest tests/test_lock.py
```

## O que cada arquivo testa

| Arquivo | Cobre |
|---|---|
| `test_auth.py` | Login, token JWT, usuário inativo |
| `test_users.py` | CRUD de usuários, campos vazios, exclusão permanente, permissões por role |
| `test_locations.py` | CRUD de locais, validação de nome vazio, permissões (roles) por local |
| `test_lock.py` | Motor de decisão de acesso — permitido/negado, cartão não cadastrado, usuário/local inexistente, geração de logs |
| `test_logs.py` | Consulta e filtro de logs de auditoria |
| `test_analytics.py` | Dashboard — acesso liberado pra todos os perfis, estrutura dos dados |

## Como funciona o reset entre testes

Como o "banco de dados" é só listas Python em memória, o `conftest.py` tem uma fixture `reset_database` com `autouse=True` que limpa e repovoa tudo (`seed()`) **antes de cada teste**. Isso garante que um teste nunca interfere no outro.

## Bugs cobertos pelos testes

Esses testes existem especificamente porque eram bugs encontrados e corrigidos durante o desenvolvimento:

1. ✅ Dashboard não aparecia para aluno/terceirizado → `test_analytics.py`
2. ✅ Locais criados sem opção de definir permissão → `test_locations.py`
3. ✅ Não era possível excluir usuário de fato (só desativava) → `test_users.py`
4. ✅ Usuário podia ser criado com campos vazios → `test_users.py`
5. ✅ Local podia ser criado com campos vazios → `test_locations.py`
