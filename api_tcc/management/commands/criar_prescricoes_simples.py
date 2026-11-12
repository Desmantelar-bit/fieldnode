from django.core.management.base import BaseCommand
from api_tcc.models import Prescricao, Colheitadeira


class Command(BaseCommand):
    help = 'Cria prescrições de teste simples'

    def handle(self, *args, **options):
        # Buscar uma colheitadeira existente ou criar prescrições mockadas
        try:
            colheitadeira = Colheitadeira.objects.first()
            if not colheitadeira:
                self.stdout.write(self.style.WARNING('Nenhuma colheitadeira encontrada'))
                return
            
            # Limpar prescrições antigas
            Prescricao.objects.filter(colheitadeira=colheitadeira).delete()

            # Criar prescrições de teste
            p1 = Prescricao.objects.create(
                colheitadeira=colheitadeira,
                titulo='Verificar Sistema de Arrefecimento',
                descricao='Temperatura média elevada (98.2°C) detectada nas últimas leituras. Recomenda-se verificar radiador, nível de fluido de arrefecimento e funcionamento da ventoinha.',
                status='pendente'
            )

            p2 = Prescricao.objects.create(
                colheitadeira=colheitadeira,
                titulo='Manutenção Preventiva do Motor', 
                descricao='Análise dos dados indica necessidade de verificação dos filtros de ar e óleo. Temperatura operacional ligeiramente acima do normal.',
                status='pendente'
            )

            self.stdout.write(self.style.SUCCESS(f'Colheitadeira: {colheitadeira.maquina_id}'))
            self.stdout.write(self.style.SUCCESS(f'Prescrições criadas: {p1.id}, {p2.id}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro: {e}'))