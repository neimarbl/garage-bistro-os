from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.database_models import Mesa, Comanda, StatusMesa, StatusComanda

class AtendimentoRepository:
    # 1. Troca Session síncrona por AsyncSession assíncrona
    def __init__(self, db: AsyncSession):
        self.db = db

    # 2. O Método que estava faltando no seu roteador
    async def listar_todas_mesas(self) -> List[Mesa]:
        query = select(Mesa).order_by(Mesa.numero_identificador)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    # 3. Refatoração assíncrona dos demais métodos (Padrão SQLAlchemy 2.0)
    async def obter_mesa_por_numero(self, numero: int) -> Optional[Mesa]:
        query = select(Mesa).filter(Mesa.numero_identificador == numero)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def criar_mesa(self, numero: int) -> Mesa:
        mesa = Mesa(numero_identificador=numero, status=StatusMesa.LIVRE)
        self.db.add(mesa)
        await self.db.commit()
        await self.db.refresh(mesa)
        return mesa

    async def agrupar_mesas(self, numero_pai: int, numeros_filhas: List[int]) -> Optional[Mesa]:
        mesa_pai = await self.obter_mesa_por_numero(numero_pai)
        if not mesa_pai:
            return None
        
        mesa_pai.status = StatusMesa.OCUPADA
        
        for num in numeros_filhas:
            mesa_filha = await self.obter_mesa_por_numero(num)
            if mesa_filha:
                mesa_filha.mesa_pai_id = mesa_pai.id
                mesa_filha.status = StatusMesa.OCUPADA
        
        await self.db.commit()
        await self.db.refresh(mesa_pai)
        return mesa_pai

    async def activar_comanda_pvc(self, numero_pvc: int, token_sessao: str) -> Comanda:
        query = select(Comanda).filter(
            Comanda.numero_pvc == numero_pvc, 
            Comanda.status == StatusComanda.ATIVA
        )
        result = await self.db.execute(query)
        comanda_existente = result.scalars().first()
        
        if comanda_existente:
            return comanda_existente
            
        nova_comanda = Comanda(
            numero_pvc=numero_pvc, 
            status=StatusComanda.ATIVA,
            token_sessao=token_sessao
        )
        self.db.add(nova_comanda)
        await self.db.commit()
        await self.db.refresh(nova_comanda)
        return nova_comanda
