"""PoC de decisão agentiva: seleção de eventos, chamada LLM e validação."""

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

import requests
from django.conf import settings
from django.utils import timezone

from api_tcc.models import Decision, Event, Machine

METHODOLOGY = "agentic_llm_poc"
PROMPT_VERSION = "agentic_decision_v1"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "agentic_decision_v1.txt"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
SEVERITIES = {Event.Severidade.NORMAL, Event.Severidade.ATENCAO, Event.Severidade.CRITICO}


class AgenticOutputError(ValueError):
    """Resposta do provedor ausente ou fora do contrato da PoC."""


def carregar_prompt(contexto: dict[str, Any]) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{{CONTEXT_JSON}}", json.dumps(contexto, ensure_ascii=False, indent=2, sort_keys=True))


def montar_contexto(machine: Machine, events: list[Event]) -> dict[str, Any]:
    return {
        "machine": {
            "id": str(machine.id),
            "external_code": machine.external_code,
            "organization": str(machine.organization_id) if machine.organization_id else None,
        },
        "operation_graph": {
            "status": "indisponivel_na_poc",
            "observacao": "Contexto S10 ainda não está disponível; usar apenas a Machine e os Events.",
        },
        "events": [
            {
                "id": str(event.id),
                "tipo": event.tipo,
                "severidade": event.severidade,
                "status": event.status,
                "priority_score": float(event.priority_score),
                "criado_em": event.criado_em.isoformat(),
                "dados_contexto": event.dados_contexto,
            }
            for event in events
        ],
    }


def extrair_texto_gemini(payload: dict[str, Any]) -> str:
    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise AgenticOutputError("resposta Gemini sem texto no formato esperado") from exc


def validar_saida(texto: str) -> dict[str, Any]:
    normalizado = texto.strip()
    if normalizado.startswith("```"):
        normalizado = normalizado.removeprefix("```").removeprefix("json").removesuffix("```").strip()
    try:
        saida = json.loads(normalizado)
    except json.JSONDecodeError as exc:
        raise AgenticOutputError("resposta Gemini não é JSON válido") from exc
    if not isinstance(saida, dict):
        raise AgenticOutputError("resposta Gemini não é um objeto JSON")
    for campo in ("texto", "acao_recomendada", "severidade", "confianca"):
        if campo not in saida:
            raise AgenticOutputError(f"campo obrigatório ausente: {campo}")
    if not isinstance(saida["texto"], str) or not saida["texto"].strip():
        raise AgenticOutputError("texto vazio")
    if not isinstance(saida["acao_recomendada"], str) or not saida["acao_recomendada"].strip():
        raise AgenticOutputError("acao_recomendada vazia")
    if saida["severidade"] not in SEVERITIES:
        raise AgenticOutputError("severidade fora do contrato")
    if isinstance(saida["confianca"], bool) or not isinstance(saida["confianca"], (int, float)):
        raise AgenticOutputError("confianca não numérica")
    if not 0 <= float(saida["confianca"]) <= 1:
        raise AgenticOutputError("confianca fora do intervalo 0..1")
    saida["confianca"] = float(saida["confianca"])
    return saida


def chamar_gemini(prompt: str) -> dict[str, Any]:
    api_key = str(getattr(settings, "GEMINI_API_KEY", "") or "").strip()
    if not api_key:
        raise AgenticOutputError("GEMINI_API_KEY não configurada")
    try:
        response = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=10.0,
        )
        response.raise_for_status()
        return validar_saida(extrair_texto_gemini(response.json()))
    except requests.RequestException as exc:
        raise AgenticOutputError(f"falha na chamada Gemini: {type(exc).__name__}") from exc


def candidatos_agenticos(*, horas: int = 24, limite_eventos: int = 5, machine_id: str | None = None):
    desde = timezone.now() - timedelta(hours=horas)
    queryset = Event.objects.filter(criado_em__gte=desde, priority_score__isnull=False).select_related("machine").order_by("machine_id", "-priority_score", "-criado_em")
    if machine_id:
        queryset = queryset.filter(machine__external_code=machine_id)
    agrupados: dict[Any, list[Event]] = {}
    for event in queryset:
        agrupados.setdefault(event.machine_id, []).append(event)
    return [(events[0].machine, events[:limite_eventos]) for events in agrupados.values()]


def decisao_agentica_existente(machine: Machine, *, desde) -> bool:
    return Decision.objects.filter(machine=machine, criado_em__gte=desde, detalhes__metodologia=METHODOLOGY).exists()


def persistir_decisao_agentica(machine: Machine, events: list[Event], saida: dict[str, Any]) -> Decision:
    return Decision.objects.create(
        machine=machine,
        event=events[0],
        texto=saida["texto"],
        acao_recomendada=saida["acao_recomendada"],
        severidade=saida["severidade"],
        confianca=saida["confianca"],
        status=Decision.Status.PENDENTE,
        detalhes={
            "metodologia": METHODOLOGY,
            "prompt_version": PROMPT_VERSION,
            "event_ids": [str(event.id) for event in events],
            "event_priority_scores": [float(event.priority_score) for event in events],
            "operation_graph": "indisponivel_na_poc",
        },
    )
