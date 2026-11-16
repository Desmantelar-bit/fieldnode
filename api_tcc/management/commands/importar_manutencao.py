import csv
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from api_tcc.models import MaintenanceRecord, Machine


REQUIRED = {"machine", "registro_id", "data", "tipo", "horas_motor", "pecas", "observacao"}


class Command(BaseCommand):
    help = "Importa histórico de manutenção em CSV UTF-8 separado por ponto e vírgula."

    def add_arguments(self, parser):
        parser.add_argument("input", type=Path)
        parser.add_argument("--organization", type=int)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        path = options["input"]
        if not path.is_file():
            raise CommandError(f"CSV não encontrado: {path}")
        counts = {"lidas": 0, "importados": 0, "duplicados": 0, "rejeitados": 0}
        errors = []
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            headers = set(reader.fieldnames or [])
            missing = REQUIRED - headers
            if missing:
                raise CommandError(f"cabeçalho ausente: {', '.join(sorted(missing))}")
            for number, row in enumerate(reader, start=2):
                counts["lidas"] += 1
                try:
                    machine_code = (row.get("machine") or "").strip().upper()
                    machine = Machine.objects.get(external_code=machine_code)
                    if options["organization"] and machine.organization_id != options["organization"]:
                        raise ValueError("machine não pertence à organização informada")
                    if not row["registro_id"].strip():
                        raise ValueError("registro_id obrigatório para reexecução idempotente")
                    parsed_date = date.fromisoformat(row["data"].strip())
                    hours = None if not row["horas_motor"].strip() else Decimal(row["horas_motor"].strip())
                    if hours is not None and hours < 0:
                        raise ValueError("horas_motor não pode ser negativo")
                    parts = json.loads(row["pecas"]) if row["pecas"].strip() else []
                    if not isinstance(parts, (list, dict)):
                        raise ValueError("pecas deve ser JSON de lista ou objeto")
                    if MaintenanceRecord.objects.filter(machine=machine, registro_id=row["registro_id"].strip()).exists():
                        counts["duplicados"] += 1
                        continue
                    if not options["dry_run"]:
                        with transaction.atomic():
                            MaintenanceRecord.objects.create(
                                machine=machine, registro_id=row["registro_id"].strip(),
                                data=parsed_date, tipo=row["tipo"].strip(),
                                horas_motor=hours, pecas=parts,
                                observacao=row["observacao"].strip(), origem="csv",
                            )
                    counts["importados"] += 1
                except (Machine.DoesNotExist, ValueError, InvalidOperation, json.JSONDecodeError, IntegrityError) as exc:
                    counts["rejeitados"] += 1
                    reason = "machine inexistente" if isinstance(exc, Machine.DoesNotExist) else str(exc)
                    errors.append((number, reason))
        self.stdout.write(f"linhas lidas={counts['lidas']}; importados={counts['importados']}; duplicados={counts['duplicados']}; rejeitados={counts['rejeitados']}; dry_run={options['dry_run']}")
        for number, reason in errors:
            self.stdout.write(self.style.WARNING(f"linha {number}: rejeitada: {reason}"))
