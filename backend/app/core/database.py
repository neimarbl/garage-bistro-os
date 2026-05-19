# backend/app/core/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Recupera a URL do banco das variáveis de ambiente do Docker com um fallback seguro
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://garage_admin:secure_password_change_me@db-master:5432/garage_bistro_prod"
)

# O engine é o gerenciador de conexões físicas com o banco do Docker
engine = create_engine(
    DATABASE_URL,
    # Configurações recomendadas para evitar conexões presas ou lentas na rede local
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# O SessionLocal age como uma fábrica de sessões de conversação com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Injetor de Dependência (Dependency Injection) para o FastAPI.
    Garante que cada requisição do celular do garçom abra uma conexão única 
    com o banco e a feche imediatamente após o término do pedido, evitando vazamento de memória.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
