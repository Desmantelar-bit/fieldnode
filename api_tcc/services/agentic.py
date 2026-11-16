"""PoC de decisão agentiva: seleção de eventos, chamada LLM e validação."""

import json
import re
from datetime import timedelta
from pathlib import Path
from typing import Any

import requests
from django.conf import settings
from django.utils import timezone

from api_tcc.models import Decision, Event, Machine
from api_tcc.services.decisions import criar_decision
from api_tcc.services.decision_schema import validate_decision_details

METHODOLOGY = "agentic_llm_poc"
PROMPT_VERSION = "agentic_decision_v1"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "agentic_decision_v1.txt"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
SEVERITIES = {Event.Severidade.NORMAL, Event.Severidade.ATENCAO, Event.Severidade.CRITICO}


class AgenticOutputError(ValueError):
    """Resposta do provedor ausente ou fora do contrato da PoC."""


EXPLANATION_FIELDS = frozenset({"texto", "evidencias_citadas"})
_NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])-?(?:\d+(?:[.,]\d+)?)")


def carregar_prompt(contexto: dict[str, Any]) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{{CONTEXT_JSON}}", json.dumps(contexto, ensure_ascii=False, indent=2, sort_keys=True))


def montar_decision_v1(machine: Machine, events: list[Event]) -> dict[str, Any]:
    """Cria o único contexto autorizado para a explicação do LLM."""
    evidencias = []
    for event in events:
        dados = event.dados_contexto if isinstance(event.dados_contexto, dict) else {}
        itens = [(campo, valor) for campo, valor in dados.items() if isinstance(valor, (int, float)) and not isinstance(valor, bool)]
        if not itens:
            itens = [(event.tipo, None)]
        for campo, valor in itens:
            evidencias.append({
                "leitura_id": str(event.leitura_origem_id or event.id),
                "campo": str(campo),
                "valor": valor,
                "limiar": dados.get("limite_critico") if isinstance(dados.get("limite_critico"), (int, float)) else None,
                "event_time": event.criado_em.isoformat(),
            })
    contexto = {
        "schema": "decision.v1",
        "observado": "Eventos selecionados pelo pipeline para explicação.",
        "evidencias": evidencias,
        "janela_analisada": {"inicio": events[-1].criado_em.isoformat(), "fim": events[0].criado_em.isoformat(), "n_leituras": max(1, len({e["leitura_id"] for e in evidencias}))},
        "qualidade_dado": {"evidence_quality": events[0].evidence_quality, "fatores": []},
        "regra": {"id": "AGENTIC_LLM", "versao": PROMPT_VERSION},
        "modelo": {"id": "agentic-selection", "score": None, "contribuinte": None},
        "dados_faltantes": [], "horizonte_minutos": None, "alternativas": [],
    }
    validate_decision_details(contexto)
    return contexto


def montar_contexto(machine: Machine, events: list[Event]) -> dict[str, Any]:
    return montar_decision_v1(machine, events)


def validar_explicacao(texto: str, decision_v1: dict[str, Any]) -> dict[str, Any]:
    """Valida o contrato estrito da explicação antes de exibi-la."""
    validate_decision_details(decision_v1)
    try:
        saida = json.loads(texto.strip())
    except (TypeError, json.JSONDecodeError) as exc:
        raise AgenticOutputError("explicação não é JSON válido") from exc
    if not isinstance(saida, dict) or set(saida) != EXPLANATION_FIELDS:
        raise AgenticOutputError("schema de explicação incompatível")
    if not isinstance(saida["texto"], str) or not saida["texto"].strip():
        raise AgenticOutputError("texto vazio")
    citadas = saida["evidencias_citadas"]
    ids = {str(item["leitura_id"]) for item in decision_v1["evidencias"]}
    if not isinstance(citadas, list) or not citadas or not all(isinstance(item, str) and item in ids for item in citadas):
        raise AgenticOutputError("evidência citada inexistente ou ausente")
    autorizados = {str(value).replace(",", ".") for evidencia in decision_v1["evidencias"] for value in (evidencia.get("valor"), evidencia.get("limiar")) if value is not None}
    for token in _NUMBER_RE.findall(saida["texto"]):
        if token.replace(",", ".") not in autorizados:
            raise AgenticOutputError("número sem respaldo em evidências ou limiares")
    return saida


def chamar_explicacao_gemini(decision_v1: dict[str, Any]) -> dict[str, Any]:
    """Chama o provedor somente com decision.v1 e valida antes de retornar."""
    api_key = str(getattr(settings, "GEMINI_API_KEY", "") or "").strip()
    if not api_key:
        raise AgenticOutputError("GEMINI_API_KEY não configurada")
    try:
        response = requests.post(
            GEMINI_URL,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": carregar_prompt(decision_v1)}]}], "generationConfig": {"temperature": 0}},
            timeout=2.0,
        )
        response.raise_for_status()
        return validar_explicacao(extrair_texto_gemini(response.json()), decision_v1)
    except requests.RequestException as exc:
        raise AgenticOutputError(f"falha na chamada Gemini: {type(exc).__name__}") from None


def explicacao_deterministica(decision_v1: dict[str, Any]) -> dict[str, Any]:
    """Fallback sem provedor: descreve apenas que há evidências registradas."""
    return {
        "texto": "Há evidências registradas para esta decisão; os dados disponíveis não permitem concluir além do que foi observado.",
        "evidencias_citadas": [str(item["leitura_id"]) for item in decision_v1["evidencias"]],
        "fonte": "deterministic_fallback",
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
            GEMINI_URL,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=2.0,
        )
        response.raise_for_status()
        return validar_saida(extrair_texto_gemini(response.json()))
    except requests.RequestException as exc:
        raise AgenticOutputError(f"falha na chamada Gemini: {type(exc).__name__}") from None


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


def persistir_decisao_agentica(machine: Machine, events: list[Event], saida: dict[str, Any], decision_v1: dict[str, Any] | None = None) -> Decision:
    evidence_events = [event for event in events if event.leitura_origem_id]
    if not evidence_events:
        raise ValueError("Decision rejeitada: eventos agenticos sem leitura de evidencia.")
    decision_v1 = decision_v1 or montar_decision_v1(machine, events)
    confianca = saida.get("confianca", float(events[0].priority_score or 0))
    return criar_decision(
        machine=machine,
        event=events[0],
        texto=saida["texto"],
        acao_recomendada=saida.get("acao_recomendada", "Revisar as evidências citadas antes de qualquer ação."),
        severidade=saida.get("severidade", events[0].severidade),
        confianca=confianca,
        status=Decision.Status.PENDENTE,
        detalhes={
            "schema": "decision.v1",
            "observado": saida["texto"],
            "evidencias": decision_v1["evidencias"],
            "janela_analisada": {"inicio": events[-1].criado_em.isoformat(), "fim": events[0].criado_em.isoformat(), "n_leituras": len(evidence_events)},
            "qualidade_dado": {"evidence_quality": events[0].evidence_quality, "fatores": []},
            "regra": {"id": "AGENTIC_LLM", "versao": PROMPT_VERSION},
            "modelo": {"id": "gemini-2.5-flash", "score": confianca, "contribuinte": None},
            "dados_faltantes": [], "horizonte_minutos": None, "alternativas": [],
            "metodologia": METHODOLOGY,
            "prompt_version": PROMPT_VERSION,
            "event_ids": [str(event.id) for event in events],
            "event_priority_scores": [float(event.priority_score) for event in events],
            "operation_graph": "indisponivel_na_poc",
            "explicacao": {"fonte": saida.get("fonte", "llm_validated"), "evidencias_citadas": saida.get("evidencias_citadas", [])},
        },
    )
