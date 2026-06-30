# backend/app/repositories/estoque_repository.py
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Sessão assíncrona
from sqlalchemy.future import select                # 🔄 CORREÇÃO: Sintaxe SQLAlchemy 2.0
from sqlalchemy import and_
from app.models.database_models import Insumo, FichaTecnica, ItemPedido
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

class EstoqueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def registrar_entrada_atacado(self, insumo_id: int, quantidade: float, data_validade: datetime, congelado: bool = False) -> Optional[Insumo]:
        """
        Dá entrada em mercadorias compradas no distribuidor, atualizando o saldo real.
        """
        query = select(Insumo).filter(Insumo.id == insumo_id)
        result = await self.db.execute(query)
        insumo = result.scalars().first()
        
        if insumo:
            insumo.quantidade_atual = float(insumo.quantidade_atual) + quantidade
            insumo.data_validade = data_validade
            insumo.congelado = congelado
            await self.db.commit()   # 🔄 CORREÇÃO: Commit assíncrono
            await self.db.refresh(insumo)  # 🔄 CORREÇÃO: Refresh assíncrono
        return insumo

    # 🔄 CORREÇÃO: Transformado em método assíncrono para o fluxo do KDS
    async def descontar_estoque_por_produto(self, produto_id: int, quantidade_pedido: int):
        """
        Lógica de Ficha Técnica: Varre a receita do produto e abate cada grama/unidade dos insumos.
        """
        query_ingredientes = select(FichaTecnica).filter(FichaTecnica.produto_id == produto_id)
        result_ingredientes = await self.db.execute(query_ingredientes)
        ingredientes = result_ingredientes.scalars().all()
        
        for ing in ingredientes:
            query_insumo = select(Insumo).filter(Insumo.id == ing.insumo_id)
            result_insumo = await self.db.execute(query_insumo)
            insumo = result_insumo.scalars().first()
            
            if insumo:
                total_desconto = float(ing.quantidade_gasta) * quantidade_pedido
                insumo.quantidade_atual = max(float(insumo.quantidade_atual) - total_desconto, 0.0)
                
        await self.db.commit()  # 🔄 CORREÇÃO: Um único commit assíncrono ao final da transação

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def listar_alertas_criticos(self) -> List[Dict[str, Any]]:
        """
        Retorna insumos abaixo do estoque mínimo ou congelados com validade menor que 5 dias.
        """
        alertas = []
        # 🔄 CORREÇÃO: Substituído utcnow() depreciado por timezone nativo do Python 3.11+
        hoje = datetime.now(timezone.utc).replace(tzinfo=None)
        limite_validade = hoje + timedelta(days=5)

        # 1. Alertas de Estoque Baixo
        query_baixo = select(Insumo).filter(Insumo.quantidade_atual <= Insumo.quantidade_minima)
        result_baixo = await self.db.execute(query_baixo)
        estoque_baixo = result_baixo.scalars().all()
        
        for item in estoque_baixo:
            alertas.append({
                "insumo": item.nome,
                "motivo": "Estoque crítico abaixo do limite mínimo definido para eventos.",
                "saldo_atual": float(item.quantidade_atual)
            })

        # 2. Alertas de Validade Próxima (Foco em Congelados)
        query_vencendo = select(Insumo).filter(
            and_(Insumo.data_validade <= limite_validade, Insumo.quantidade_atual > 0)
        )
        result_vencendo = await self.db.execute(query_vencendo)
        itens_vencendo = result_vencendo.scalars().all()
        
        for item in itens_vencendo:
            alertas.append({
                "insumo": item.nome,
                "motivo": f"⚠️ ATENÇÃO: Item {'CONGELADO' if item.congelado else 'FRESCO'} perto do vencimento ({item.data_validade.strftime('%d/%m')}).",
                "saldo_atual": float(item.quantidade_atual)
            })

        return alertas

    # 🔄 CORREÇÃO: Convertido para método estático assíncrono (@classmethod) para sanar duplicação de classe
    @classmethod
    async def calcular_alertas_criticos(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Varre os lotes físicos do PostgreSQL gerando matrizes preventivas de perdas e validades.
        """
        alertas = []
        hoje = datetime.now(timezone.utc).replace(tzinfo=None)
        limite_validade = hoje + timedelta(days=5)

        query = select(Insumo)
        result = await db.execute(query)
        insumos = result.scalars().all()

        for insumo in insumos:
            if float(insumo.quantidade_atual) <= float(insumo.quantidade_minima):
                alertas.append({
                    "tipo": "CRÍTICO",
                    "insumo_nome": insumo.nome,
                    "quantidade_atual": float(insumo.quantidade_atual),
                    "mensagem": f"⚠️ Ruptura iminente! Saldo atual está abaixo do mínimo operacional."
                })

            if insumo.data_validade and hoje <= insumo.data_validade <= limite_validade:
                alertas.append({
                    "tipo": "VALIDADE",
                    "insumo_nome": insumo.nome,
                    "data_validade": insumo.data_validade.isoformat(),
                    "mensagem": f"🚨 Risco de perda financeira! Insumo está a menos de 5 dias do vencimento."
                })

        return alertas
