from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.database_models import Mesa, Comanda, StatusMesa, StatusComanda

class AtendimentoRepository:
    def __init__(self, db: Session):
        self.db = db

    def obter_mesa_por_numero(self, numero: int) -> Optional[Mesa]:
        return self.db.query(Mesa).filter(Mesa.numero_identificador == numero).first()

    def criar_mesa(self, numero: int) -> Mesa:
        mesa = Mesa(numero_identificador=numero, status=StatusMesa.LIVRE)
        self.db.add(mesa)
        self.db.commit()
        self.db.refresh(mesa)
        return mesa

    def agrupar_mesas(self, numero_pai: int, numeros_filhas: List[int]) -> Optional[Mesa]:
        mesa_pai = self.obter_mesa_por_numero(numero_pai)
        if not mesa_pai:
            return None
        
        mesa_pai.status = StatusMesa.OCUPADA
        
        for num in numeros_filhas:
            mesa_filha = self.obter_mesa_por_numero(num)
            if mesa_filha:
                mesa_filha.mesa_pai_id = mesa_pai.id
                mesa_filha.status = StatusMesa.OCUPADA
        
        self.db.commit()
        self.db.refresh(mesa_pai)
        return mesa_pai

    def activar_comanda_pvc(self, numero_pvc: int, token_sessao: str) -> Comanda:
        """
        Busca ou cria uma comanda ativa injetando o token de segurança obrigatório.
        """
        comanda_existente = self.db.query(Comanda).filter(
            Comanda.numero_pvc == numero_pvc, 
            Comanda.status == StatusComanda.ATIVA
        ).first()
        
        if comanda_existente:
            return comanda_existente
            
        nova_comanda = Comanda(
            numero_pvc=numero_pvc, 
            status=StatusComanda.ATIVA,
            token_sessao=token_sessao
        )
        self.db.add(nova_comanda)
        self.db.commit()
        self.db.refresh(nova_comanda)
        return nova_comanda
