import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from api_tcc.models import Front, Machine
from api_tcc.services.operation_graph import criar_machine_link


class Command(BaseCommand):
    help = "Importa vínculos operacionais de um CSV sem persistência parcial."

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=Path)
        parser.add_argument("--organization", required=True, help="UUID da organização")

    def handle(self, *args, **options):
        path = options["arquivo"]
        try:
            rows = list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))
        except (OSError, UnicodeDecodeError) as exc:
            raise CommandError(f"não foi possível ler o CSV: {exc}") from exc
        required = {"origem", "destino", "tipo", "front", "de", "ate"}
        if not rows or set(rows[0].keys() or ()) != required:
            raise CommandError("cabeçalho deve ser origem,destino,tipo,front,de,ate")
        machines = {m.external_code: m for m in Machine.objects.filter(organization_id=options["organization"], ativo=True)}
        prepared, errors = [], []
        for line, row in enumerate(rows, start=2):
            origem = machines.get((row.get("origem") or "").strip().upper())
            destino = machines.get((row.get("destino") or "").strip().upper())
            start = parse_datetime((row.get("de") or "").strip())
            end = parse_datetime((row.get("ate") or "").strip()) if (row.get("ate") or "").strip() else None
            if start is not None and timezone.is_naive(start):
                start = timezone.make_aware(start)
            if end is not None and timezone.is_naive(end):
                end = timezone.make_aware(end)
            front_token = (row.get("front") or "").strip()
            front = Front.objects.filter(organization_id=options["organization"], ativo=True).filter(pk=front_token).first() or Front.objects.filter(organization_id=options["organization"], ativo=True, codigo=front_token).first() if front_token else None
            if not origem or not destino or not start or (front_token and front is None):
                errors.append((line, "máquina ou data inválida"))
            else:
                prepared.append((line, origem, destino, row.get("tipo"), start, end, front))
        if errors:
            self._report(errors)
            raise CommandError(f"{len(errors)} linha(s) rejeitada(s); nada foi gravado")
        try:
            with transaction.atomic():
                for line, origem, destino, tipo, start, end, front in prepared:
                    criar_machine_link(origem=origem, destino=destino, tipo=tipo, valido_de=start, valido_ate=end, front=front, organization=origem.organization)
        except (ValidationError, ValueError) as exc:
            self._report([(line, str(exc))])
            raise CommandError("importação abortada; nada foi gravado") from exc
        self.stdout.write(self.style.SUCCESS(f"{len(prepared)} vínculo(s) importado(s); 0 rejeitado(s)"))

    def _report(self, errors):
        for line, error in errors:
            self.stdout.write(f"linha {line}: rejeitada: {error}")
