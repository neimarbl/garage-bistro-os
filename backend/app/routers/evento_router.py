# backend/app/routers/evento_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Tipo assíncrono correto
from datetime import datetime
from app.core.database import get_async_db         # 🔄 CORREÇÃO: Importação corrigida
from app.repositories.evento_repository import EventoRepository
from app.models.database_models import TipoCusteio

router = APIRouter(prefix="/eventos", tags=["Eventos Corporativos & Regras B2B"])

class NovoEventoRequest(BaseModel):
    nome: str
    data_evento: str # YYYY-MM-DD
    tipo_custeio: TipoCusteio
    limite_orcamento_empresa: float = 0.0

class VinculoComandaRequest(BaseModel):
    comanda_id: int

# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.post("/abrir-festa", status_code=status.HTTP_201_CREATED)
async def abrir_festa_parametrizada(payload: NovoEventoRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Cadastra e ativa o evento da noite, aplicando as regras de rateio e custeio comercial.
    """
    try:
        data_dt = datetime.strptime(payload.data_evento, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM-DD.")

    repo = EventoRepository(db)
    # 🔄 CORREÇÃO: Adicionado await na chamada assíncrona do repositório
    evento = await repo.criar_evento(
        nome=payload.nome,
        data_evento=data_dt,
        tipo_custeio=payload.tipo_custeio,
        teto_gastos=payload.limite_orcamento_empresa
    )
    return {"message": f"Evento '{evento.nome}' ativo com política de custeio {evento.tipo_custeio.value}!"}

# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.post("/vincular-comanda", status_code=status.HTTP_200_OK)
async def vincular_comanda_pvc(payload: VinculoComandaRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Vincula uma comanda física ativa ao evento corporativo do dia.
    """
    repo = EventoRepository(db)
    # 🔄 CORREÇÃO: Adicionado await para busca assíncrona
    evento_ativo = await repo.obter_evento_ativo()
    if not evento_ativo:
        raise HTTPException(status_code=404, detail="Não há nenhum evento corporativo ativo hoje.")
        
    # 🔄 CORREÇÃO: Adicionado await para a persistência assíncrona do vínculo
    await repo.vincular_comanda_ao_evento(evento_id=evento_ativo.id, comanda_id=payload.comanda_id)
    return {"message": f"Comanda {payload.comanda_id} integrada ao orçamento de '{evento_ativo.nome}'."}
