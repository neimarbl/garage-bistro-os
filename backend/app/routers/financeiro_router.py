# backend/app/routers/financeiro_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.database_models import CategoriaProduto, ItemPedido, StatusItem, Produto, TipoCusteio
from app.core.websocket_manager import notifier

router = APIRouter(prefix="/financeiro", tags=["Financeiro & Fechamento de Contas"])

class PagamentoRequest(BaseModel):
    comanda_id: int
    valor: float
    metodo: str # "pix", "credito", "debito", "dinheiro"
    transacao_id: str = None

@router.get("/comanda/{comanda_id}/extrato")
def obter_extrato(comanda_id: int, cover: float = 0.0, db: Session = Depends(get_db)):
    """
    Exibe a prévia da conta aplicando regras dinâmicas se houver um evento corporativo ativo.
    """
    # ⚡ LAZY IMPORTS: Importações tardias locais para estripar a importação circular do portfólio
    from app.repositories.financeiro_repository import FinanceiroRepository
    from app.repositories.evento_repository import EventoRepository
    
    fin_repo = FinanceiroRepository(db)
    eve_repo = EventoRepository(db)
    
    extrato_base = fin_repo.calcular_extrato_comanda(comanda_id=comanda_id, valor_cover=cover)
    evento_ativo = eve_repo.obter_evento_ativo()
    
    if not evento_ativo:
        return {**extrato_base, "responsabilidade_empresa": 0.0, "responsabilidade_cliente": extrato_base["saldo_restante"]}
        
    if evento_ativo.tipo_custeio == TipoCusteio.TOTAL_EMPRESA:
        return {**extrato_base, "responsabilidade_empresa": extrato_base["saldo_restante"], "responsabilidade_cliente": 0.0}
        
    elif evento_ativo.tipo_custeio == TipoCusteio.HIBRIDO_FIXO:
        itens_comanda = db.query(ItemPedido).join(Produto).filter(
            ItemPedido.pedido.has(comanda_id=comanda_id), ItemPedido.status != StatusItem.PENDENTE
        ).all()
        
        valor_comidas = sum(float(i.produto.preco) * i.quantidade for i in itens_comanda if i.produto.categoria != CategoriaProduto.BEBIDA)
        valor_bebidas = sum(float(i.produto.preco) * i.quantidade for i in itens_comanda if i.produto.categoria == CategoriaProduto.BEBIDA)
        
        custo_empresa = valor_comidas * 1.10
        custo_cliente = (valor_bebidas * 1.10) + cover
        
        return {
            **extrato_base,
            "regra_evento_aplicada": f"Híbrido ({evento_ativo.nome})",
            "responsabilidade_empresa": round(custo_empresa, 2),
            "responsabilidade_cliente": round(max(custo_cliente - extrato_base["total_pago"], 0.0), 2)
        }
        
    return {**extrato_base, "responsabilidade_empresa": 0.0, "responsabilidade_cliente": extrato_base["saldo_restante"]}

@router.post("/pagar-fracionado", status_code=status.HTTP_201_CREATED)
async def pagar_fracionado(payload: PagamentoRequest, db: Session = Depends(get_db)):
    """
    Registra um pagamento fracionado parcial.
    """
    from app.repositories.financeiro_repository import FinanceiroRepository
    
    repo = FinanceiroRepository(db)
    pagamento = repo.registrar_pagamento_parcial(
        comanda_id=payload.comanda_id,
        valor=payload.valor,
        metodo=payload.metodo,
        transacao_id=payload.transacao_id
    )

    if payload.metodo == "pix":
        await notifier.broadcast_to_group("caixa", {
            "evento": "pix_recebido",
            "comanda_id": payload.comanda_id,
            "alerta": f"✅ PIX de R$ {payload.valor} recebido da Comanda {payload.comanda_id}! Liberar saída."
        })
    elif payload.metodo in ["credito", "debito"]:
        await notifier.broadcast_to_group("garcons", {
            "evento": "chamar_maquininha",
            "comanda_id": payload.comanda_id,
            "alerta": f"💳 Levar maquinha para receber R$ {payload.valor} na Comanda {payload.comanda_id}."
        })

    return {"message": "Pagamento registrado!", "saldo": repo.calcular_extrato_comanda(payload.comanda_id)}

@router.get("/resumo-diario", status_code=status.HTTP_200_OK)
def obter_resumo_caixa(db: Session = Depends(get_db)):
    """
    Retorna o faturamento bruto consolidado do caixa segregado por método de pagamento.
    """
    from app.repositories.financeiro_repository import FinanceiroRepository
    return FinanceiroRepository.obter_resumo_diario(db)