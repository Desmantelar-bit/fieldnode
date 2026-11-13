"""
Camada de explicação em linguagem natural. Recebe um ResultadoAnalise
já decidido pelo pipeline determinístico e devolve texto explicativo.
NUNCA decide status sozinha. Sempre tem fallback.
"""
import logging
import threading
import time

import requests
from django.conf import settings
from django.core.cache import cache

from api_tcc.ia.pipeline import ResultadoAnalise

logger = logging.getLogger('fieldnode.ia.llm')

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.6-flash:generateContent"
)

# Circuit breaker por processo: três falhas consecutivas abrem por 120 s.
_falhas_consecutivas = 0
_ultima_falha_ts = 0
LIMITE_FALHAS = 3
JANELA_DEGRADADA_SEGUNDOS = 120
_circuito_lock = threading.Lock()
_tentativa_half_open = False
_CACHE_EXPLICACAO_TTL = 3600
_CACHE_FALLBACK_TTL = JANELA_DEGRADADA_SEGUNDOS


def _circuito_aberto() -> bool:
    global _falhas_consecutivas, _ultima_falha_ts
    if _falhas_consecutivas < LIMITE_FALHAS:
        return False
    if time.time() - _ultima_falha_ts > JANELA_DEGRADADA_SEGUNDOS:
        _falhas_consecutivas = 0  # janela expirou, tenta de novo
        return False
    return True


def _pode_chamar_provedor() -> bool:
    """Permite uma única tentativa HALF_OPEN após expirar o período aberto."""
    global _falhas_consecutivas, _tentativa_half_open
    with _circuito_lock:
        if _falhas_consecutivas < LIMITE_FALHAS:
            return True
        if time.time() - _ultima_falha_ts <= JANELA_DEGRADADA_SEGUNDOS:
            return False
        if _tentativa_half_open:
            return False
        _tentativa_half_open = True
        return True


def _registrar_falha():
    global _falhas_consecutivas, _ultima_falha_ts
    global _tentativa_half_open
    with _circuito_lock:
        _falhas_consecutivas += 1
        _ultima_falha_ts = time.time()
        _tentativa_half_open = False


def _registrar_sucesso():
    global _falhas_consecutivas, _tentativa_half_open
    with _circuito_lock:
        _falhas_consecutivas = 0
        _tentativa_half_open = False


def _cache_key(decision_id):
    return f"fieldnode:llm:explanation:{decision_id}"


def _cache_get(key):
    try:
        return cache.get(key)
    except Exception as exc:
        logger.warning("cache de explicação indisponível (%s)", type(exc).__name__)
        return None


def _cache_set(key, value, timeout):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception as exc:
        logger.warning("persistência de explicação indisponível (%s)", type(exc).__name__)


def _cache_add(key, value, timeout):
    try:
        return cache.add(key, value, timeout=timeout)
    except Exception as exc:
        logger.warning("lock de explicação indisponível (%s)", type(exc).__name__)
        return True


def _cache_delete(key):
    try:
        cache.delete(key)
    except Exception as exc:
        logger.warning("liberação de lock da explicação indisponível (%s)", type(exc).__name__)


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


def gerar_explicacao_natural(resultado: ResultadoAnalise, decision_id=None) -> dict:
    """
    Retorna sempre um dict com 'texto' e 'fonte'.
    Nunca lança exceção pro caller — o fallback é interno.
    """
    if resultado.status == 'NORMAL':
        return {'texto': 'Máquina operando dentro dos parâmetros esperados.', 'fonte': 'determinístico'}

    cache_key = _cache_key(decision_id) if decision_id else None
    if cache_key:
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached
        # Uma única requisição por decisão pode chamar o provedor. As demais
        # recebem fallback determinístico e não duplicam uma chamada em voo.
        lock_key = f"{cache_key}:lock"
        if not _cache_add(lock_key, True, timeout=10):
            return {'texto': resultado.recomendacao, 'fonte': 'fallback_determinístico'}
    else:
        lock_key = None

    try:
        if not _pode_chamar_provedor():
            logger.warning("circuito Gemini aberto — usando fallback determinístico")
            resposta = {'texto': resultado.recomendacao, 'fonte': 'fallback_determinístico'}
            if cache_key:
                _cache_set(cache_key, resposta, _CACHE_FALLBACK_TTL)
            return resposta

        api_key = str(getattr(settings, 'GEMINI_API_KEY', '') or '').strip()
        if not api_key:
            logger.warning("GEMINI_API_KEY ausente — usando fallback determinístico")
            _registrar_falha()
            resposta = {'texto': resultado.recomendacao, 'fonte': 'fallback_determinístico'}
            if cache_key:
                _cache_set(cache_key, resposta, _CACHE_FALLBACK_TTL)
            return resposta
        resp = requests.post(
            GEMINI_URL,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": _montar_prompt(resultado)}]}]},
            timeout=2.0,
        )
        resp.raise_for_status()
        texto = resp.json()['candidates'][0]['content']['parts'][0]['text']
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("resposta Gemini vazia")
        _registrar_sucesso()
        resposta = {'texto': texto.strip(), 'fonte': 'ia_generativa'}
        if cache_key:
            _cache_set(cache_key, resposta, _CACHE_EXPLICACAO_TTL)
        return resposta
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as exc:
        logger.warning(
            "falha na chamada ao Gemini (%s) — usando fallback",
            type(exc).__name__,
        )
        _registrar_falha()
        resposta = {'texto': resultado.recomendacao, 'fonte': 'fallback_determinístico'}
        if cache_key:
            _cache_set(cache_key, resposta, _CACHE_FALLBACK_TTL)
        return resposta
    finally:
        if lock_key:
            _cache_delete(lock_key)


def _falhas_consecutivas_reset_se_sucesso():
    _registrar_sucesso()
