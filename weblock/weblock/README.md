# 🔒 WebLock — Sistema de Controle de Acesso

## Estrutura do Projeto
```
weblock/
├── backend/          # API REST Node.js + Express
│   └── src/
│       ├── controllers/  # Auth, Users, Lock, Logs, Analytics, Locations
│       ├── middlewares/  # JWT Auth
│       ├── models/       # Banco em memória + seed
│       ├── routes/       # Todas as rotas
│       └── server.js
└── frontend/         # React + Vite
    └── src/
        ├── pages/     # Login, Dashboard, Logs, Users, Locations, Simulate
        ├── components/# Layout com sidebar
        ├── context/   # AuthContext (JWT)
        └── services/  # API axios
```

## Como rodar

### Backend
```bash
cd backend
npm install
npm start   # http://localhost:3001
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

## Credenciais padrão
- **Email:** admin@weblock.ufc.br
- **Senha:** admin123

## Endpoints da API
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /api/auth/login | Login JWT |
| GET | /api/auth/me | Usuário logado |
| GET/POST/PUT/DELETE | /api/users | CRUD Usuários |
| GET | /api/logs | Logs de acesso |
| GET | /api/analytics | Métricas/Dashboard |
| GET/POST/PUT | /api/locations | Locais/Salas |
| POST | /api/lock/access | Decisão de acesso (hardware) |
| POST | /api/lock/event | Eventos da fechadura |

## Perfis de acesso
- **admin** — Acesso total
- **professor** — Acesso a labs e salas
- **aluno** — Acesso a labs e salas comuns
- **terceirizado** — Acesso apenas a áreas comuns
