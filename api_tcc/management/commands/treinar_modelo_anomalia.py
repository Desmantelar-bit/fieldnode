from django.core.management.base import BaseCommand, CommandError

from api_tcc.ia.model_registry import registry
from api_tcc.models import Machine
from api_tcc.services.anomaly_detection import pode_treinar, train_model_for_machine


class Command(BaseCommand):
    help = "Treina e persiste o modelo de anomalias somente quando a política permite."

    def add_arguments(self, parser):
        parser.add_argument("--machine", required=True, type=str, help='Código externo da máquina. Use "all" para todas.')

    def handle(self, *args, **options):
        machine_arg = options["machine"].strip()
        if not machine_arg:
            raise CommandError("--machine não pode ser vazio.")
        machines = Machine.objects.filter(leituras__isnull=False).distinct().order_by("external_code") if machine_arg.lower() == "all" else Machine.objects.filter(external_code=machine_arg)
        if not machines.exists():
            raise CommandError(f"Máquina não encontrada: {machine_arg}")
        for machine in machines:
            eligible, reasons = pode_treinar(machine)
            if not eligible:
                message = f"Treino recusado para {machine.external_code}: {', '.join(reasons)}"
                if machine_arg.lower() == "all":
                    self.stdout.write(self.style.WARNING(message))
                    continue
                raise CommandError(message)
            train_model_for_machine(machine.external_code)
            self.stdout.write(self.style.SUCCESS(f"Modelo salvo em {registry.get_model_path(machine.external_code, regime='trabalhando')}"))
