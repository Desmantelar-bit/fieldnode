import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from api_tcc.models import Machine, Organization
from api_tcc.services.passport import export_passport


class Command(BaseCommand):
    help = "Exporta um Data Passport v0.1 para uma organização autorizada pela operação administrativa."

    def add_arguments(self, parser):
        parser.add_argument("--organization", required=True, help="UUID da organização")
        parser.add_argument("--machine", help="UUID ou código externo da máquina")
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        organization = Organization.objects.filter(pk=options["organization"]).first()
        if not organization:
            raise CommandError("organização não encontrada")
        machine = None
        if options.get("machine"):
            machine = Machine.objects.filter(organization=organization).filter(pk=options["machine"]).first() or Machine.objects.filter(organization=organization, external_code=options["machine"].upper()).first()
            if not machine:
                raise CommandError("máquina não encontrada na organização")
        blob = export_passport(organization=organization, machine=machine)
        Path(options["output"]).write_bytes(blob)
        self.stdout.write(self.style.SUCCESS(f"Passport exportado: {options['output']} ({len(blob)} bytes)"))
