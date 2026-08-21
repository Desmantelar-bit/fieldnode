"""
Camada de explicação em linguagem natural. Recebe um ResultadoAnalise
já decidido pelo pipeline determinístico e devolve texto explicativo.
NUNCA decide status sozinha. Sempre tem fallback.
"""
import logging
import time

import requests
from django.conf import settings

from api_tcc.ia.pipeline import ResultadoAnalise

logger = logging.getLogger('fieldnode.ia.llm')

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.6-flash:generateContent"
)

# circuit breaker simples em memória
_falhas_consecutivas = 0
_ultima_falha_ts = 0
LIMITE_FALHAS = 3
JANELA_DEGRADADA_SEGUNDOS = 120


def _circuito_aberto() -> bool:
    global _falhas_consecutivas, _ultima_falha_ts
    if _falhas_consecutivas < LIMITE_FALHAS:
        return False
    if time.time() - _ultima_falha_ts > JANELA_DEGRADADA_SEGUNDOS:
        _falhas_consecutivas = 0  # janela expirou, tenta de novo
        return False
    return True


def _registrar_falha():
    global _falhas_consecutivas, _ultima_falha_ts
    _falhas_consecutivas += 1
    _ultima_falha_ts = time.time()


def _montar_prompt(resultado: ResultadoAnalise) -> str:
    return (
        "Você é um assistente técnico de manutenção agrícola. "
        "Com base nos dados a seguir, escreva uma explicação curta (máximo 2 frases) "
        "em português, para um operador de campo, sem jargão técnico excessivo.\n\n"
        f"Máquina: {resultado.maquina_id}\n"
        f"Status classificado pelo sistema: {resultado.status}\n"
        f"Motivos identificados: {'; '.join(resultado.motivos)}\n"
        f"Recomendação já calculada pelo sistema: {resultado.recomendacao}\n\n"
        "Reescreva a recomendação de forma clara e direta, mantendo o mesmo "
        "nível de severidade. Não invente informação que não esteja nos dados acima."
    )


def gerar_explicacao_natural(resultado: ResultadoAnalise) -> dict:
    """
    Retorna sempre um dict com 'texto' e 'fonte'.
    Nunca lança exceção pro caller — o fallback é interno.
    """
    if resultado.status == 'NORMAL':
        return {'texto': 'Máquina operando dentro dos parâmetros esperados.', 'fonte': 'determinístico'}

    if _circuito_aberto():
        logger.warning("circuito de IA generativa aberto — usando fallback direto")
        return {'texto': resultado.recomendacao, 'fonte': 'fallback_determinístico'}

    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": _montar_prompt(resultado)}]}]},
            timeout=2.0,  # CRÍTICO: timeout curto
        )
        resp.raise_for_status()
        texto = resp.json()['candidates'][0]['content']['parts'][0]['text']
        _falhas_consecutivas_reset_se_sucesso()
        return {'texto': texto.strip(), 'fonte': 'ia_generativa'}
    except (requests.RequestException, KeyError, IndexError) as exc:
        logger.warning(
            "falha na chamada ao Gemini (%s) — usando fallback",
            type(exc).__name__,
        )
        _registrar_falha()
        return {'texto': resultado.recomendacao, 'fonte': 'fallback_determinístico'}


def _falhas_consecutivas_reset_se_sucesso():
    global _falhas_consecutivas
    _falhas_consecutivas = 0
