# backend/app/repositories/chamado_repository.py
from sqlalchemy.orm import Session
from app.models.database_models import ChamadoAtendimento, StatusChamado
from typing import List

class ChamadoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar_chamado(self, mesa_id: int, tipo: str) -> ChamadoAtendimento:
        novo_chamado = ChamadoAtendimento(
            mesa_id=mesa_id,
            tipo=tipo,  # "duvida" ou "maquininha"
            status=StatusChamado.ABERTO
        )
        self.db.add(novo_chamado)
        self.db.commit()
        self.db.refresh(novo_chamado)
        return novo_chamado

    def atender_chamado(self, chamado_id: int) -> bool:
        chamado = self.db.query(ChamadoAtendimento).filter(ChamadoAtendimento.id == chamado_id).first()
        if chamado:
            chamado.status = StatusChamado.ATENDIDO
            self.db.commit()
            return True
        return False

    def listar_chamados_ativos(self) -> List[ChamadoAtendimento]:
        return self.db.query(ChamadoAtendimento).filter(
            ChamadoAtendimento.status == StatusChamado.ABERTO
        ).order_by(ChamadoAtendimento.criado_em.asc()).all()
