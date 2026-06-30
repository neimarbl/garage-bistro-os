# backend/app/main.py
from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Importação de TODOS os roteadores do ecossistema do Bistrô
from app.routers.atendimento_router import router as atendimento_router 
from app.routers.pedido_router import router as pedido_router 
from app.routers.chamado_router import router as chamado_router 
from app.routers.producao_router import router as producao_router 
from app.routers.financeiro_router import router as financeiro_router
from app.routers.estoque_router import router as estoque_router
from app.routers.evento_router import router as evento_router
from app.models.database_models import Base
Base.__allow_unmapped__ = True

# 🔄 CORREÇÃO: Removido o Base.metadata.create_all(bind=engine) síncrono que quebrava o motor assíncrono.
# A criação de tabelas e sementes (seed) já está garantida via PostgreSQL Master e Alembic.

app = FastAPI(
    title="Garage Bistro OS",
    description="Sistema de Gestão de Fluxo de Pedidos e Insumos do Garage Bistrô",
    version="0.1.0"
)

# Configuração Dinâmica Avançada de CORS para Redes Locais LAN (Omnichannel)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra TODOS os módulos no ecossistema ativo do FastAPI
app.include_router(atendimento_router)
app.include_router(pedido_router)
app.include_router(chamado_router)
app.include_router(producao_router)
app.include_router(financeiro_router)
app.include_router(estoque_router)
app.include_router(evento_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Bem-vindo ao motor de gerenciamento do Garage Bistrô."
    }
