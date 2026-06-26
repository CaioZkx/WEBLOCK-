# 🔒 WebLock — Backend Python + FastAPI

## Como rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar o banco de dados (PostgreSQL)

Você tem duas opções:

**Opção A — Supabase (recomendado, gratuito):**
- Crie uma conta em [supabase.com](https://supabase.com)
- Crie um novo projeto e copie a `DATABASE_URL` disponível em *Project Settings → Database*

**Opção B — Local com Docker:**
```bash
docker run --name weblock-db -e POSTGRES_PASSWORD=senha123 -e POSTGRES_DB=weblock -p 5432:5432 -d postgres
```

### 3. Criar o arquivo .env
Crie um arquivo `.env` na pasta `backend/` com:
```
DATABASE_URL=postgresql://usuario:senha@host:5432/nome_do_banco
SECRET_KEY=weblock_jwt_secret_2024_seguro
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8
```

Se usou o Docker local, a `DATABASE_URL` fica assim:
```
DATABASE_URL=postgresql://postgres:senha123@localhost:5432/weblock
```

### 4. Rodar o servidor
```bash
uvicorn main:app --reload --port 8000
```

> Na primeira execução, as tabelas são criadas automaticamente e o banco é populado com dados iniciais (5 usuários, 5 locais e 30 logs de exemplo).

A API estará em: http://localhost:8000  
Documentação automática (Swagger): http://localhost:8000/docs

## Credenciais padrão
- **Email:** admin@weblock.ufc.br  
- **Senha:** admin123

## Endpoints
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /api/auth/login | Login JWT |
| GET | /api/auth/me | Usuário logado |
| GET/POST/PUT/DELETE | /api/users | CRUD Usuários |
| GET | /api/logs | Logs de acesso |
| GET | /api/analytics | Métricas |
| GET/POST/PUT | /api/locations | Locais |
| POST | /api/lock/access | Decisão de acesso |
| POST | /api/lock/event | Eventos da fechadura |

---

## 🧪 Como rodar os testes

Os testes usam **SQLite** automaticamente — não é necessário ter o banco PostgreSQL rodando.

### Pré-requisito: instalar as dependências
```bash
pip install -r requirements.txt
```

### Rodar todos os testes
Dentro da pasta `backend/`:
```bash
pytest tests/ -v
```

### Rodar os testes de um módulo específico
```bash
# Autenticação
pytest tests/test_auth.py -v

# Usuários
pytest tests/test_users.py -v

# Fechadura (controle de acesso)
pytest tests/test_lock.py -v

# Logs de auditoria
pytest tests/test_logs.py -v

# Locais
pytest tests/test_locations.py -v

# Analytics / Dashboard
pytest tests/test_analytics.py -v
```

### O que esperar na saída
```
tests/test_analytics.py::test_admin_acessa_dashboard PASSED
tests/test_analytics.py::test_professor_acessa_dashboard PASSED
tests/test_analytics.py::test_aluno_acessa_dashboard PASSED
...
```

> **Obs:** cada teste roda com um banco limpo e repovoado automaticamente pelo `conftest.py`, garantindo isolamento entre os testes.

---

## ⚠️ Atenção
O frontend React (pasta `frontend/`) deve apontar para a porta **8000** agora.  
Edite `frontend/vite.config.js` e troque:
```js
proxy: { '/api': 'http://localhost:3001' }
// para:
proxy: { '/api': 'http://localhost:8000' }
```
