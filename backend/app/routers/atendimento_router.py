# backend/app/routers/atendimento_router.py
import json
from fastapi import APIRouter, Depends, HTTPException, status, Response  # 🔄 CORREÇÃO: Agrupado de forma correta na raiz do FastAPI
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 CORREÇÃO: Utiliza sessão assíncrona
from app.repositories.atendimento_repository import AtendimentoRepository

# Importando ambas as funções do seu seguranca.py na mesma linha para manter o padrão sênior
from app.core.seguranca import gerar_token_comanda, validar_token_comanda
from app.core.database import get_async_db  # 🔄 CORREÇÃO: Nome corrigido para refletir a sessão assíncrona

router = APIRouter(prefix="/atendimento", tags=["Atendimento / Salão"])

class AgrupamentoMesasRequest(BaseModel):
    numero_mesa_principal: int
    numeros_mesas_adicionais: List[int]

class AtivarComandaRequest(BaseModel):
    numero_pvc: int
    mesa_id_inicial: int # Adicionado para poder injetar a amarração geográfica no QR Code

@router.get("/mesas", status_code=status.HTTP_200_OK)
async def listar_mesas_salao(db = Depends(get_async_db)):
    """
    Retorna o status de todas as mesas injetadas via seed de forma direta em texto bruto.
    Estripa definitivamente o erro f405 forçando o bypass da validação do FastAPI.
    """
    repo = AtendimentoRepository(db)
    mesas_db = await repo.listar_todas_mesas()
    
    mesas_serializadas = []
    for mesa in mesas_db:
        status_texto = "LIVRE"
        if hasattr(mesa, "status") and mesa.status is not None:
            status_texto = mesa.status.value if hasattr(mesa.status, "value") else str(mesa.status)
            
        mesas_serializadas.append({
            "id": int(mesa.id) if getattr(mesa, "id", None) is not None else None,
            "numero_identificador": int(mesa.numero_identificador),
            "status": str(status_texto).upper(),
            "mesa_pai_id": int(mesa.mesa_pai_id) if getattr(mesa, "mesa_pai_id", None) is not None else None
        })
        
    # 🔄 CORREÇÃO: Transforma em string JSON e joga direto no corpo da Response, pulando o crivo do FastAPI
    conteudo_json = json.dumps(mesas_serializadas)
    return Response(content=conteudo_json, media_type="application/json")


# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.post("/mesas/agrupar", status_code=status.HTTP_200_OK)
async def agrupar_mesas(payload: AgrupamentoMesasRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Agrupa mesas de forma lógica para atender grupos grandes ou aniversários na garagem.
    """
    repo = AtendimentoRepository(db)
    # 🔄 CORREÇÃO: Adicionado await na chamada do repositório refatorado
    mesa = await repo.agrupar_mesas(payload.numero_mesa_principal, payload.numeros_mesas_adicionais)
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa principal não encontrada.")
    return {"message": "Mesas agrupadas com sucesso no mapa do salão."}

# 🔄 CORREÇÃO: Rota transformada em assíncrona com async def
@router.post("/comandas/ativar", status_code=status.HTTP_201_CREATED)
async def activar_comanda(payload: AtivarComandaRequest, db: AsyncSession = Depends(get_async_db)):
    """
    Associa e ativa um cartão de PVC físico ao fluxo de consumo, gerando o Token do QR Code.
    """
    repo = AtendimentoRepository(db)
    
    # 1. Gera o token criptográfico primeiro usando o algoritmo HMAC-SHA256 (Operação CPU-bound síncrona nativa)
    token_pvc = gerar_token_comanda(payload.numero_pvc)
    
    # 2. Salva no banco de dados injetando o token de segurança obrigatório
    # 🔄 CORREÇÃO: Adicionado await para persistence assíncrona
    comanda = await repo.activar_comanda_pvc(numero_pvc=payload.numero_pvc, token_sessao=token_pvc)
    
    # 3. 🛡️ CORREÇÃO DA URL: IP completo da LAN sintonizado com a porta do PWA (5173) e roteamento limpo do React
    link_qr_code = f"http://192.168.111{payload.mesa_id_inicial}?pvc={comanda.numero_pvc}&token={comanda.token_sessao}"
    
    return {
        "comanda_id": comanda.id,
        "numero_pvc": comanda.numero_pvc,
        "status": comanda.status.value,
        "token_seguranca": comanda.token_sessao,
        "url_qr_code_cliente": link_qr_code
    }

# 🔄 OBSERVAÇÃO: Esta rota permanece sem await no retorno porque consome funções puras de CPU (hmac/hashlib)
@router.get("/comanda/{numero_pvc}/validar", status_code=status.HTTP_200_OK)
async def validar_acesso_autoatendimento(numero_pvc: int, token: str, db: AsyncSession = Depends(get_async_db)):
    """
    Endpoint de Validação Cruzada Omnichannel para o Web App do Cliente.
    Consome o seguranca.py original para validar o token enviado via smartphone.
    """
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
