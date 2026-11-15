from django.core.management.base import BaseCommand

from api_tcc.models import Decision, Machine


class Command(BaseCommand):
    help = "Cria uma Decision de teste pelo caminho consolidado."

    def handle(self, *args, **options):
        machine = Machine.objects.first()
        if not machine:
            self.stdout.write(self.style.WARNING("Nenhuma Machine encontrada"))
            return
        decision = Decision.objects.create(
            machine=machine,
            texto="Temperatura elevada observada em dados de teste.",
            acao_recomendada="Verificar o sistema de arrefecimento.",
            severidade="ATENCAO",
        )
        self.stdout.write(self.style.SUCCESS(f"Decision criada: {decision.id}"))
