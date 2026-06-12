from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.repositories.producao_repository import ProducaoRepository
from app.models.database_models import StatusItem
from app.core.websocket_manager import notifier
from app.repositories.estoque_repository import EstoqueRepository

router = APIRouter(prefix="/producao", tags=["KDS & Produção (Cozinha/Bar)"])

@router.get("/fila", status_code=status.HTTP_200_OK)
def obtener_fila(bebidas: bool = False, db: Session = Depends(get_db)):
    """
    Retorna a lista de itens na fila do KDS. ?bebidas=true (Bar) ou false (Cozinha).
    """
    repo = ProducaoRepository(db)
    itens = repo.listar_fila_producao(apenas_bebidas=bebidas)
    
    return [{
        "item_id": item.id,
        "pedido_id": item.pedido_id,
        "mesa": item.pedido.mesa.numero_identificador if item.pedido.mesa else 0,
        "comanda_pvc": item.pedido.comanda.numero_pvc if item.pedido.comanda else 0,
        "produto": item.produto.nome,
        "quantidade": item.quantidade,
        "observacao": item.observacao,
        "status": item.status.value,
        "minutos_espera": int((datetime.utcnow() - item.pedido.criado_em).total_seconds() / 60) if item.pedido.criado_em else 0
    } for item in itens]

@router.post("/item/{item_id}/avancar", status_code=status.HTTP_200_OK)
async def avancar_estagio_item(item_id: int, db: Session = Depends(get_db)):
    """
    Muda o status do item no KDS via teclado USB. Alerta o garçom via WebSocket se ficar PRONTO.
    """
    repo = ProducaoRepository(db)
    item_atual = db.query(item_id).filter_by(id=item_id).first()
    if not item_atual:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
        
    proximo_status = StatusItem.EM_PREPARO
    if item_atual.status == StatusItem.EM_PREPARO:
        proximo_status = StatusItem.PRONTO
        # ⚡ BAIXA AUTOMÁTICA DE ESTOQUE: O prato ficou pronto, desconta os ingredientes brutos
        estoque_repo = EstoqueRepository(db)
        estoque_repo.descontar_estoque_por_produto(
            produto_id=item_atual.produto_id,
            quantidade_pedido=item_atual.quantidade
        )
    elif item_atual.status == StatusItem.PRONTO:
        proximo_status = StatusItem.ENTREGUE

    item_atualizado = repo.atualizar_status_item(item_id, proximo_status)
    
    if proximo_status == StatusItem.PRONTO and item_atualizado.pedido.mesa:
        await notifier.broadcast_to_group("garcons", {
            "evento": "item_pronto",
            "item_id": item_id,
            "mesa": item_atualizado.pedido.mesa.numero_identificador,
            "produto": item_atualizado.produto.nome,
            "alerta": f"🚨 Retirar: {item_atualizado.produto.nome} da Mesa {item_atualizado.pedido.mesa.numero_identificador} está PRONTO!"
        })
        
    return {"message": f"Status atualizado para {proximo_status.value}."}
