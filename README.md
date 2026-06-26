# 🔒 WebLock — Backend Python + FastAPI

## 📁 Estrutura do Projeto

```
weblock-completo/
├── weblock-py/
│   ├── backend/
│   │   ├── main.py                  # Entrada da aplicação
│   │   ├── database_config.py       # Conexão com o banco
│   │   ├── requirements.txt         # Dependências Python
│   │   ├── .env                     # Variáveis de ambiente (criar manualmente)
│   │   ├── routers/                 # Endpoints da API
│   │   │   ├── auth.py              # Login e autenticação
│   │   │   ├── users.py             # CRUD de usuários
│   │   │   ├── lock.py              # Controle de acesso físico
│   │   │   ├── logs.py              # Logs de auditoria
│   │   │   ├── analytics.py         # Métricas e dashboard
│   │   │   └── locations.py         # Gerenciamento de locais
│   │   ├── models/
│   │   │   ├── orm_models.py        # Modelos do banco (SQLAlchemy)
│   │   │   ├── schemas.py           # Schemas de entrada/saída (Pydantic)
│   │   │   └── seed.py              # Dados iniciais do banco
│   │   ├── services/
│   │   │   └── auth.py              # JWT, hash de senha, guards de permissão
│   │   └── tests/                   # Testes unitários por módulo
│   └── frontend/                    # Interface React
```

---

## 🚀 Como rodar

### 1. Instalar dependências
Dentro da pasta `backend/`:
```bash
pip install -r requirements.txt
```

### 2. Configurar o banco de dados (PostgreSQL)

Você tem duas opções:

**Opção A — Supabase (recomendado, gratuito, sem instalar nada):**
- Crie uma conta em [supabase.com](https://supabase.com)
- Clique em **New Project**, defina um nome e uma senha
- Após criar, vá em **Project Settings → Database → Connection string → URI**
- Copie a URL no formato: `postgresql://postgres:SENHA@db.xxxx.supabase.co:5432/postgres`

**Opção B — Local com Docker:**
```bash
docker run --name weblock-db -e POSTGRES_PASSWORD=senha123 -e POSTGRES_DB=weblock -p 5432:5432 -d postgres
```
> ⚠️ Requer que a **virtualização esteja ativada** na BIOS. Se aparecer o erro "Virtualization support not detected", use a Opção A.

### 3. Criar o arquivo .env
Crie um arquivo `.env` dentro da pasta `backend/` com:
```
DATABASE_URL=postgresql://usuario:senha@host:5432/nome_do_banco
SECRET_KEY=weblock_jwt_secret_2024_seguro
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8
```

Exemplo com Docker local:
```
DATABASE_URL=postgresql://postgres:senha123@localhost:5432/weblock
```

### 4. Rodar o backend
```bash
uvicorn main:app --reload --port 8000
```

> Na primeira execução, as tabelas são criadas automaticamente e o banco é populado com dados iniciais (seed).

A API estará disponível em: http://localhost:8000  
Documentação interativa (Swagger): http://localhost:8000/docs

### 5. Rodar o frontend (em outro terminal)
```bash
cd ../frontend
npm install
npm run dev
```

O frontend estará disponível em: http://localhost:5173

> ⚠️ Se o frontend não conectar no backend, edite `frontend/vite.config.js` e certifique-se que o proxy aponta para a porta 8000:
> ```js
> proxy: { '/api': 'http://localhost:8000' }
> ```

---

## 🗃️ Povoamento inicial do banco (Seed)

Na primeira execução, o sistema cria automaticamente os seguintes dados:

### Usuários criados

| Nome | Email | Senha | Perfil | Matrícula |
|------|-------|-------|--------|-----------|
| Administrador | admin@weblock.ufc.br | admin123 | admin | ADM0001 |
| Prof. João Silva | joao.silva@ufc.br | senha123 | professor | PROF001 |
| Maria Oliveira | maria.oliveira@ufc.br | senha123 | aluno | 2021001 |
| Carlos Souza | carlos.souza@ufc.br | senha123 | aluno | 2022003 |
| Ana Lima | ana.lima@ufc.br | senha123 | terceirizado | TERC01 |

### Locais criados

| Local | Bloco | Andar | Perfis com acesso |
|-------|-------|-------|-------------------|
| Laboratório de Informática 1 | Bloco A | 1 | admin, professor, aluno |
| Laboratório de Informática 2 | Bloco A | 2 | admin, professor, aluno |
| Sala de Aula 101 | Bloco B | 1 | admin, professor, aluno, terceirizado |
| Biblioteca | Bloco C | 1 | admin, professor, aluno, terceirizado |
| Sala dos Professores | Bloco B | 2 | admin, professor |

Além disso, são gerados **30 logs de acesso aleatórios** distribuídos nas últimas 48 horas, respeitando as regras de permissão de cada local.

---

## 🔐 Permissões por perfil

### 👑 Admin
- Acesso **irrestrito** a todos os locais, independente das permissões configuradas
- Criar, editar e desativar usuários
- Criar, editar e desativar locais
- Ver todos os logs de acesso
- Ver o dashboard de analytics
- Ver, listar e buscar qualquer usuário

### 👨‍🏫 Professor
- Acesso aos locais: Laboratórios, Sala de Aula, Biblioteca e Sala dos Professores
- Listar e buscar usuários
- Ver todos os logs de acesso
- Ver o dashboard de analytics
- ❌ Não pode criar, editar ou remover usuários
- ❌ Não pode criar, editar ou remover locais

### 🎓 Aluno
- Acesso aos locais: Laboratórios, Sala de Aula e Biblioteca
- Ver o próprio perfil
- ❌ Não pode acessar a Sala dos Professores
- ❌ Não pode listar outros usuários
- ❌ Não pode ver logs
- ❌ Não pode ver o dashboard de analytics

### 🧹 Terceirizado
- Acesso aos locais: Sala de Aula e Biblioteca
- Ver o próprio perfil
- ❌ Não pode acessar Laboratórios nem Sala dos Professores
- ❌ Não pode listar outros usuários
- ❌ Não pode ver logs
- ❌ Não pode ver o dashboard de analytics

---

## 📡 Endpoints

| Método | Rota | Descrição | Acesso mínimo |
|--------|------|-----------|---------------|
| POST | /api/auth/login | Login JWT | Público |
| GET | /api/auth/me | Usuário logado | Qualquer autenticado |
| GET | /api/users | Listar usuários | Admin / Professor |
| GET | /api/users/{id} | Buscar usuário | Qualquer autenticado |
| POST | /api/users | Criar usuário | Admin |
| PUT | /api/users/{id} | Editar usuário | Admin |
| DELETE | /api/users/{id} | Remover usuário | Admin |
| GET | /api/locations | Listar locais | Qualquer autenticado |
| POST | /api/locations | Criar local | Admin |
| PUT | /api/locations/{id} | Editar local | Admin |
| GET | /api/logs | Listar logs | Qualquer autenticado |
| GET | /api/logs/{id} | Ver log específico | Qualquer autenticado |
| GET | /api/analytics | Dashboard | Qualquer autenticado |
| POST | /api/lock/access | Decisão de acesso | Público (chamado pelo hardware) |
| POST | /api/lock/event | Evento da fechadura | Público (chamado pelo hardware) |

---

## 🧪 Como rodar os testes

Os testes usam **SQLite em memória** automaticamente — não é necessário ter o banco PostgreSQL rodando.

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

> **Obs:** cada teste roda com um banco limpo e repovoado automaticamente pelo `conftest.py`, garantindo isolamento total entre os testes.
