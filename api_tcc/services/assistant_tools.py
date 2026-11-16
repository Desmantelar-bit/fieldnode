"""Allowlist de consultas do assistente. Nenhuma ferramenta escreve no domínio."""

from uuid import UUID

from django.db.models import Q

from api_tcc.models import Decision, Event, Machine, MachineDataHealth
from api_tcc.permissions import get_machines_for_user


TOOL_SCHEMAS = {
    "listar_maquinas_criticas": {"limit"},
    "explicar_decisao": {"id"},
    "saude_da_maquina": {"id"},
    "eventos_recentes": {"id", "limit"},
}
READ_ONLY_TOOLS = frozenset(TOOL_SCHEMAS)


def _args(name, arguments):
    if name not in READ_ONLY_TOOLS or not isinstance(arguments, dict):
        raise ValueError("ferramenta não autorizada")
    if set(arguments) - TOOL_SCHEMAS[name]:
        raise ValueError("argumentos extras não autorizados")
    if name in {"explicar_decisao", "saude_da_maquina", "eventos_recentes"}:
        try:
            value = UUID(str(arguments["id"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("id inválido") from exc
        arguments = {**arguments, "id": value}
    if "limit" in arguments:
        try:
            limit = int(arguments["limit"])
        except (TypeError, ValueError) as exc:
            raise ValueError("limit inválido") from exc
        if limit < 1 or limit > 20:
            raise ValueError("limit fora do intervalo permitido")
        arguments = {**arguments, "limit": limit}
    return arguments


def _machines(user):
    return get_machines_for_user(user).filter(ativo=True)


def listar_maquinas_criticas(user, *, limit=20):
    qs = _machines(user).filter(events__severidade=Event.Severidade.CRITICO, events__status=Event.Status.ABERTO).distinct().order_by("external_code")[:limit]
    return {"resultados": [{"machine_id": str(m.id), "maquina_id": m.external_code, "citacoes": [str(m.id)]} for m in qs]}


def explicar_decisao(user, *, id):
    decision = Decision.objects.select_related("machine").filter(id=id, machine__in=_machines(user)).first()
    if decision is None:
        return {"mensagem": "Não encontrada.", "citacoes": []}
    detalhes = decision.detalhes if isinstance(decision.detalhes, dict) else {}
    evidencias = detalhes.get("evidencias", []) if isinstance(detalhes.get("evidencias", []), list) else []
    return {"decision_id": str(decision.id), "texto": decision.texto, "status": decision.status, "evidencias_citadas": [str(e.get("leitura_id")) for e in evidencias if e.get("leitura_id")], "citacoes": [str(decision.id)]}


def saude_da_maquina(user, *, id):
    machine = _machines(user).filter(id=id).first()
    if machine is None:
        return {"mensagem": "Não encontrada.", "citacoes": []}
    health = MachineDataHealth.objects.filter(machine=machine).first()
    if health is None:
        estado = "ausente"
        payload = {"machine_id": str(machine.id), "estado": estado, "citacoes": [str(machine.id)]}
    else:
        payload = {"machine_id": str(machine.id), "estado": "disponivel", "trust_score_medio": health.trust_score_medio, "ultima_atualizacao": health.ultima_atualizacao.isoformat(), "leituras_analisadas": health.leituras_analisadas, "citacoes": [str(machine.id)]}
    return payload


def eventos_recentes(user, *, id, limit=20):
    machine = _machines(user).filter(id=id).first()
    if machine is None:
        return {"mensagem": "Não encontrada.", "citacoes": []}
    events = Event.objects.filter(machine=machine).select_related("leitura_origem").order_by("-leitura_origem__timestamp", "-criado_em", "-id")[:limit]
    return {"machine_id": str(machine.id), "eventos": [{"event_id": str(event.id), "tipo": event.tipo, "severidade": event.severidade, "event_time": event.leitura_origem.timestamp.isoformat() if event.leitura_origem and event.leitura_origem.timestamp else None, "ingested_at": event.criado_em.isoformat(), "citacoes": [str(event.id)]} for event in events], "citacoes": [str(machine.id)]}


def execute_tool(user, name, arguments):
    args = _args(name, arguments)
    if name == "listar_maquinas_criticas":
        return listar_maquinas_criticas(user, limit=args.get("limit", 20))
    if name == "explicar_decisao":
        return explicar_decisao(user, id=args["id"])
    if name == "saude_da_maquina":
        return saude_da_maquina(user, id=args["id"])
    return eventos_recentes(user, id=args["id"], limit=args.get("limit", 20))
