from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.repositories.atendimento_repository import AtendimentoRepository
from app.core.seguranca import gerar_token_comanda
# 🔐 IMPORTAÇÃO DA CONEXÃO REAL DO BANCO DE DADOS:
from app.core.database import get_db 

router = APIRouter(prefix="/atendimento", tags=["Atendimento / Salão"])

class AgrupamentoMesasRequest(BaseModel):
    numero_mesa_principal: int
    numeros_mesas_adicionais: List[int]

class AtivarComandaRequest(BaseModel):
    numero_pvc: int

@router.post("/mesas/agrupar", status_code=status.HTTP_200_OK)
def agrupar_mesas(payload: AgrupamentoMesasRequest, db: Session = Depends(get_db)):
    """
    Agrupa mesas de forma lógica para atender grupos grandes ou aniversários na garagem.
    """
    repo = AtendimentoRepository(db)
    mesa = repo.agrupar_mesas(payload.numero_mesa_principal, payload.numeros_mesas_adicionais)
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa principal não encontrada.")
    return {"message": "Mesas agrupadas com sucesso no mapa do salão."}

@router.post("/comandas/ativar", status_code=status.HTTP_201_CREATED)
def ativar_comanda(payload: AtivarComandaRequest, db: Session = Depends(get_db)):
    """
    Associa e ativa um cartão de PVC físico ao fluxo de consumo, gerando o Token do QR Code.
    """
    repo = AtendimentoRepository(db)
    
    # 1. Gera o token criptográfico primeiro usando o algoritmo HMAC-SHA256
    token_pvc = gerar_token_comanda(payload.numero_pvc)
    
    # 2. Salva no banco de dados injetando o token de segurança obrigatório
    comanda = repo.activar_comanda_pvc(numero_pvc=payload.numero_pvc, token_sessao=token_pvc)
    
    # 3. Monta o link omnichannel de autoatendimento local para o QR Code do cliente
    link_qr_code = f"http://192.168.111{comanda.numero_pvc}?token={comanda.token_sessao}"
    
    return {
        "comanda_id": comanda.id,
        "numero_pvc": comanda.numero_pvc,
        "status": comanda.status.value,
        "token_seguranca": comanda.token_sessao,
        "url_qr_code_cliente": link_qr_code
    }
