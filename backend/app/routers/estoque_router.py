# backend/app/routers/estoque_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from app.core.database import get_db
from app.repositories.estoque_repository import EstoqueRepository

router = APIRouter(prefix="/estoque", tags=["Almoxarifado & Estoque Crítico"])

class EntradaInsumoRequest(BaseModel):
    insumo_id: int
    quantidade: float
    data_validade: str # Formato YYYY-MM-DD
    congelado: bool = False

@router.post("/entrada", status_code=status.HTTP_200_OK)
def dar_entrada_mercadoria(payload: EntradaInsumoRequest, db: Session = Depends(get_db)):
    """
    Registra as compras feitas no atacado diretamente no saldo do estoque.
    """
    try:
        validade_dt = datetime.strptime(payload.data_validade, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

    repo = EstoqueRepository(db)
    insumo = repo.registrar_entrada_atacado(
        insumo_id=payload.insumo_id,
        quantidade=payload.quantidade,
        data_validade=validade_dt,
        congelado=payload.congelado
    )
    if not insumo:
        raise HTTPException(status_code=404, detail="Insumo não localizado no cadastro.")
    return {"message": f"Entrada de {payload.quantidade} unidades de {insumo.nome} registrada!"}

@router.get("/alertas", status_code=status.HTTP_200_OK)
def obter_alertas_estoque(db: Session = Depends(get_db)):
    """
    Painel de alertas: varre validades de porções congeladas e itens abaixo do mínimo.
    """
    repo = EstoqueRepository(db)
    return repo.listar_alertas_criticos()
