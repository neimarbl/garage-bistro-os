# backend/app/routers/atendimento_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.repositories.atendimento_repository import AtendimentoRepository

# Dependência simulada para o Banco de Dados (será conectada ao engine global depois)
def get_db():
    raise NotImplementedError("Conexão real com DB pendente de injeção global")

router = APIRouter(prefix="/atendimento", tags=["Atendimento / Salão"])

# Esquemas de validação de dados com Pydantic (Garantia de tipos de entrada)
class AgrupamentoMesasRequest(BaseModel):
    numero_mesa_principal: int
    numeros_mesas_adicionais: List[int]

class AtivarComandaRequest(BaseModel):
    numero_pvc: int

@router.post("/mesas/agrupar", status_code=status.HTTP_200_OK)
def agrupar_mesas(payload: AgrupamentoMesasRequest, db: Session = Depends(get_db)):
    """
    Agrupa mesas de forma lógica para atender grupos grandes ou aniversários na garagem.
    """
    repo = AtendimentoRepository(db)
    mesa = repo.agrupar_mesas(payload.numero_mesa_principal, payload.numeros_mesas_adicionais)
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa principal não encontrada.")
    return {"message": "Mesas agrupadas com sucesso no mapa do salão."}

@router.post("/comandas/ativar", status_code=status.HTTP_201_CREATED)
def ativar_comanda(payload: AtivarComandaRequest, db: Session = Depends(get_db)):
    """
    Associa e ativa um cartão de PVC físico ao fluxo de consumo de um cliente.
    """
    repo = AtendimentoRepository(db)
    comanda = repo.ativar_comanda_pvc(payload.numero_pvc)
    return {
        "comanda_id": comanda.id,
        "numero_pvc": comanda.numero_pvc,
        "status": comanda.status.value
    }
