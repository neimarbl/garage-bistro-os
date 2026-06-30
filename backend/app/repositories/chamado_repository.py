# backend/app/repositories/chamado_repository.py
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Utiliza sessão assíncrona
from sqlalchemy.future import select                # 🔄 CORREÇÃO: Sintaxe de consulta SQLAlchemy 2.0
from app.models.database_models import ChamadoAtendimento, StatusChamado
from typing import List, Optional

class ChamadoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def criar_chamado(self, mesa_id: int, tipo: str) -> ChamadoAtendimento:
        novo_chamado = ChamadoAtendimento(
            mesa_id=mesa_id,
            tipo=tipo,  # "duvida" ou "maquininha"
            status=StatusChamado.ABERTO
        )
        self.db.add(novo_chamado)
        await self.db.commit()   # 🔄 CORREÇÃO: Commit assíncrono
        await self.db.refresh(novo_chamado)  # 🔄 CORREÇÃO: Refresh assíncrono
        return novo_chamado

    # 🔄 CORREÇÃO: Retorna o objeto atualizado ou None para manter consistência com o router
    async def atender_chamado(self, chamado_id: int) -> Optional[ChamadoAtendimento]:
        # 🔄 CORREÇÃO: Consulta reescrita usando select() assíncrono
        query = select(ChamadoAtendimento).filter(ChamadoAtendimento.id == chamado_id)
        result = await self.db.execute(query)
        chamado = result.scalars().first()
        
        if chamado:
            chamado.status = StatusChamado.ATENDIDO
            await self.db.commit()  # 🔄 CORREÇÃO: Commit assíncrono
            return chamado
        return None

    # 🔄 CORREÇÃO: Transformado em método assíncrono
    async def listar_chamados_ativos(self) -> List[ChamadoAtendimento]:
        # 🔄 CORREÇÃO: Consulta reescrita usando select() assíncrono
        query = (
            select(ChamadoAtendimento)
            .filter(ChamadoAtendimento.status == StatusChamado.ABERTO)
            .order_by(ChamadoAtendimento.criado_em.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
