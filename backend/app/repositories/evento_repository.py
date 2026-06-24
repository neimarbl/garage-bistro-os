# backend/app/repositories/evento_repository.py
from sqlalchemy.orm import Session
from app.models.database_models import Evento, ComandaEventos, TipoCusteio
from datetime import datetime
from typing import Optional, List

class EventoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar_evento(self, nome: str, data_evento: datetime, tipo_custeio: TipoCusteio, teto_gastos: float = 0.0) -> Evento:
        # Desativa qualquer outro evento que tenha ficado aberto por engano
        self.db.query(Evento).filter(Evento.ativo == True).update({"ativo": False})
        
        novo_evento = Evento(
            nome=nome,
            data_evento=data_evento,
            tipo_custeio=tipo_custeio,
            limite_orcamento_empresa=teto_gastos,
            ativo=True
        )
        self.db.add(novo_evento)
        self.db.commit()
        self.db.refresh(novo_evento)
        return novo_evento

    def obter_evento_ativo(self) -> Optional[Evento]:
        return self.db.query(Evento).filter(Evento.ativo == True).first()

    def vincular_comanda_ao_evento(self, evento_id: int, comanda_id: int) -> ComandaEventos:
        vinculo = ComandaEventos(evento_id=evento_id, comanda_id=comanda_id)
        self.db.add(vinculo)
        self.db.commit()
        self.db.refresh(vinculo)
        return vinculo
