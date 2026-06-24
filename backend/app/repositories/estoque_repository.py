# backend/app/repositories/estoque_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.database_models import Insumo, FichaTecnica, ItemPedido
from datetime import datetime, timedelta
from typing import List, Dict, Any

class EstoqueRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar_entrada_atacado(self, insumo_id: int, quantidade: float, data_validade: datetime, congelado: bool = False) -> Insumo:
        """
        Dá entrada em mercadorias compradas no distribuidor, atualizando o saldo real.
        """
        insumo = self.db.query(Insumo).filter(Insumo.id == insumo_id).first()
        if insumo:
            insumo.quantidade_atual = float(insumo.quantidade_atual) + quantidade
            insumo.data_validade = data_validade
            insumo.congelado = congelado
            self.db.commit()
            self.db.refresh(insumo)
        return insumo

    def descontar_estoque_por_produto(self, produto_id: int, quantidade_pedido: int):
        """
        Lógica de Ficha Técnica: Varre a receita do produto e abate cada grama/unidade dos insumos.
        """
        ingredientes = self.db.query(FichaTecnica).filter(FichaTecnica.produto_id == produto_id).all()
        for ing in ingredientes:
            insumo = self.db.query(Insumo).filter(Insumo.id == ing.insumo_id).first()
            if insumo:
                total_desconto = float(ing.quantidade_gasta) * quantidade_pedido
                insumo.quantidade_atual = max(float(insumo.quantidade_atual) - total_desconto, 0.0)
        self.db.commit()

    def listar_alertas_criticos(self) -> List[Dict[str, Any]]:
        """
        Retorna insumos abaixo do estoque mínimo ou congelados com validade menor que 5 dias.
        """
        alertas = []
        hoje = datetime.utcnow()
        limite_validade = hoje + timedelta(days=5)

        # 1. Alertas de Estoque Baixo
        estoque_baixo = self.db.query(Insumo).filter(Insumo.quantidade_atual <= Insumo.quantidade_minima).all()
        for item in estoque_baixo:
            alertas.append({
                "insumo": item.nome,
                "motivo": "Estoque crítico abaixo do limite mínimo definido para eventos.",
                "saldo_atual": float(item.quantidade_atual)
            })

        # 2. Alertas de Validade Próxima (Foco em Congelados)
        itens_vencendo = self.db.query(Insumo).filter(
            and_(Insumo.data_validade <= limite_validade, Insumo.quantidade_atual > 0)
        ).all()
        for item in itens_vencendo:
            alertas.append({
                "insumo": item.nome,
                "motivo": f"⚠️ ATENÇÃO: Item {'CONGELADO' if item.congelado else 'FRESCO'} perto do vencimento ({item.data_validade.strftime('%d/%m')}).",
                "saldo_atual": float(item.quantidade_atual)
            })

        return alertas

class EstoqueRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def calcular_alertas_criticos(db: Session) -> List[Dict[str, Any]]:
        from app.models.database_models import Insumo
        
        alertas = []
        hoje = datetime.utcnow()
        limite_validade = hoje + timedelta(days=5) # Janela crítica de 5 dias solicitada

        # 1. Busca todos os insumos cadastrados no almoxarifado
        insumos = db.query(Insumo).all()

        for insumo in insumos:
            # Alerta de Nível Crítico (Abaixo da quantidade mínima configurada)
            if float(insumo.quantidade_atual) <= float(insumo.quantidade_minima):
                alertas.append({
                    "tipo": "CRÍTICO",
                    "insumo_nome": insumo.nome,
                    "quantidade_atual": float(insumo.quantidade_atual),
                    "mensagem": f"⚠️ Ruptura iminente! Saldo atual está abaixo do mínimo operacional."
                })

            # Alerta de Validade Próxima (Insumos congelados ou resfriados vencendo em < 5 dias)
            if insumo.data_validade and hoje <= insumo.data_validade <= limite_validade:
                alertas.append({
                    "tipo": "VALIDADE",
                    "insumo_nome": insumo.nome,
                    "data_validade": insumo.data_validade.isoformat(),
                    "mensagem": f"🚨 Risco de perda financeira! Insumo está a menos de 5 dias do vencimento."
                })

        return alertas