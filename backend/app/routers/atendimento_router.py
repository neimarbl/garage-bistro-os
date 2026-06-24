# backend/app/routers/atendimento_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.repositories.atendimento_repository import AtendimentoRepository

# 🟢 Importando ambas as funções do seu seguranca.py na mesma linha para manter o padrão sênior
from app.core.seguranca import gerar_token_comanda, validar_token_comanda
from app.core.database import get_db 

router = APIRouter(prefix="/atendimento", tags=["Atendimento / Salão"])

class AgrupamentoMesasRequest(BaseModel):
    numero_mesa_principal: int
    numeros_mesas_adicionais: List[int]

class AtivarComandaRequest(BaseModel):
    numero_pvc: int
    mesa_id_inicial: int # 🆕 Adicionado para poder injetar a amarração geográfica no QR Code

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
def activar_comanda(payload: AtivarComandaRequest, db: Session = Depends(get_db)):
    """
    Associa e ativa um cartão de PVC físico ao fluxo de consumo, gerando o Token do QR Code.
    """
    repo = AtendimentoRepository(db)
    
    # 1. Gera o token criptográfico primeiro usando o algoritmo HMAC-SHA256
    token_pvc = gerar_token_comanda(payload.numero_pvc)
    
    # 2. Salva no banco de dados injetando o token de segurança obrigatório (Grafia original mantida)
    comanda = repo.activar_comanda_pvc(numero_pvc=payload.numero_pvc, token_sessao=token_pvc)
    
    # 3. 🛡️ CORREÇÃO DA URL: Monta o link omnichannel real casado com o IP da sua LAN e parâmetros do PWA
    link_qr_code = f"http://192.168.111{payload.mesa_id_inicial}&pvc={comanda.numero_pvc}&token={comanda.token_sessao}"
    
    return {
        "comanda_id": comanda.id,
        "numero_pvc": comanda.numero_pvc,
        "status": comanda.status.value,
        "token_seguranca": comanda.token_sessao,
        "url_qr_code_cliente": link_qr_code
    }

# 🆕 INJEÇÃO DO MOTOR DE VALIDAÇÃO DA FRENTE B (CLIENTE):
@router.get("/comanda/{numero_pvc}/validar", status_code=status.HTTP_200_OK)
def validar_acesso_autoatendimento(numero_pvc: int, token: str, db: Session = Depends(get_db)):
    """
    Endpoint de Validação Cruzada Omnichannel para o Web App do Cliente.
    Consome o seguranca.py original para validar o token enviado via smartphone.
    """
    # Executa a sua função nativa imune a Timing Attacks
    is_valido = validar_token_comanda(numero_pvc=numero_pvc, token_recebido=token)
    
    if not is_valido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="⚠️ Alerta de Fraude: A assinatura digital deste cartão PVC é inválida ou expirou!"
        )
        
    return {
        "status": "autorizado",
        "numero_pvc": numero_pvc
    }
