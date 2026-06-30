# backend/app/core/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 🔄 CORREÇÃO: O driver assíncrono do psycopg exige o prefixo 'postgresql+psycopg' na URL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://postgres:postgres@db-master:5432/garage_bistro"
)

# 🔄 CORREÇÃO: Utiliza o create_async_engine para conexões sem bloqueio de thread (Non-blocking)
engine = create_async_engine(
    DATABASE_URL,
    pool_size=15,          # Otimizado para alta concorrência de smartphones corporativos
    max_overflow=25,
    pool_pre_ping=True
)

# 🔄 CORREÇÃO: Utiliza o async_sessionmaker para fabricar sessões assíncronas AsyncSession
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    class_=AsyncSession
)

# 🔄 CORREÇÃO: Função renomeada para get_async_db acompanhando o modificador async/await
async def get_async_db():
    """
    Injetor de Dependência Assíncrono para o FastAPI.
    Garante concorrência nativa via asyncio para osPWAs de atendimento e TVs da garagem,
    liberando a conexão imediatamente de forma assíncrona após cada operação.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
