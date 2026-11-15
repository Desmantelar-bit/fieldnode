"""Contrato versionado para a explicacao persistida de uma Decision."""
import json
from datetime import date, datetime
from pathlib import Path

from django.core.exceptions import ValidationError


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "decision_v1.json"
DECISION_SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_datetime(value):
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_decision_details(value):
    """Valida decision.v1 sem depender de um pacote externo em runtime."""
    errors = []
    if not isinstance(value, dict):
        raise ValidationError("detalhes precisa ser um objeto JSON.")
    required = DECISION_SCHEMA["required"]
    missing = [field for field in required if field not in value]
    if missing:
        errors.append(f"campos obrigatorios ausentes: {', '.join(missing)}")
    if value.get("schema") != "decision.v1":
        errors.append("schema deve ser decision.v1")
    if not isinstance(value.get("observado"), str) or not value.get("observado", "").strip():
        errors.append("observado deve ser texto nao vazio")

    evidencias = value.get("evidencias")
    if not isinstance(evidencias, list) or not evidencias:
        errors.append("evidencias deve conter pelo menos uma leitura")
    else:
        for index, evidence in enumerate(evidencias):
            fields = {"leitura_id", "campo", "valor", "limiar", "event_time"}
            if not isinstance(evidence, dict) or not fields.issubset(evidence):
                errors.append(f"evidencias[{index}] fora do contrato")
                continue
            if not isinstance(evidence["leitura_id"], str) or not evidence["leitura_id"]:
                errors.append(f"evidencias[{index}].leitura_id invalido")
            if not isinstance(evidence["campo"], str) or not evidence["campo"]:
                errors.append(f"evidencias[{index}].campo invalido")
            if evidence["valor"] is not None and not _is_number(evidence["valor"]):
                errors.append(f"evidencias[{index}].valor invalido")
            if evidence["limiar"] is not None and not _is_number(evidence["limiar"]):
                errors.append(f"evidencias[{index}].limiar invalido")
            if not _is_datetime(evidence["event_time"]):
                errors.append(f"evidencias[{index}].event_time invalido")

    window = value.get("janela_analisada")
    if not isinstance(window, dict) or not all(key in window for key in ("inicio", "fim", "n_leituras")):
        errors.append("janela_analisada fora do contrato")
    elif not (_is_datetime(window["inicio"]) and _is_datetime(window["fim"]) and isinstance(window["n_leituras"], int) and not isinstance(window["n_leituras"], bool) and window["n_leituras"] >= 1):
        errors.append("janela_analisada possui valores invalidos")

    quality = value.get("qualidade_dado")
    if not isinstance(quality, dict) or quality.get("evidence_quality") not in {"boa", "suspeita", "insuficiente"} or not isinstance(quality.get("fatores"), list):
        errors.append("qualidade_dado fora do contrato")
    for object_name in ("regra", "modelo"):
        if not isinstance(value.get(object_name), dict):
            errors.append(f"{object_name} fora do contrato")
    if isinstance(value.get("regra"), dict) and not all(isinstance(value["regra"].get(k), str) and value["regra"][k] for k in ("id", "versao")):
        errors.append("regra.id e regra.versao sao obrigatorios")
    if isinstance(value.get("modelo"), dict):
        model = value["modelo"]
        if not isinstance(model.get("id"), str) or not model["id"] or (model.get("score") is not None and (not _is_number(model["score"]) or not 0 <= model["score"] <= 1)):
            errors.append("modelo fora do contrato")
    if not isinstance(value.get("dados_faltantes"), list) or not all(isinstance(item, str) for item in value.get("dados_faltantes", [])):
        errors.append("dados_faltantes fora do contrato")
    horizon = value.get("horizonte_minutos")
    if horizon is not None and (not isinstance(horizon, int) or isinstance(horizon, bool) or horizon < 0):
        errors.append("horizonte_minutos deve ser inteiro nao negativo ou null")
    if not isinstance(value.get("alternativas"), list) or not all(isinstance(item, str) for item in value.get("alternativas", [])):
        errors.append("alternativas fora do contrato")
    if errors:
        raise ValidationError({"detalhes": errors})
    return value
