# 🔒 WebLock — Backend Python + FastAPI

## Como rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Criar o arquivo .env
Crie um arquivo `.env` na pasta `backend/` com:
```
SECRET_KEY=weblock_jwt_secret_2024_seguro
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8
```

### 3. Rodar o servidor
```bash
uvicorn main:app --reload --port 8000
```

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

## ⚠️ Atenção
O frontend React (pasta `frontend/`) deve apontar para a porta **8000** agora.  
Edite `frontend/vite.config.js` e troque:
```js
proxy: { '/api': 'http://localhost:3001' }
// para:
proxy: { '/api': 'http://localhost:8000' }
```
