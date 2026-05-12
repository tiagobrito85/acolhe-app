from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, conversations, safety
from app.core.database import engine, Base

app = FastAPI(
    title="Acolhe.app API",
    description="Backend do Acolhe — conexão humana anônima e gratuita.",
    version="0.1.0"
)

# CORS — permite o frontend se conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque pelo domínio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router)
app.include_router(conversations.router)
app.include_router(safety.router)

@app.on_event("startup")
async def startup():
    # Cria as tabelas se não existirem
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {
        "app": "Acolhe.app",
        "status": "online",
        "mensagem": "Você não precisa estar sozinho."
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
