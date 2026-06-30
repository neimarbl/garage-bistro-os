# backend/app/repositories/producao_repository.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Utiliza sessão assíncrona
from sqlalchemy.future import select                # 🔄 CORREÇÃO: Nova API de consultas do SQLAlchemy 2.0
from sqlalchemy.orm import joinedload              # 🔄 CORREÇÃO: Evita MissingGreenlet carregando árvore de relações
from app.models.database_models import ItemPedido, StatusItem, Produto, CategoriaProduto, Pedido

class ProducaoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def listar_fila_producao(self, apenas_bebidas: bool = False) -> List[ItemPedido]:
        """
        Retorna a fila de produção do KDS de forma assíncrona, pré-carregando o Produto, Pedido e Mesa.
        """
        # 🔄 CORREÇÃO: Query reescrita para select() assíncrono com joinedload profundo de múltiplos níveis
        stmt = (
            select(ItemPedido)
            .join(Produto)
            .join(Pedido)
            .filter(ItemPedido.status.in_([StatusItem.PENDENTE, StatusItem.EM_PREPARO]))
            .options(
                joinedload(ItemPedido.produto),
                joinedload(ItemPedido.pedido).joinedload(Pedido.mesa),
                joinedload(ItemPedido.pedido).joinedload(Pedido.comanda)
            )
        )
        
        if apenas_bebidas:
            stmt = stmt.filter(Produto.categoria == CategoriaProduto.BEBIDA)
        else:
            stmt = stmt.filter(Produto.categoria != CategoriaProduto.BEBIDA)
            
        stmt = stmt.order_by(ItemPedido.id.asc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def atualizar_status_item(self, item_id: int, novo_status: StatusItem) -> Optional[ItemPedido]:
        """
        Atualiza o estágio do item no KDS de forma assíncrona.
        """
        # 🔄 CORREÇÃO: Busca do item adaptada para select assíncrono carregando dependências para o WebSocket do router
        stmt = (
            select(ItemPedido)
            .filter(ItemPedido.id == item_id)
            .options(
                joinedload(ItemPedido.produto),
                joinedload(ItemPedido.pedido).joinedload(Pedido.mesa)
            )
        )
        result = await self.db.execute(stmt)
        item = result.scalars().first()
        
        if item:
            item.status = novo_status
            await self.db.commit()      # 🔄 CORREÇÃO: Commit assíncrono
            await self.db.refresh(item) # 🔄 CORREÇÃO: Refresh assíncrono
            return item
        return None
