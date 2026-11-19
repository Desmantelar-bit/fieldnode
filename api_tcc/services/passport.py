"""Data Passport v0.1: exportacao verificavel e importacao controlada."""
from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import secrets
import zipfile
from datetime import datetime
from uuid import UUID, uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from api_tcc.models import Decision, Event, LeituraTelemetria, Machine, Organization, WorkOrder

PASSPORT_VERSION = "0.1"
SCHEMA_VERSION = "fieldnode-data-passport-0.1"
TELEMETRY_FIELDS = [
    "id", "machine_id", "machine_external_code", "device_id", "message_id", "sequence_number",
    "timestamp", "recebido_em", "temperatura", "vibracao", "vibracao_unit", "rpm",
    "velocidade_kmh", "regime", "evidence_quality", "latitude", "longitude", "source",
    "data_origin", "transport", "payload_hash", "sync_status", "priority_class", "time_source",
    "event_time_confidence", "trust_score", "agregada",
]
DATA_FILES = ("telemetry.csv", "events.json", "decisions.json", "work_orders.json", "provenance.json", "FORMAT.md")


def _json_default(value):
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    return value


def canonical_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=_json_default).encode("utf-8")


def _record(model, *, include_private=False):
    data = {field.attname: getattr(model, field.attname) for field in model._meta.fields}
    if not include_private:
        for key in ("webhook_secret", "token_hash", "password"):
            data.pop(key, None)
    return data


def _json_records(queryset):
    return [{key: _json_default(value) for key, value in _record(item).items()} for item in queryset]


def _entity_records(queryset):
    records = _json_records(queryset)
    for item, record in zip(queryset, records):
        record["machine_external_code"] = item.machine.external_code
    return records


def _scope_queryset(organization, machine=None, start=None, end=None):
    machines = Machine.objects.filter(organization=organization)
    if machine:
        machines = machines.filter(pk=machine.pk)
    readings = LeituraTelemetria.objects.filter(machine__in=machines).select_related("machine").order_by("timestamp", "id")
    events = Event.objects.filter(machine__in=machines).select_related("machine", "leitura_origem").order_by("criado_em", "id")
    decisions = Decision.objects.filter(machine__in=machines).select_related("machine", "event").order_by("criado_em", "id")
    work_orders = WorkOrder.objects.filter(machine__in=machines).select_related("machine", "decision").order_by("criado_em", "id")
    if start:
        readings = readings.filter(timestamp__gte=start); events = events.filter(criado_em__gte=start); decisions = decisions.filter(criado_em__gte=start); work_orders = work_orders.filter(criado_em__gte=start)
    if end:
        readings = readings.filter(timestamp__lte=end); events = events.filter(criado_em__lte=end); decisions = decisions.filter(criado_em__lte=end); work_orders = work_orders.filter(criado_em__lte=end)
    return machines, readings, events, decisions, work_orders


def _telemetry_csv(readings):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=TELEMETRY_FIELDS, lineterminator="\n")
    writer.writeheader()
    count = 0
    first = last = None
    for item in readings.iterator(chunk_size=1000):
        row = {field: _json_default(getattr(item, field, None)) for field in TELEMETRY_FIELDS}
        row["machine_external_code"] = item.machine.external_code
        writer.writerow(row); count += 1
        if item.timestamp and first is None: first = item.timestamp
        if item.timestamp: last = item.timestamp
    return output.getvalue().encode("utf-8"), count, first, last


def _signature_payload(manifest):
    unsigned = dict(manifest)
    unsigned["signature"] = None
    return canonical_json(unsigned)


def _sign(manifest):
    key = str(getattr(settings, "FIELDNODE_PASSPORT_SIGNING_KEY", ""))
    if not key:
        return {"status": "unavailable", "algorithm": "HMAC-SHA256", "key_id": ""}
    digest = hmac.new(key.encode(), _signature_payload(manifest), hashlib.sha256).hexdigest()
    return {"status": "signed", "algorithm": "HMAC-SHA256", "key_id": getattr(settings, "FIELDNODE_PASSPORT_SIGNING_KEY_ID", "default"), "value": digest}


def verify_manifest_signature(manifest):
    signature = manifest.get("signature") or {}
    key = str(getattr(settings, "FIELDNODE_PASSPORT_SIGNING_KEY", ""))
    if signature.get("status") != "signed" or not key:
        return False, "assinatura indisponivel ou chave de confianca ausente"
    expected = hmac.new(key.encode(), _signature_payload(manifest), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature.get("value", "")):
        return False, "assinatura invalida"
    return True, "ok"


def export_passport(*, organization, machine=None, start=None, end=None):
    """Retorna bytes ZIP; consultas usam iterator para não materializar telemetria inteira."""
    machines, readings, events, decisions, work_orders = _scope_queryset(organization, machine, start, end)
    telemetry, telemetry_count, actual_start, actual_end = _telemetry_csv(readings)
    datasets = {
        "telemetry.csv": telemetry,
        "events.json": canonical_json(_entity_records(events)),
        "decisions.json": canonical_json(_entity_records(decisions)),
        "work_orders.json": canonical_json(_entity_records(work_orders)),
        "provenance.json": canonical_json({"schema_version": SCHEMA_VERSION, "telemetry_fields": TELEMETRY_FIELDS, "notes": ["timestamp e event_time sao distintos de recebido_em e ingested_at.", "assinatura nao prova veracidade fisica."]}),
        "FORMAT.md": b"# FieldNode Data Passport v0.1\n\ntelemetry.csv usa UTF-8, cabecalho estavel e timestamps ISO-8601. Hashes sao SHA-256 dos bytes armazenados. A assinatura HMAC identifica a configuracao confiavel do gerador; nao prova a origem fisica da medicao.\n",
    }
    manifest = {
        "passport_version": PASSPORT_VERSION, "schema_version": SCHEMA_VERSION, "export_id": str(uuid4()),
        "generated_at": timezone.now().isoformat(), "scope": {"organization_id": str(organization.id), "organization_name": organization.nome, "machine_ids": [str(m.id) for m in machines], "machine_external_codes": list(machines.values_list("external_code", flat=True))},
        "requested_interval": {"start": _json_default(start), "end": _json_default(end)},
        "included_interval": {"start": _json_default(actual_start), "end": _json_default(actual_end)},
        "files": {}, "record_counts": {"telemetry": telemetry_count, "events": events.count(), "decisions": decisions.count(), "work_orders": work_orders.count()},
        "status": "complete", "hash_algorithm": "SHA-256", "signature": None,
        "limitations": ["Exportacao inclui leituras de telemetria persistidas e entidades operacionais existentes; anexos externos nao sao copiados."],
    }
    for name, content in datasets.items():
        manifest["files"][name] = {"size": len(content), "sha256": hashlib.sha256(content).hexdigest()}
    manifest["signature"] = _sign(manifest)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", canonical_json(manifest))
        for name, content in datasets.items(): archive.writestr(name, content)
    return output.getvalue()


def validate_passport(blob):
    if len(blob) > getattr(settings, "FIELDNODE_PASSPORT_MAX_BYTES", 250 * 1024 * 1024): raise ValueError("passport excede limite de tamanho")
    try: archive = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile as exc: raise ValueError("ZIP invalido") from exc
    names = set(archive.namelist())
    if "manifest.json" not in names: raise ValueError("manifest.json ausente")
    if any(name.startswith("/") or ".." in name.split("/") for name in names): raise ValueError("caminho inseguro no ZIP")
    manifest = json.loads(archive.read("manifest.json"))
    if manifest.get("passport_version") != PASSPORT_VERSION: raise ValueError("versao de Passport nao suportada")
    for name, metadata in manifest.get("files", {}).items():
        if name not in names: raise ValueError(f"arquivo declarado ausente: {name}")
        if hashlib.sha256(archive.read(name)).hexdigest() != metadata.get("sha256"): raise ValueError(f"hash invalido: {name}")
    signed, reason = verify_manifest_signature(manifest)
    if manifest.get("signature", {}).get("status") == "signed" and not signed: raise ValueError(reason)
    return archive, manifest


@transaction.atomic
def import_passport(blob, *, organization, allow_unsigned=False):
    archive, manifest = validate_passport(blob)
    if manifest.get("signature", {}).get("status") != "signed" and not allow_unsigned: raise ValueError("importacao exige Passport assinado")
    machines = {}
    for code in manifest["scope"].get("machine_external_codes", []):
        machine = Machine.objects.filter(organization=organization, external_code=code).first()
        if machine is None:
            imported_code = code
            if Machine.objects.filter(external_code=imported_code).exists():
                imported_code = f"{code}-IMPORT"
                suffix = 2
                while Machine.objects.filter(external_code=imported_code).exists():
                    imported_code = f"{code}-IMPORT-{suffix}"; suffix += 1
            machine = Machine.objects.create(organization=organization, external_code=imported_code, ativo=True)
        machines[code] = machine
    actor = organization.membership_set.select_related("user").filter(role__in=("admin", "member")).first()
    if not actor:
        raise ValueError("organização de destino não possui membro para atribuir registros")
    reader = csv.DictReader(io.TextIOWrapper(io.BytesIO(archive.read("telemetry.csv")), encoding="utf-8"))
    telemetry_count = 0
    reading_map = {}
    for row in reader:
        machine = machines.get(row["machine_external_code"])
        if not machine: raise ValueError("maquina fora do escopo do Passport")
        device_id, message_id = row["device_id"], row["message_id"]
        existing = LeituraTelemetria.objects.filter(device_id=device_id, message_id=message_id).select_related("machine").first()
        if existing and existing.machine_id != machine.id:
            message_id = f"{message_id}-IMPORT"
        imported_id = row["id"] if not LeituraTelemetria.objects.filter(pk=row["id"]).exists() else str(uuid4())
        reading, _ = LeituraTelemetria.objects.get_or_create(device_id=device_id, message_id=message_id, defaults={"id": imported_id, "maquina_id": row["machine_external_code"], "machine": machine, "sequence_number": int(row["sequence_number"] or 0), "timestamp": row["timestamp"] or None, "temperatura": float(row["temperatura"]), "vibracao": float(row["vibracao"]), "vibracao_unit": row["vibracao_unit"], "rpm": int(row["rpm"]) if row["rpm"] else None, "velocidade_kmh": float(row["velocidade_kmh"]) if row["velocidade_kmh"] else None, "regime": row["regime"], "evidence_quality": row["evidence_quality"], "source": row["source"], "data_origin": row["data_origin"] or None, "transport": row["transport"], "payload_hash": row["payload_hash"] or None, "sync_status": row["sync_status"], "priority_class": row["priority_class"], "time_source": row["time_source"], "event_time_confidence": float(row["event_time_confidence"] or 0), "trust_score": float(row["trust_score"]) if row["trust_score"] else None, "agregada": row["agregada"].lower() == "true"})
        reading_map[str(row["id"])] = reading
        telemetry_count += 1
    event_map = {}
    for data in json.loads(archive.read("events.json")):
        machine = machines.get(str(data.get("machine_id"))) or machines.get(data.get("machine_external_code"))
        if machine:
            event, _ = Event.objects.get_or_create(id=data["id"], defaults={"machine": machine, "leitura_origem": reading_map.get(str(data.get("leitura_origem_id"))), "tipo": data["tipo"], "severidade": data["severidade"], "status": data["status"], "trust_score_herdado": data.get("trust_score_herdado"), "evidence_quality": data.get("evidence_quality", "insuficiente"), "needs_verification": data.get("needs_verification", True), "priority_score": data.get("priority_score"), "criado_em": data.get("criado_em"), "dados_contexto": data.get("dados_contexto") or {}})
            event_map[str(event.id)] = event
    decision_count = 0
    decision_map = {}
    for data in json.loads(archive.read("decisions.json")):
        machine = machines.get(str(data.get("machine_id"))) or machines.get(data.get("machine_external_code"))
        if machine:
            decision, _ = Decision.objects.get_or_create(id=data["id"], defaults={"machine": machine, "event": event_map.get(str(data.get("event_id"))), "texto": data["texto"], "acao_recomendada": data["acao_recomendada"], "severidade": data["severidade"], "confianca": data.get("confianca"), "status": data["status"], "criado_em": data.get("criado_em"), "decidido_por_id": data.get("decidido_por_id") or actor.user_id, "decidido_em": data.get("decidido_em"), "outcome_texto": data.get("outcome_texto"), "motivo_rejeicao": data.get("motivo_rejeicao", ""), "detalhes": data.get("detalhes") or {}})
            decision_map[str(decision.id)] = decision
            decision_count += 1
    work_order_count = 0
    for data in json.loads(archive.read("work_orders.json")):
        machine = machines.get(data.get("machine_external_code"))
        decision = decision_map.get(str(data.get("decision_id")))
        if machine and decision:
            WorkOrder.objects.get_or_create(id=data["id"], defaults={"decision": decision, "machine": machine, "titulo": data["titulo"], "descricao": data["descricao"], "prioridade": data["prioridade"], "responsavel_usuario_id": actor.user_id, "prazo": data["prazo"], "status": data["status"], "checklist": data.get("checklist") or [], "pecas_sugeridas": data.get("pecas_sugeridas"), "criado_por_id": actor.user_id, "historico": data.get("historico") or [], "criado_em": data.get("criado_em"), "concluida_em": data.get("concluida_em")} )
            work_order_count += 1
    return {"manifest": manifest, "counts": {"telemetry": telemetry_count, "events": len(event_map), "decisions": decision_count, "work_orders": work_order_count}, "organization_id": str(organization.id)}


def issue_raw_token():
    return "fnt_" + secrets.token_urlsafe(32)

