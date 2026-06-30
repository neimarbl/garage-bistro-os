# backend/app/routers/chamado_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Tipo assíncrono correto
from app.core.database import get_async_db         # 🔄 CORREÇÃO: Importação corrigida
from app.repositories.chamado_repository import ChamadoRepository
from app.core.websocket_manager import notifier

router = APIRouter(prefix="/chamados", tags=["Chamados & Alertas (Salão)"])

class NovoChamadoRequest(BaseModel):
    mesa_id: int
    tipo: str  # "duvida" ou "maquininha"

@router.post("/", status_code=status.HTTP_201_CREATED)
async def abrir_chamado(payload: NovoChamadoRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Aberto pelo cliente via celular. Salva no DB e alerta os garçons via WebSocket na LAN.
    """
    if payload.tipo not in ["duvida", "maquininha"]:
        raise HTTPException(status_code=400, detail="Tipo de chamado inválido.")

    repo = ChamadoRepository(db)
    # 🔄 CORREÇÃO: Adicionado await para chamada assíncrona do repositório
    chamado = await repo.criar_chamado(mesa_id=payload.mesa_id, tipo=payload.tipo)

    # 📡 TRANSMISSÃO EM TEMPO REAL: Alerta todos os garçons logados na rede local
    await notifier.broadcast_to_group("garcons", {
        "evento": "novo_chamado",
        "chamado_id": chamado.id,
        "mesa_id": payload.mesa_id,
        "tipo": payload.tipo,
        "alerta": f"A Mesa {payload.mesa_id} solicitou atenção! Motivo: {payload.tipo.upper()}."
    })

    return {"message": "Garçom acionado! Um membro da equipe já está a caminho."}

# 🔄 CORREÇÃO: Convertido para async def para evitar bloqueio de concorrência local
@router.post("/{chamado_id}/atender", status_code=status.HTTP_200_OK)
async def encerrar_chamado(chamado_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Executado pelo garçom no celular dele ao chegar na mesa para dar baixa no alerta.
    """
    repo = ChamadoRepository(db)
    # 🔄 CORREÇÃO: Adicionado await na execução da baixa do chamado
    chamado_atendido = await repo.atender_chamado(chamado_id)
    if not chamado_atendido:
        raise HTTPException(status_code=404, detail="Chamado não encontrado.")
    return {"message": "Chamado finalizado com sucesso."}
