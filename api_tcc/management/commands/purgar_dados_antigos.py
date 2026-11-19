"""Purga conservadora, tenant-scoped e auditável.

Ausência de política é bloqueio, não autorização. Decisões nunca são removidas
automaticamente por este comando; seus desfechos são exportáveis e preservados.
"""
import hashlib
import json
import uuid
from datetime import timedelta
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from api_tcc.models import (
    AuditLog, CanonicalTelemetry, Event, Incident, LeituraTelemetria,
    Organization, RetentionPurgeRun, TelemetryAggregate,
)


CATEGORIES = {
    "telemetria_bruta": (LeituraTelemetria, "recebido_em", "machine__organization"),
    "telemetria_canonica": (CanonicalTelemetry, "criado_em", "raw_telemetry__machine__organization"),
    "telemetria_agregada": (TelemetryAggregate, "recebido_em", "machine__organization"),
    "eventos": (Event, "criado_em", "machine__organization"),
    "incidentes": (Incident, "criado_em", "organization"),
    "gps": (LeituraTelemetria, "recebido_em", "machine__organization"),
}


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


class Command(BaseCommand):
    help = "Simula ou executa purga de dados vencidos por organização e em lotes."

    def add_arguments(self, parser):
        parser.add_argument("--organization", required=True, help="UUID da organização; nunca é autorização por si só.")
        parser.add_argument("--category", choices=sorted(CATEGORIES), action="append")
        parser.add_argument("--reference-at", help="ISO-8601; padrão: agora.")
        parser.add_argument("--batch-size", type=int, default=500)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--execute", action="store_true")
        parser.add_argument("--export-dir", type=Path, help="Diretório para exportação verificável antes da execução.")
        parser.add_argument("--executor", default="management-command")

    def handle(self, *args, **options):
        if options["dry_run"] == options["execute"]:
            raise CommandError("informe exatamente um de --dry-run ou --execute")
        if options["batch_size"] < 1 or options["batch_size"] > 10000:
            raise CommandError("--batch-size deve estar entre 1 e 10000")
        try:
            organization = Organization.objects.get(pk=options["organization"])
        except (Organization.DoesNotExist, ValueError):
            raise CommandError("organização não encontrada")
        policy = getattr(organization, "policy", None)
        retention = getattr(policy, "retention_policy", {}) if policy else {}
        if not isinstance(retention, dict) or not retention:
            raise CommandError("organização sem política de retenção aprovada; nenhuma exclusão foi feita")
        categories = options["category"] or sorted(retention)
        if isinstance(categories, str):
            categories = [categories]
        unknown = set(categories) - set(CATEGORIES)
        if unknown:
            raise CommandError(f"categorias sem purga implementada: {sorted(unknown)}")
        for category in categories:
            days = retention.get(category)
            if isinstance(days, bool) or not isinstance(days, int) or not 1 <= days <= 36500:
                raise CommandError(f"prazo inválido ou ausente para {category}")
        if options["reference_at"]:
            from django.utils.dateparse import parse_datetime
            reference_at = parse_datetime(options["reference_at"])
            if reference_at is None:
                raise CommandError("--reference-at inválido")
            if timezone.is_naive(reference_at):
                reference_at = timezone.make_aware(reference_at, timezone.get_current_timezone())
        else:
            reference_at = timezone.now()

        run = RetentionPurgeRun.objects.create(
            executor=options["executor"], organization_id_text=str(organization.pk),
            categories=categories, policy_version=getattr(policy, "retention_policy_version", ""),
            reference_at=reference_at,
        )
        totals = {"evaluated": 0, "deleted": 0, "preserved": 0}
        reasons = {}
        export_manifest = {}
        errors = []
        try:
            for category in categories:
                model, date_field, organization_field = CATEGORIES[category]
                cutoff = reference_at - timedelta(days=retention[category])
                queryset = model.objects.filter(**{f"{date_field}__lt": cutoff})
                queryset = queryset.filter(**{organization_field: organization})
                if category == "telemetria_bruta":
                    queryset = queryset.filter(~Q(agregada=True))
                if category == "gps":
                    queryset = queryset.filter(latitude__isnull=False, longitude__isnull=False)
                rows = list(queryset.order_by(date_field, "pk").values_list("pk", flat=True))
                totals["evaluated"] += len(rows)
                export_manifest[category] = self._export_candidates(
                    organization, category, rows, options["export_dir"], run.id
                )
                if options["dry_run"]:
                    continue
                for offset in range(0, len(rows), options["batch_size"]):
                    for pk in rows[offset:offset + options["batch_size"]]:
                        try:
                            deleted, _ = model.objects.filter(pk=pk).delete()
                            totals["deleted"] += deleted
                        except ProtectedError:
                            totals["preserved"] += 1
                            reasons[category] = reasons.get(category, 0) + 1
                        except Exception as exc:  # keep partial run auditable
                            errors.append(f"{category}:{pk}:{type(exc).__name__}")
            run.evaluated = totals["evaluated"]
            run.deleted = totals["deleted"]
            run.preserved = totals["preserved"]
            run.preservation_reasons = reasons
            run.export_manifest = export_manifest
            run.errors = errors
            run.result = "dry_run" if options["dry_run"] else ("failed" if errors else "completed")
            run.finished_at = timezone.now()
            run.save(update_fields=["evaluated", "deleted", "preserved", "preservation_reasons", "export_manifest", "errors", "result", "finished_at"])
            AuditLog.objects.create(
                action="retention.purge", result=run.result,
                metadata={"run_id": str(run.id), "organization_id": str(organization.pk), "categories": categories, "evaluated": totals["evaluated"], "deleted": totals["deleted"], "preserved": totals["preserved"]},
                object_type="api_tcc.retentionpurgerun", object_id=str(run.id),
            )
        except Exception as exc:
            run.result = "failed"
            run.errors = errors + [f"{type(exc).__name__}:{exc}"]
            run.finished_at = timezone.now()
            run.save(update_fields=["result", "errors", "finished_at"])
            raise
        self.stdout.write(json.dumps({"run_id": str(run.id), **totals, "preserved_reasons": reasons, "result": run.result}, ensure_ascii=False, sort_keys=True))

    def _export_candidates(self, organization, category, ids, export_dir, run_id):
        if not export_dir:
            return {"count": len(ids), "exported": False}
        export_dir.mkdir(parents=True, exist_ok=True)
        model = CATEGORIES[category][0]
        rows = list(model.objects.filter(pk__in=ids).values())
        payload = _canonical({"schema": "fieldnode-retention-export-v1", "organization": str(organization.pk), "category": category, "rows": rows})
        path = export_dir / f"{run_id}_{category}.json"
        path.write_text(payload + "\n", encoding="utf-8", newline="\n")
        return {"count": len(rows), "path": str(path), "sha256": hashlib.sha256(payload.encode()).hexdigest()}
