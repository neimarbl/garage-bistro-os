# backend/app/routers/estoque_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Tipo assíncrono correto
from datetime import datetime
from typing import List
from app.core.database import get_async_db         # 🔄 CORREÇÃO: Importação corrigida
from app.repositories.estoque_repository import EstoqueRepository

router = APIRouter(prefix="/estoque", tags=["Almoxarifado & Estoque Crítico"])

class EntradaInsumoRequest(BaseModel):
    insumo_id: int
    quantidade: float
    data_validade: str # Formato YYYY-MM-DD
    congelado: bool = False

# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.post("/entrada", status_code=status.HTTP_200_OK)
async def dar_entrada_mercadoria(payload: EntradaInsumoRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Registra as compras feitas no atacado diretamente no saldo do estoque.
    """
    try:
        validade_dt = datetime.strptime(payload.data_validade, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

    repo = EstoqueRepository(db)
    # 🔄 CORREÇÃO: Adicionado await na chamada assíncrona do repositório
    insumo = await repo.registrar_entrada_atacado(
        insumo_id=payload.insumo_id,
        quantidade=payload.quantidade,
        data_validade=validade_dt,
        congelado=payload.congelado
    )
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não localizado no cadastro.")
    return {"message": f"Entrada de {payload.quantidade} unidades de {insumo.nome} registrada!"}

# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.get("/alertas", status_code=status.HTTP_200_OK)
async def obter_alertas_estoque(db: AsyncSession = Depends(get_async_db)):
    """
    Painel de alertas: varre validades de porções congeladas e itens abaixo do mínimo.
    """
    repo = EstoqueRepository(db)
    # 🔄 CORREÇÃO: Adicionado await para busca assíncrona
    return await repo.listar_alertas_criticos()

# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.get("/alertas-criticos", status_code=status.HTTP_200_OK)
async def obter_alertas_almoxarifado(db: AsyncSession = Depends(get_async_db)):
    """
    Varre os lotes físicos do PostgreSQL gerando matrizes preventivas de perdas e validades.
    """
    # 🔄 CORREÇÃO: Adicionado await na chamada de método estático assíncrono da classe
    return await EstoqueRepository.calcular_alertas_criticos(db)
