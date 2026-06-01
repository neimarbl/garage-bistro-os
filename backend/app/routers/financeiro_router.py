from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.financeiro_repository import FinanceiroRepository
from app.core.websocket_manager import notifier

router = APIRouter(prefix="/financeiro", tags=["Financeiro & Fechamento de Contas"])

class PagamentoRequest(BaseModel):
    comanda_id: int
    valor: float
    metodo: str # "pix", "credito", "debito", "dinheiro"
    transacao_id: str = None

@router.get("/comanda/{comanda_id}/extrato")
def obter_extrato(comanda_id: int, cover: float = 0.0, db: Session = Depends(get_db)):
    """
    Exibe a prévia da conta com consumo + 10% + cover artístico.
    """
    repo = FinanceiroRepository(db)
    return repo.calcular_extrato_comanda(comanda_id=comanda_id, valor_cover=cover)

@router.post("/pagar-fracionado", status_code=status.HTTP_201_CREATED)
async def pagar_fracionado(payload: PagamentoRequest, db: Session = Depends(get_db)):
    """
    Registra pagamentos parciais e alerta garçons/caixa em tempo real via WebSocket.
    """
    repo = FinanceiroRepository(db)
    pagamento = repo.registrar_pagamento_parcial(
        comanda_id=payload.comanda_id,
        valor=payload.valor,
        metodo=payload.metodo,
        transacao_id=payload.transacao_id
    )

    if payload.metodo == "pix":
        await notifier.broadcast_to_group("caixa", {
            "evento": "pix_recebido",
            "comanda_id": payload.comanda_id,
            "alerta": f"✅ PIX de R$ {payload.valor} recebido da Comanda {payload.comanda_id}!"
        })
    elif payload.metodo in ["credito", "debito"]:
        await notifier.broadcast_to_group("garcons", {
            "evento": "chamar_maquininha",
            "comanda_id": payload.comanda_id,
            "alerta": f"💳 Levar maquininha para receber R$ {payload.valor} na Comanda {payload.comanda_id}."
        })

    return {"message": "Pagamento registrado!", "extrato": repo.calcular_extrato_comanda(payload.comanda_id)}
