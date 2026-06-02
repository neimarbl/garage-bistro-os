# backend/app/core/seguranca.py
import hmac
import hashlib
import os

# Em produção, essa chave vem das variáveis do ambiente do evento. Aqui criamos um fallback seguro.
SECRET_KEY = os.getenv("SECRET_KEY", "chave_secreta_garage_bistro_2026_sd9f87gh23")

def gerar_token_comanda(numero_pvc: int) -> str:
    """
    Gera uma assinatura digital criptográfica única para o número da comanda em PVC.
    """
    mensagem = f"comanda:{numero_pvc}".encode('utf-8')
    assinatura = hmac.new(SECRET_KEY.encode('utf-8'), mensagem, hashlib.sha256)
    return assinatura.hexdigest()

def validar_token_comanda(numero_pvc: int, token_recebido: str) -> bool:
    """
    Compara o token recebido do celular do cliente com o token real gerado pelo algoritmo.
    Usa hmac.compare_digest para evitar ataques de temporização (Timing Attacks) no portfólio.
    """
    token_esperado = gerar_token_comanda(numero_pvc)
    return hmac.compare_digest(token_esperado, token_recebido)
