from django.core.management.base import BaseCommand, CommandError

from api_tcc.ia.model_registry import registry
from api_tcc.models import LeituraTelemetria, Machine
from api_tcc.services.anomaly_detection import MINIMUM_TRAINING_READINGS, train_model_for_machine


class Command(BaseCommand):
    help = "Treina e persiste o modelo de anomalias para uma máquina ou todas."

    def add_arguments(self, parser):
        parser.add_argument("--machine", required=True, type=str, help='Código externo da máquina. Use "all" para todas.')

    def handle(self, *args, **options):
        machine_arg = options["machine"].strip()
        if not machine_arg:
            raise CommandError("--machine não pode ser vazio.")
        if machine_arg.lower() == "all":
            codes = list(Machine.objects.filter(leituras__isnull=False).values_list("external_code", flat=True).distinct().order_by("external_code"))
            if not codes:
                self.stdout.write(self.style.WARNING("Nenhuma máquina com telemetria encontrada."))
                return
            for code in codes:
                count = LeituraTelemetria.objects.filter(machine__external_code=code).count()
                if count < MINIMUM_TRAINING_READINGS:
                    self.stdout.write(self.style.WARNING(f"Amostras insuficientes para {code}: {count}; pulando."))
                    continue
                self._train(code)
            return
        if not Machine.objects.filter(external_code=machine_arg).exists():
            raise CommandError(f"Máquina não encontrada: {machine_arg}")
        self._train(machine_arg)

    def _train(self, machine_code: str) -> None:
        count = LeituraTelemetria.objects.filter(machine__external_code=machine_code).count()
        if count < MINIMUM_TRAINING_READINGS:
            raise CommandError(f"Amostras insuficientes para {machine_code}: {count}; mínimo: {MINIMUM_TRAINING_READINGS}.")
        train_model_for_machine(machine_code)
        self.stdout.write(self.style.SUCCESS(f"Modelo salvo em {registry.get_model_path(machine_code)}"))
