# 🔒 WebLock — Sistema de Controle de Acesso

Sistema completo de controle de acesso físico (fechaduras eletrônicas) desenvolvido para a disciplina de Engenharia da Computação — UFC Sobral. Permite gerenciar usuários, locais, permissões de acesso por perfil, auditoria de tentativas de entrada e um dashboard com métricas em tempo real.

---

## 📋 Sumário

- [Visão geral](#-visão-geral)
- [Stack utilizada](#-stack-utilizada)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Como rodar](#-como-rodar)
- [Configuração do banco de dados](#-configuração-do-banco-de-dados)
- [Povoamento inicial (seed)](#-povoamento-inicial-seed)
- [Regras de negócio](#-regras-de-negócio)
- [Permissões por perfil](#-permissões-por-perfil)
- [Endpoints da API](#-endpoints-da-api)
- [Telas do frontend](#-telas-do-frontend)
- [Como rodar os testes](#-como-rodar-os-testes)
- [Solução de problemas comuns](#-solução-de-problemas-comuns)

---

## 🧭 Visão geral

O WebLock simula a arquitetura de um sistema de controle de acesso baseado em fechaduras eletrônicas conectadas a uma API central. O fluxo principal é:

1. Uma fechadura (ou, neste projeto, a tela **Simular Acesso**) envia uma tentativa de entrada com o ID do usuário/cartão e o ID do local.
2. O **motor de decisão de acesso** (`/api/lock/access`) verifica se o perfil do usuário tem permissão configurada para aquele local.
3. A decisão (permitido/negado) é registrada automaticamente em um **log de auditoria**.
4. O **dashboard** consolida esses logs em métricas (acessos por dia, por hora, por local, por perfil).

---

## 🛠 Stack utilizada

**Backend**
- Python 3.11+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL (via Supabase ou local)
- JWT (`python-jose`) para autenticação
- Bcrypt (`passlib`) para hash de senhas
- Pytest + SQLite em memória para testes

**Frontend**
- React 18 + Vite
- React Router
- Axios
- Recharts (gráficos do dashboard)
- Lucide React (ícones)

---

## 📁 Estrutura do projeto

```
weblock-completo/
├── weblock-py/
│   ├── backend/
│   │   ├── main.py                  # Entrada da aplicação — registra rotas e roda o seed
│   │   ├── database_config.py       # Engine, SessionLocal e Base do SQLAlchemy
│   │   ├── requirements.txt         # Dependências Python
│   │   ├── pytest.ini               # Configuração do pytest
│   │   ├── .env                     # Variáveis de ambiente (criar manualmente)
│   │   ├── routers/
│   │   │   ├── auth.py              # Login (JWT) e /me
│   │   │   ├── users.py             # CRUD de usuários + validações
│   │   │   ├── lock.py              # Motor de decisão de acesso (permitir/negar)
│   │   │   ├── logs.py              # Consulta e filtro de logs de auditoria
│   │   │   ├── analytics.py         # Métricas agregadas para o dashboard
│   │   │   └── locations.py         # CRUD de locais + permissões por perfil
│   │   ├── models/
│   │   │   ├── orm_models.py        # Tabelas: User, Location, AccessPermission, AccessLog
│   │   │   ├── schemas.py           # Schemas Pydantic de entrada/saída
│   │   │   └── seed.py              # Dados iniciais (só roda se o banco estiver vazio)
│   │   ├── services/
│   │   │   └── auth.py              # Geração/validação de JWT, hash de senha, guards de permissão
│   │   └── tests/
│   │       ├── conftest.py          # Fixtures + banco SQLite isolado para testes
│   │       ├── test_auth.py
│   │       ├── test_users.py
│   │       ├── test_locations.py
│   │       ├── test_lock.py
│   │       ├── test_logs.py
│   │       └── test_analytics.py
│   └── README.md
└── weblock/
    └── frontend/
        ├── index.html
        ├── vite.config.js
        └── src/
            ├── main.jsx                       # Rotas da aplicação
            ├── context/AuthContext.jsx        # Estado do usuário logado + token JWT
            ├── services/api.js                # Chamadas HTTP (axios) para a API
            ├── components/layout/Layout.jsx   # Sidebar + navegação
            └── pages/
                ├── LoginPage.jsx
                ├── DashboardPage.jsx
                ├── LogsPage.jsx
                ├── UsersPage.jsx
                ├── LocationsPage.jsx
                └── SimulatePage.jsx
```

---

## 🚀 Como rodar

### 1. Backend

Dentro da pasta `weblock-py/backend/`:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` (veja [Configuração do banco de dados](#-configuração-do-banco-de-dados)) e depois rode:

```bash
python -m uvicorn main:app --reload --port 8000
```

> ⚠️ **Importante:** o comando precisa ser executado de dentro da pasta `backend/`, nunca de dentro de `routers/` ou de outra subpasta — senão o uvicorn não encontra o `main.py`.

Na primeira execução as tabelas são criadas automaticamente e o banco é populado com o seed.

- API: http://localhost:8000
- Documentação interativa (Swagger): http://localhost:8000/docs
- Especificação OpenAPI crua (útil para depurar cache do navegador): http://localhost:8000/openapi.json

### 2. Frontend

Em outro terminal, dentro de `weblock/frontend/`:

```bash
npm install
npm run dev
```

- Frontend: http://localhost:3000

Confirme que `frontend/vite.config.js` aponta o proxy para a porta certa do backend:

```js
server: { port: 3000, proxy: { '/api': 'http://localhost:8000' } }
```

### 3. Login

| Email | Senha | Perfil |
|---|---|---|
| `admin@weblock.ufc.br` | `admin123` | admin |

---

## 🗄 Configuração do banco de dados

O projeto usa **PostgreSQL**. Duas opções:

### Opção A — Supabase (recomendado, gratuito)

1. Crie uma conta em [supabase.com](https://supabase.com) e um novo projeto.
2. No painel do projeto, clique no botão **Connect** (canto superior direito).
3. Escolha a aba de **connection string** no modo **Session pooler** e copie a URI.
4. Substitua `[YOUR-PASSWORD]` pela senha do banco definida na criação do projeto.

```
postgresql://postgres:SUA_SENHA@db.xxxxxxxxxxxx.supabase.co:5432/postgres
```

> Se sua senha tiver caracteres especiais (`@ # $ % & + / : ? = !`), eles precisam ser codificados em formato de URL (ex: `!` → `%21`, `@` → `%40`) para não quebrar a connection string.

### Opção B — Local com Docker

```bash
docker run --name weblock-db -e POSTGRES_PASSWORD=senha123 -e POSTGRES_DB=weblock -p 5432:5432 -d postgres
```

> Requer virtualização ativada na BIOS. Se aparecer erro de "Virtualization support not detected", use a Opção A.

### Arquivo `.env`

Crie `backend/.env`:

```
DATABASE_URL=postgresql://usuario:senha@host:5432/nome_do_banco
SECRET_KEY=weblock_jwt_secret_2024_seguro
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8
```

---

## 🌱 Povoamento inicial (seed)

O seed só roda **uma vez**, na primeira inicialização com o banco vazio (`if db.query(User).count() > 0: return`). Para forçar um novo seed, apague as tabelas no Supabase (SQL Editor):

```sql
DELETE FROM access_logs;
DELETE FROM access_permissions;
DELETE FROM locations;
DELETE FROM users;
```

### Usuários criados

| Nome | Email | Senha | Perfil | Matrícula |
|---|---|---|---|---|
| Administrador | admin@weblock.ufc.br | admin123 | admin | ADM0001 |
| Prof. João Silva | joao.silva@ufc.br | senha123 | professor | PROF001 |
| Maria Oliveira | maria.oliveira@ufc.br | senha123 | aluno | 2021001 |
| Carlos Souza | carlos.souza@ufc.br | senha123 | aluno | 2022003 |
| Ana Lima | ana.lima@ufc.br | senha123 | terceirizado | TERC01 |

### Locais criados

| Local | Bloco | Andar | Perfis com acesso configurado |
|---|---|---|---|
| Laboratório de Informática 1 | Bloco A | 1 | professor, aluno *(+ admin sempre)* |
| Laboratório de Informática 2 | Bloco A | 2 | professor, aluno *(+ admin sempre)* |
| Sala de Aula 101 | Bloco B | 1 | professor, aluno, terceirizado *(+ admin sempre)* |
| Biblioteca | Bloco C | 1 | professor, aluno, terceirizado *(+ admin sempre)* |
| Sala dos Professores | Bloco B | 2 | professor *(+ admin sempre)* |

Além disso, são gerados **30 logs de acesso** com timestamps aleatórios nas últimas 48h, já respeitando a regra real de permissão de cada local (ou seja, os logs de exemplo não são aleatórios quanto ao resultado — eles simulam um histórico coerente).

---

## ⚖️ Regras de negócio

- **Admin sempre acessa qualquer local**, independente do que estiver configurado nas permissões daquele local. A opção "Admin" não aparece como checkbox marcável na tela de Locais — é uma regra fixa do sistema.
- **Email deve ter formato válido** (`usuario@dominio.com`) tanto na criação quanto na edição de usuário — apenas conter `@` não é suficiente.
- **Matrícula é obrigatória** na criação de um usuário.
- **Nome, email e senha não podem ser vazios** (nem só espaços) na criação de usuário.
- **Email duplicado é bloqueado** (`409 Conflict`) — o login busca o usuário pelo email, então ele precisa ser único.
- **Local duplicado é bloqueado**: não é possível criar dois locais com o mesmo nome + bloco + andar (`409 Conflict`).
- **Exclusão de usuário e de local** suporta dois modos:
  - Sem parâmetro (`DELETE /api/users/{id}`) → *soft delete*, o registro só é marcado como `active: false`, mas continua existindo.
  - Com `?permanent=true` → exclusão definitiva do banco.
- **Usuário inativo (soft-deleted) não consegue logar** e qualquer tentativa de acesso física é automaticamente negada.
- **Tentativa de acesso sem `userId`** (cartão não cadastrado) gera um log com resultado negado e motivo `"Cartão não cadastrado"`, sem quebrar a aplicação.
- **Timestamps no banco são sempre em UTC.** A conversão para horário de Brasília (UTC-3) é feita na camada de apresentação:
  - No frontend (`LogsPage`), o `toLocaleString('pt-BR')` do JavaScript já faz a conversão automaticamente.
  - No backend (`analytics.py`), os agrupamentos por hora e por dia subtraem manualmente 3 horas antes de agrupar.

---

## 🔐 Permissões por perfil

### 👑 Admin
- Acesso irrestrito a todos os locais.
- CRUD completo de usuários e locais.
- Visualiza logs, dashboard e pode simular o acesso de qualquer usuário (incluindo "cartão não cadastrado").

### 👨‍🏫 Professor
- Acesso configurável aos locais (por padrão: laboratórios, sala de aula, biblioteca e sala dos professores).
- Pode listar e buscar usuários (somente leitura).
- Visualiza logs e dashboard.
- ❌ Não pode criar, editar ou remover usuários e locais.

### 🎓 Aluno
- Acesso configurável aos locais (por padrão: laboratórios, sala de aula e biblioteca).
- Visualiza logs e dashboard.
- Na tela **Simular Acesso**, só pode testar o **próprio acesso** em diferentes locais (não pode escolher outro usuário).
- ❌ Não pode listar outros usuários, nem gerenciar usuários/locais.

### 🧹 Terceirizado
- Acesso configurável aos locais (por padrão: sala de aula e biblioteca).
- Mesmas restrições do aluno: simula apenas o próprio acesso, sem listagem de usuários.

---

## 📡 Endpoints da API

| Método | Rota | Descrição | Acesso mínimo |
|---|---|---|---|
| POST | `/api/auth/login` | Login (retorna JWT) | Público |
| GET | `/api/auth/me` | Dados do usuário logado | Qualquer autenticado |
| GET | `/api/users` | Listar usuários (filtros: `role`, `active`, `search`) | Admin / Professor |
| GET | `/api/users/{id}` | Buscar usuário por ID | Qualquer autenticado |
| POST | `/api/users` | Criar usuário | Admin |
| PUT | `/api/users/{id}` | Editar usuário | Admin |
| DELETE | `/api/users/{id}` | Desativar usuário (ou excluir com `?permanent=true`) | Admin |
| GET | `/api/locations` | Listar locais (inclui `roles` configurados) | Qualquer autenticado |
| POST | `/api/locations` | Criar local | Admin |
| PUT | `/api/locations/{id}` | Editar local / permissões | Admin |
| DELETE | `/api/locations/{id}` | Desativar local (ou excluir com `?permanent=true`) | Admin |
| GET | `/api/logs` | Listar logs (filtros: `user_id`, `location_id`, `result`, datas, paginação) | Qualquer autenticado |
| GET | `/api/logs/{id}` | Ver log específico | Qualquer autenticado |
| GET | `/api/analytics` | Métricas do dashboard (parâmetro `period`: `24h`, `7d`, `30d`) | Qualquer autenticado |
| POST | `/api/lock/access` | Decisão de acesso (chamado pela fechadura/simulação) | Público |
| POST | `/api/lock/event` | Evento genérico da fechadura (porta forçada, etc.) | Público |
| GET | `/api/health` | Healthcheck | Público |

---

## 🖥 Telas do frontend

| Tela | Arquivo | Descrição |
|---|---|---|
| Login | `LoginPage.jsx` | Autenticação com email/senha |
| Dashboard | `DashboardPage.jsx` | KPIs e gráficos (Recharts): acessos por dia, hora, local, perfil |
| Logs de Acesso | `LogsPage.jsx` | Tabela paginada com filtro por resultado |
| Usuários | `UsersPage.jsx` | CRUD de usuários, incluindo status (ativo/inativo) |
| Locais | `LocationsPage.jsx` | CRUD de locais com checkboxes de permissão por perfil |
| Simular Acesso | `SimulatePage.jsx` | Simula uma tentativa de acesso na fechadura; admin/professor escolhem qualquer usuário, aluno/terceirizado só simulam o próprio acesso |

---

## 🧪 Como rodar os testes

Os testes usam **SQLite em memória** automaticamente, isolado do banco de produção (Supabase) — não é necessário ter o PostgreSQL rodando para testar.

Dentro de `backend/`:

```bash
python -m pytest
```

Para rodar um módulo específico:

```bash
python -m pytest tests/test_lock.py -v
```

Cada teste roda com o banco resetado e repovoado automaticamente (`conftest.py`, fixture `reset_database` com `autouse=True`), garantindo isolamento total entre os testes.

### Cobertura por arquivo

| Arquivo | Cobre |
|---|---|
| `test_auth.py` | Login, JWT, usuário inativo |
| `test_users.py` | CRUD, validações (email, matrícula, campos vazios), exclusão permanente vs. soft delete |
| `test_locations.py` | CRUD, validação de duplicidade, permissões (roles) por local |
| `test_lock.py` | Motor de decisão de acesso — permitido/negado, cartão não cadastrado, geração de logs |
| `test_logs.py` | Listagem, filtro e paginação de logs |
| `test_analytics.py` | Acesso ao dashboard por todos os perfis, estrutura dos dados retornados |
