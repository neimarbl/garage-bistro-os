# backend/app/routers/pedido_router.py
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.pedido_repository import PedidoRepository
from app.models.database_models import OrigemPedido
from app.core.websocket_manager import notifier # Importa o gerenciador de tempo real

router = APIRouter(prefix="/pedidos", tags=["Pedidos & Produção (KDS)"])

class ItemPedidoInput(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)
    observacao: Optional[str] = None

class NovoPedidoRequest(BaseModel):
    mesa_id: int
    comanda_id: int
    origem: OrigemPedido = OrigemPedido.GARCON # Diferencia se veio do Garçom ou Cliente via QR Code
    itens: List[ItemPedidoInput]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def lançar_pedido(payload: NovoPedidoRequest, db: Session = Depends(get_db)):
    """
    Registra o pedido e avisa a cozinha/bar instantaneamente via WebSocket se vier do cliente.
    """
    if not payload.itens:
        raise HTTPException(status_code=400, detail="O pedido deve conter itens.")
        
    repo = PedidoRepository(db)
    itens_dict = [item.model_dump() for item in payload.itens]
    
    # Passamos o campo origem adaptado ao novo banco
    pedido = repo.criar_pedido(
        mesa_id=payload.mesa_id,
        comanda_id=payload.comanda_id,
        itens_data=itens_dict
    )
    
    # ⚡ NOTIFICAÇÃO EM TEMPO REAL: Se o cliente pediu pelo celular, a cozinha/bar avisa na hora
    if payload.origem == OrigemPedido.AUTOATENDIMENTO:
        await notifier.broadcast_to_group("cozinha", {
            "evento": "novo_pedido_autoatendimento",
            "mesa_id": payload.mesa_id,
            "pedido_id": pedido.id,
            "alerta": f"Novo pedido digital recebido da Mesa {payload.mesa_id}!"
        })
    
    return {"message": "Pedido processado com sucesso!", "pedido_id": pedido.id}

# 📡 ENDPOINT WEBSOCKET: Celulares dos garçons e tela do caixa se conectam aqui para ouvir alertas
@router.websocket("/ws/{grupo}")
async def websocket_endpoint(websocket: WebSocket, grupo: str):
    if grupo not in ["garcons", "caixa", "cozinha", "clientes"]:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    await notifier.connect(websocket, grupo)
    try:
        while True:
            # Mantém a conexão aberta escutando batimentos de coração (ping/pong) ou dados
            data = await websocket.receive_json()
            # Se um garçom responder um chamado, pode enviar dados por aqui
    except WebSocketDisconnect:
        notifier.disconnect(websocket, grupo)
