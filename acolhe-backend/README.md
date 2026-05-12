# Acolhe.app — Backend

API construída com **FastAPI + PostgreSQL + WebSockets**.

## Estrutura

```
acolhe-backend/
├── app/
│   ├── core/
│   │   ├── config.py        # Configurações e variáveis de ambiente
│   │   └── database.py      # Conexão com PostgreSQL
│   ├── models/
│   │   └── models.py        # Tabelas do banco de dados
│   ├── schemas/
│   │   └── schemas.py       # Validação de dados (Pydantic)
│   ├── services/
│   │   ├── matchmaking.py   # Lógica de conectar usuários
│   │   └── websocket_manager.py  # Gerenciador de chat em tempo real
│   ├── routers/
│   │   ├── users.py         # Criar usuário anônimo
│   │   ├── conversations.py # Match, chat, encerrar
│   │   └── safety.py        # Denúncias e bloqueios
│   └── main.py              # Entrada da aplicação
├── requirements.txt
└── .env.example
```

## Como rodar

### 1. Pré-requisitos
- Python 3.11+
- PostgreSQL rodando localmente
- (Opcional) Redis para sessões futuras

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env com suas credenciais do PostgreSQL
```

### 4. Criar o banco de dados no PostgreSQL
```sql
CREATE DATABASE acolhe;
```

### 5. Rodar a aplicação
```bash
uvicorn app.main:app --reload
```

A API estará disponível em: http://localhost:8000

Documentação automática: http://localhost:8000/docs

## Endpoints principais

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | /users/ | Criar usuário anônimo |
| PATCH | /users/{id}/listening | Marcar como disponível |
| POST | /conversations/match | Buscar parceiro |
| GET | /conversations/{id}/messages | Histórico |
| POST | /conversations/{id}/end | Encerrar conversa |
| WS | /conversations/ws/{conv_id}/{user_id} | Chat em tempo real |
| POST | /safety/report | Denunciar usuário |
| POST | /safety/block | Bloquear usuário |

## WebSocket — como usar

Conecte em: `ws://localhost:8000/conversations/ws/{conversation_id}/{user_id}`

**Enviar mensagem de texto:**
```json
{ "type": "text", "content": "Olá, tudo bem?" }
```

**Enviar áudio:**
```json
{ "type": "audio", "audio_url": "url_do_arquivo_de_audio" }
```
