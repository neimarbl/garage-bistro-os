# backend/app/repositories/pedido_repository.py
from sqlalchemy.orm import Session
from app.models.database_models import Pedido, ItemPedido, Mesa, StatusMesa
from typing import List, Dict, Any

class PedidoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar_pedido(self, mesa_id: int, comanda_id: int, itens_data: List[Dict[str, Any]]) -> Pedido:
        # 1. Cria a instância do pedido principal
        novo_pedido = Pedido(mesa_id=mesa_id, comanda_id=comanda_id)
        self.db.add(novo_pedido)
        self.db.flush() # Executa o comando no banco para gerar o ID do pedido sem fechar a transação

        # 2. Varre a lista de itens enviados pelo celular do garçom
        for item in itens_data:
            novo_item = ItemPedido(
                pedido_id=novo_pedido.id,
                produto_id=item["produto_id"],
                quantidade=item["quantidade"],
                observacao=item.get("observacao")
            )
            self.db.add(novo_item)
        
        # 3. Atualiza o status da mesa para ocupada automaticamente
        mesa = self.db.query(Mesa).filter(Mesa.id == mesa_id).first()
        if mesa:
            mesa.status = StatusMesa.OCUPADA

        self.db.commit()
        self.db.refresh(novo_pedido)
        return novo_pedido

    def listar_itens_por_status(self, categorias_bebida: bool = False) -> List[ItemPedido]:
        """
        Garante a separação de telas do KDS.
        Se categorias_bebida for True, busca apenas bebidas para a tela do Barman.
        Se False, busca comidas para os auxiliares de cozinha.
        """
        from app.models.database_models import Produto, CategoriaProduto, StatusItem
        
        query = self.db.query(ItemPedido).join(Produto).filter(
            ItemPedido.status.in_([StatusItem.PENDENTE, StatusItem.EM_PREPARO])
        )
        
        if categorias_bebida:
            query = query.filter(Produto.categoria == CategoriaProduto.BEBIDA)
        else:
            query = query.filter(Produto.categoria != CategoriaProduto.BEBIDA)
            
        return query.order_by(ItemPedido.id.asc()).all()
