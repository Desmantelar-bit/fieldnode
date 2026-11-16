import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from api_tcc.models import Decision, Machine
from api_tcc.services.labeled_dataset import RULE_VERSION, eligible_windows, materialize_decision


HEADER = [
    "example_id", "machine", "decision_id", "window_start", "window_end", "rule_version",
    "feature_temperatura", "feature_vibracao", "feature_rpm", "feature_evidence_quality",
    "feature_reevaluation_before_pct", "feature_reevaluation_after_pct",
    "feature_followup_event_type", "feature_followup_severity",
    "label", "label_category", "label_source", "justification", "eligible",
]


class Command(BaseCommand):
    help = "Materializa e exporta janelas de decisões com desfecho elegível."

    def add_arguments(self, parser):
        parser.add_argument("--output", type=Path, required=True)
        parser.add_argument("--organization", type=int)
        parser.add_argument("--machine")
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, *args, **options):
        output = options["output"]
        if output.exists() and not options["overwrite"]:
            raise CommandError(f"arquivo já existe: {output}; use --overwrite explicitamente")
        machines = Machine.objects.all()
        if options["machine"]:
            machines = machines.filter(external_code=options["machine"].strip().upper())
            if not machines.exists():
                raise CommandError("machine não encontrada")
        if options["organization"]:
            machines = machines.filter(organization_id=options["organization"])

        found = eligible = 0
        for decision in Decision.objects.filter(machine__in=machines).select_related(
            "machine", "machine__organization", "event", "event__leitura_origem"
        ).order_by("machine__external_code", "criado_em", "id").iterator():
            found += 1
            if materialize_decision(decision) is not None:
                eligible += 1

        queryset = eligible_windows(organization_id=options["organization"])
        if options["machine"]:
            queryset = queryset.filter(machine__external_code=options["machine"].strip().upper())
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=HEADER, delimiter=";", extrasaction="ignore")
            writer.writeheader()
            for item in queryset:
                features = item.features or {}
                writer.writerow({
                    "example_id": str(item.id),
                    "machine": item.machine.external_code,
                    "decision_id": str(item.decision_id),
                    "window_start": item.janela_inicio.isoformat(),
                    "window_end": item.janela_fim.isoformat(),
                    "rule_version": item.regra_versao or RULE_VERSION,
                    "feature_temperatura": features.get("temperatura"),
                    "feature_vibracao": features.get("vibracao"),
                    "feature_rpm": features.get("rpm"),
                    "feature_evidence_quality": features.get("evidence_quality"),
                    "feature_reevaluation_before_pct": features.get("reevaluation_before_pct"),
                    "feature_reevaluation_after_pct": features.get("reevaluation_after_pct"),
                    "feature_followup_event_type": features.get("followup_event_type"),
                    "feature_followup_severity": features.get("followup_severity"),
                    "label": item.label,
                    "label_category": item.categoria,
                    "label_source": item.fonte_rotulo,
                    "justification": item.justificativa,
                    "eligible": str(item.elegivel_exportacao).lower(),
                })
        self.stdout.write(self.style.SUCCESS(
            f"decisões encontradas={found}; elegíveis materializadas={eligible}; exportadas={queryset.count()}; arquivo={output}"
        ))
