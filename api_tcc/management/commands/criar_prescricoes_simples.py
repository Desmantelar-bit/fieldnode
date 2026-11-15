from django.core.management.base import BaseCommand
from api_tcc.models import Decision, Machine


class Command(BaseCommand):
    help = 'Cria prescrições de teste simples'

    def handle(self, *args, **options):
        # Buscar uma colheitadeira existente ou criar prescrições mockadas
        try:
            machine = Machine.objects.first()
            if not machine:
                self.stdout.write(self.style.WARNING('Nenhuma colheitadeira encontrada'))
                return
            decision = Decision.objects.create(
                machine=machine,
                texto='Análise de bancada para inspeção operacional.',
                acao_recomendada='Verificar os sinais recentes da máquina.',
                severidade='ATENCAO',
            )
            self.stdout.write(self.style.SUCCESS(f'Machine: {machine.external_code}'))
            self.stdout.write(self.style.SUCCESS(f'Decision criada: {decision.id}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro: {e}'))
