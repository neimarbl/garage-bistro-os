# backend/app/repositories/financeiro_repository.py
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Utiliza sessão assíncrona
from sqlalchemy.future import select                # 🔄 CORREÇÃO: Sintaxe SQLAlchemy 2.0
from sqlalchemy.orm import selectinload            # 🔄 CORREÇÃO: Previne MissingGreenlet no asyncio
from sqlalchemy import func, and_
from datetime import datetime, time, timezone

class FinanceiroRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def calcular_extrato_comanda(self, comanda_id: int, valor_cover: float = 0.0) -> Dict[str, Any]:
        """
        Calcula o extrato total de consumo de uma comanda de forma assíncrona com carregamento prévio de relacionamentos.
        """
        # 🟢 Lazy Import Local mantido para mitigar importação circular
        from app.models.database_models import ItemPedido, StatusItem, PagamentoParcial

        # 🔄 CORREÇÃO: Consulta reescrita usando select() assíncrono com selectinload explícito do produto
        query_itens = (
            select(ItemPedido)
            .filter(ItemPedido.pedido.has(comanda_id=comanda_id), ItemPedido.status != StatusItem.PENDENTE)
            .options(selectinload(ItemPedido.produto))
        )
        result_itens = await self.db.execute(query_itens)
        itens_consumidos = result_itens.scalars().all()

        subtotal_consumo = sum(float(item.produto.preco) * item.quantidade for item in itens_consumidos)
        taxa_servico = subtotal_consumo * 0.10
        total_geral = subtotal_consumo + taxa_servico + valor_cover

        # 🔄 CORREÇÃO: Agregação sum() reescrita para o formato assíncrono
        query_pago = select(func.sum(PagamentoParcial.valor)).filter(PagamentoParcial.comanda_id == comanda_id)
        result_pago = await self.db.execute(query_pago)
        total_pago = result_pago.scalar() or 0.0

        saldo_restante = total_geral - float(total_pago)

        return {
            "subtotal_consumo": round(subtotal_consumo, 2),
            "taxa_servico_10": round(taxa_servico, 2),
            "cover_artistico": round(valor_cover, 2),
            "total_geral": round(total_geral, 2),
            "total_pago": round(float(total_pago), 2),
            "saldo_restante": round(max(saldo_restante, 0.0), 2)
        }

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def registrar_pagamento_parcial(self, comanda_id: int, valor: float, metodo: str, transacao_id: str = None) -> Any:
        """
        Registra o pagamento de forma assíncrona.
        """
        # 🟢 Lazy Import Local
        from app.models.database_models import PagamentoParcial

        pagamento = PagamentoParcial(
            comanda_id=comanda_id,
            valor=valor,
            metodo=metodo,
            id_transacao_externa=transacao_id
        )
        self.db.add(pagamento)
        await self.db.commit()      # 🔄 CORREÇÃO: Commit assíncrono
        await self.db.refresh(pagamento) # 🔄 CORREÇÃO: Refresh assíncrono
        return pagamento
    
    # 🔄 CORREÇÃO: Re-indentado para dentro da classe e convertido para método de classe assíncrono (@classmethod)
    @classmethod
    async def obter_resumo_diario(cls, db: AsyncSession) -> Dict[str, float]:
        """
        Agrega o fechamento diário do caixa dividindo por métodos de forma assíncrona.
        """
        from app.models.database_models import PagamentoParcial, MetodoPagamento
        
        # 🔄 CORREÇÃO: Substituído utcnow() depreciado no Python 3.11+ por timezone explícito
        hoje_local = datetime.now(timezone.utc).date()
        hoje_inicio = datetime.combine(hoje_local, time.min)
        hoje_fim = datetime.combine(hoje_local, time.max)

        # 1. Total Geral do dia
        q_total = select(func.sum(PagamentoParcial.valor)).filter(PagamentoParcial.pago_em.between(hoje_inicio, hoje_fim))
        total_dia = (await db.execute(q_total)).scalar() or 0.0

        # 2. Total PIX
        q_pix = select(func.sum(PagamentoParcial.valor)).filter(
            PagamentoParcial.pago_em.between(hoje_inicio, hoje_fim),
            PagamentoParcial.metodo == MetodoPagamento.PIX
        )
        total_pix = (await db.execute(q_pix)).scalar() or 0.0

        # 3. Total Cartão (Crédito + Débito)
        q_cartao = select(func.sum(PagamentoParcial.valor)).filter(
            PagamentoParcial.pago_em.between(hoje_inicio, hoje_fim),
            PagamentoParcial.metodo.in_([MetodoPagamento.CREDITO, MetodoPagamento.DEBITO])
        )
        total_cartao = (await db.execute(q_cartao)).scalar() or 0.0

        # 4. Total Dinheiro
        q_dinheiro = select(func.sum(PagamentoParcial.valor)).filter(
            PagamentoParcial.pago_em.between(hoje_inicio, hoje_fim),
            PagamentoParcial.metodo == MetodoPagamento.DINHEIRO
        )
        total_dinheiro = (await db.execute(q_dinheiro)).scalar() or 0.0

        return {
            "total_dia": round(float(total_dia), 2),
            "total_pix": round(float(total_pix), 2),
            "total_cartao": round(float(total_cartao), 2),
            "total_dinheiro": round(float(total_dinheiro), 2)
        }
