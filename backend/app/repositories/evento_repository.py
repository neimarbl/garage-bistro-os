# backend/app/repositories/evento_repository.py
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Utiliza sessão assíncrona
from sqlalchemy.future import select                # 🔄 CORREÇÃO: Nova API de consultas do SQLAlchemy 2.0
from sqlalchemy import update                       # 🔄 CORREÇÃO: Operação assíncrona de update em lote
from app.models.database_models import Evento, ComandaEventos, TipoCusteio
from datetime import datetime
from typing import Optional, List

class EventoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def criar_evento(self, nome: str, data_evento: datetime, tipo_custeio: TipoCusteio, teto_gastos: float = 0.0) -> Evento:
        """
        Cadastra um novo evento e desativa de forma assíncrona qualquer outro que esteja aberto.
        """
        # 🔄 CORREÇÃO: Update em lote reescrito para o padrão assíncrono estrito do SQLAlchemy 2.0
        stmt_desativar = update(Evento).filter(Evento.ativo == True).values(ativo=False)
        await self.db.execute(stmt_desativar)
        
        novo_evento = Evento(
            nome=nome,
            data_evento=data_evento,
            tipo_custeio=tipo_custeio,
            limite_orcamento_empresa=teto_gastos,
            ativo=True
        )
        self.db.add(novo_evento)
        await self.db.commit()   # 🔄 CORREÇÃO: Commit assíncrono
        await self.db.refresh(novo_evento)  # 🔄 CORREÇÃO: Refresh assíncrono
        return novo_evento

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def obter_evento_ativo(self) -> Optional[Evento]:
        """
        Busca o evento corporativo ativo utilizando select assíncrono.
        """
        # 🔄 CORREÇÃO: Consulta reescrita usando select() assíncrono
        query = select(Evento).filter(Evento.ativo == True)
        result = await self.db.execute(query)
        return result.scalars().first()

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def vincular_comanda_ao_evento(self, evento_id: int, comanda_id: int) -> ComandaEventos:
        """
        Vincula uma comanda física ativa ao fluxo B2B do evento de forma assíncrona.
        """
        vinculo = ComandaEventos(evento_id=evento_id, comanda_id=comanda_id)
        self.db.add(vinculo)
        await self.db.commit()   # 🔄 CORREÇÃO: Commit assíncrono
        await self.db.refresh(vinculo)  # 🔄 CORREÇÃO: Refresh assíncrono
        return vinculo
