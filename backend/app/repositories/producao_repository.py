from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.database_models import ItemPedido, StatusItem, Produto, CategoriaProduto, Pedido

class ProducaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar_fila_producao(self, apenas_bebidas: bool = False) -> List[ItemPedido]:
        query = self.db.query(ItemPedido).join(Produto).join(Pedido).filter(
            ItemPedido.status.in_([StatusItem.PENDENTE, StatusItem.EM_PREPARO])
        )
        if apenas_bebidas:
            query = query.filter(Produto.categoria == CategoriaProduto.BEBIDA)
        else:
            query = query.filter(Produto.categoria != CategoriaProduto.BEBIDA)
        return query.order_by(ItemPedido.id.asc()).all()

    def atualizar_status_item(self, item_id: int, novo_status: StatusItem) -> Optional[ItemPedido]:
        item = self.db.query(ItemPedido).filter(ItemPedido.id == item_id).first()
        if item:
            item.status = novo_status
            self.db.commit()
            self.db.refresh(item)
            return item
        return None
