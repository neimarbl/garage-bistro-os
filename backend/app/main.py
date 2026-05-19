# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.atendimento_router import router as atendimento_router 
from app.core.database import engine
from app.models.database_models import Base
from app.routers.pedido_router import router as pedido_router 

# Cria as tabelas fisicamente no banco do Docker se elas não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Garage Bistro OS",
    description="Sistema de Gestão de Fluxo de Pedidos e Insumos do Garage Bistrô",
    version="0.1.0"
)

# Configuração de CORS para permitir que o Frontend acesse a API na rede local LAN
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção local, mapear os IPs específicos dos dispositivos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas de atendimento no ecossistema do FastAPI
app.include_router(atendimento_router)
app.include_router(pedido_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Bem-vindo ao motor de gerenciamento do Garage Bistrô."
    }
