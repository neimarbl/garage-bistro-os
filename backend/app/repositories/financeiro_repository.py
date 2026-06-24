from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

class FinanceiroRepository:
    def __init__(self, db: Session):
        self.db = db

    def calcular_extrato_comanda(self, comanda_id: int, valor_cover: float = 0.0) -> Dict[str, Any]:
        # 🟢 Lazy Import Local: Evita o travamento cíclico com o arquivo de modelos no boot
        from app.models.database_models import ItemPedido, StatusItem, PagamentoParcial

        itens_consumidos = self.db.query(ItemPedido).filter(
            ItemPedido.pedido.has(comanda_id=comanda_id),
            ItemPedido.status != StatusItem.PENDENTE
        ).all()

        subtotal_consumo = sum(float(item.produto.preco) * item.quantidade for item in itens_consumidos)
        taxa_servico = subtotal_consumo * 0.10
        total_geral = subtotal_consumo + taxa_servico + valor_cover

        total_pago = self.db.query(func.sum(PagamentoParcial.valor)).filter(
            PagamentoParcial.comanda_id == comanda_id
        ).scalar() or 0.0

        saldo_restante = total_geral - float(total_pago)

        return {
            "subtotal_consumo": round(subtotal_consumo, 2),
            "taxa_servico_10": round(taxa_servico, 2),
            "cover_artistico": round(valor_cover, 2),
            "total_geral": round(total_geral, 2),
            "total_pago": round(float(total_pago), 2),
            "saldo_restante": round(max(saldo_restante, 0.0), 2)
        }

    def registrar_pagamento_parcial(self, comanda_id: int, valor: float, metodo: str, transacao_id: str = None) -> Any:
        # 🟢 Lazy Import Local
        from app.models.database_models import PagamentoParcial

        pagamento = PagamentoParcial(
            comanda_id=comanda_id,
            valor=valor,
            metodo=metodo,
            id_transacao_externa=transacao_id
        )
        self.db.add(pagamento)
        self.db.commit()
        self.db.refresh(pagamento)
        return pagamento
