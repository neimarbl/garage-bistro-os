# backend/app/repositories/pedido_repository.py
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Utiliza sessão assíncrona
from sqlalchemy.future import select                # 🔄 CORREÇÃO: Nova API de consultas do SQLAlchemy 2.0
from sqlalchemy.orm import joinedload              # 🔄 CORREÇÃO: Previne MissingGreenlet nas rotas assíncronas do KDS
from app.models.database_models import Pedido, ItemPedido, Mesa, StatusMesa
from typing import List, Dict, Any, Optional

class PedidoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def criar_pedido(self, mesa_id: int, comanda_id: int, itens_data: List[Dict[str, Any]], origem: str = "garcon") -> Pedido:
        """
        Registra um novo pedido no sistema, vincula seus itens e altera de forma assíncrona o status da mesa para OCUPADA.
        """
        # Inclui o campo origem na criação
        novo_pedido = Pedido(mesa_id=mesa_id, comanda_id=comanda_id, origem=origem)
        self.db.add(novo_pedido)
        await self.db.flush() # 🔄 CORREÇÃO: Flush assíncrono para obter o ID do pedido gerado imediatamente

        for item in itens_data:
            novo_item = ItemPedido(
                pedido_id=novo_pedido.id,
                produto_id=item["produto_id"],
                quantidade=item["quantidade"],
                observacao=item.get("observacao")
            )
            self.db.add(novo_item)
        
        # 🔄 CORREÇÃO: Busca da mesa adaptada para select assíncrono do SQLAlchemy 2.0
        query_mesa = select(Mesa).filter(Mesa.id == mesa_id)
        result_mesa = await self.db.execute(query_mesa)
        mesa = result_mesa.scalars().first()
        
        if mesa:
            mesa.status = StatusMesa.OCUPADA

        await self.db.commit()      # 🔄 CORREÇÃO: Commit assíncrono único ao fim de toda a transação
        await self.db.refresh(novo_pedido) # 🔄 CORREÇÃO: Refresh assíncrono
        return novo_pedido

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def listar_itens_por_status(self, categorias_bebida: bool = False) -> List[ItemPedido]:
        """
        Garante a separação de telas do KDS de forma assíncrona.
        Se categorias_bebida for True, busca apenas bebidas para a tela do Barman.
        Se False, busca comidas para os auxiliares de cozinha.
        """
        from app.models.database_models import Produto, CategoriaProduto, StatusItem
        
        # 🔄 CORREÇÃO: Query reescrita de forma assíncrona aplicando joinedload no Produto
        stmt = (
            select(ItemPedido)
            .join(Produto)
            .filter(ItemPedido.status.in_([StatusItem.PENDENTE, StatusItem.EM_PREPARO]))
            .options(joinedload(ItemPedido.produto))
        )
        
        if categorias_bebida:
            stmt = stmt.filter(Produto.categoria == CategoriaProduto.BEBIDA)
        else:
            stmt = stmt.filter(Produto.categoria != CategoriaProduto.BEBIDA)
            
        stmt = stmt.order_by(ItemPedido.id.asc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
