# backend/app/routers/pedido_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.pedido_repository import PedidoRepository

router = APIRouter(prefix="/pedidos", tags=["Pedidos & Produção (KDS)"])

# Esquemas Pydantic para validação rígida de entrada
class ItemPedidoInput(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0, description="A quantidade deve ser maior que zero")
    observacao: Optional[str] = None

class NovoPedidoRequest(BaseModel):
    mesa_id: int
    comanda_id: int
    itens: List[ItemPedidoInput]

@router.post("/", status_code=status.HTTP_201_CREATED)
def lançar_pedido(payload: NovoPedidoRequest, db: Session = Depends(get_db)):
    """
    Registra um novo pedido vindo do celular do garçom, direcionando itens para cozinha/bar.
    """
    if not payload.itens:
        raise HTTPException(status_code=400, detail="O pedido deve conter pelo menos um item.")
        
    repo = PedidoRepository(db)
    
    # Converte os schemas do Pydantic em dicionários puros para o repositório
    itens_dict = [item.model_dump() for item in payload.itens]
    
    pedido = repo.criar_pedido(
        mesa_id=payload.mesa_id,
        comanda_id=payload.comanda_id,
        itens_data=itens_dict
    )
    
    return {
        "message": "Pedido lançado com sucesso!",
        "pedido_id": pedido.id,
        "itens_lançados": len(pedido.itens)
    }
