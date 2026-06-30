# backend/app/routers/producao_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Tipo assíncrono correto
from sqlalchemy.future import select                # 🔄 CORREÇÃO: Consultas em conformidade com SQLAlchemy 2.0
from datetime import datetime, timezone
from app.core.database import get_async_db         # 🔄 CORREÇÃO: Importação corrigida
from app.repositories.producao_repository import ProducaoRepository
from app.models.database_models import ItemPedido, StatusItem  # 🔄 CORREÇÃO: Importado ItemPedido para a consulta
from app.core.websocket_manager import notifier
from app.repositories.estoque_repository import EstoqueRepository

router = APIRouter(prefix="/producao", tags=["KDS & Produção (Cozinha/Bar)"])

# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.get("/fila", status_code=status.HTTP_200_OK)
async def obtener_fila(bebidas: bool = False, db: AsyncSession = Depends(get_async_db)):
    """
    Retorna a lista de itens na fila do KDS. ?bebidas=true (Bar) ou false (Cozinha).
    """
    repo = ProducaoRepository(db)
    # 🔄 CORREÇÃO: Adicionado await na chamada assíncrona do repositório
    # Importante: certifique-se de que o método interno use selectinload/joinedload para carregar produto e pedido
    itens = await repo.listar_fila_producao(apenas_bebidas=bebidas)
    
    return [{
        "item_id": item.id,
        "pedido_id": item.pedido_id,
        "mesa": item.pedido.mesa.numero_identificador if item.pedido.mesa else 0,
        "comanda_pvc": item.pedido.comanda.numero_pvc if item.pedido.comanda else 0,
        "produto": item.produto.nome,
        "quantidade": item.quantidade,
        "observacao": item.observacao,
        "status": item.status.value,
        # 🔄 CORREÇÃO: Substituído o utcnow() depreciado no Python 3.11+ pelo timezone consciente
        "minutos_espera": int((datetime.now(timezone.utc) - item.pedido.criado_em.replace(tzinfo=timezone.utc)).total_seconds() / 60) if item.pedido.criado_em else 0
    } for item in itens]

@router.post("/item/{item_id}/avancar", status_code=status.HTTP_200_OK)
async def avancar_estagio_item(item_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Muda o status do item no KDS via teclado USB. Alerta o garçom via WebSocket se ficar PRONTO.
    """
    repo = ProducaoRepository(db)
    
    # 🔄 CORREÇÃO: Sanado o erro de sintaxe e migrado para select() assíncrono do SQLAlchemy 2.0
    query = select(ItemPedido).filter(ItemPedido.id == item_id)
    result = await db.execute(query)
    item_atual = result.scalars().first()
    
    if not item_atual:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
        
    proximo_status = StatusItem.EM_PREPARO
    if item_atual.status == StatusItem.EM_PREPARO:
        proximo_status = StatusItem.PRONTO
        # ⚡ BAIXA AUTOMÁTICA DE ESTOQUE: O prato ficou pronto, desconta os ingredientes brutos
        estoque_repo = EstoqueRepository(db)
        # 🔄 CORREÇÃO: Adicionado await na baixa automática assíncrona do estoque
        await estoque_repo.descontar_estoque_por_produto(
            produto_id=item_atual.produto_id,
            quantidade_pedido=item_atual.quantidade
        )
    elif item_atual.status == StatusItem.PRONTO:
        proximo_status = StatusItem.ENTREGUE

    # 🔄 CORREÇÃO: Adicionado await na atualização de status do repositório
    item_atualizado = await repo.atualizar_status_item(item_id, proximo_status)
    
    if proximo_status == StatusItem.PRONTO and item_atualizado.pedido.mesa:
        await notifier.broadcast_to_group("garcons", {
            "evento": "item_pronto",
            "item_id": item_id,
            "mesa": item_atualizado.pedido.mesa.numero_identificador,
            "produto": item_atualizado.produto.nome,
            "alerta": f"🚨 Retirar: {item_atualizado.produto.nome} da Mesa {item_atualizado.pedido.mesa.numero_identificador} está PRONTO!"
        })
        
    return {"message": f"Status updated para {proximo_status.value}."}
