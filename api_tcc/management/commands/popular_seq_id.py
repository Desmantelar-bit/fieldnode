"""
Comando Django para popular seq_id em registros existentes.

Uso:
    python manage.py popular_seq_id
    python manage.py popular_seq_id --force  # Repopula todos
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from api_tcc.models import LeituraTelemetria


class Command(BaseCommand):
    help = 'Popula seq_id em registros de telemetria que não possuem'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Repopula todos os seq_ids (use com cuidado)',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            self.stdout.write('[AVISO] Modo --force: repopulando TODOS os seq_ids')
            leituras = LeituraTelemetria.objects.all().order_by('recebido_em')
        else:
            leituras = LeituraTelemetria.objects.filter(
                seq_id__isnull=True
            ).order_by('recebido_em')
        
        total = leituras.count()
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('[OK] Todos os registros já possuem seq_id'))
            return
        
        self.stdout.write(f'[INFO] Encontrados {total} registros sem seq_id')
        self.stdout.write('[INFO] Populando...')
        
        # Usar transação para evitar race conditions
        with transaction.atomic():
            seq_atual = 1
            if not force:
                ultimo_com_seq = LeituraTelemetria.objects.filter(
                    seq_id__isnull=False
                ).order_by('-seq_id').first()
                if ultimo_com_seq:
                    seq_atual = ultimo_com_seq.seq_id + 1
            
            processados = 0
            for leitura in leituras.iterator(chunk_size=100):
                leitura.seq_id = seq_atual
                leitura.save(update_fields=['seq_id'])
                seq_atual += 1
                processados += 1
                
                if processados % 100 == 0:
                    self.stdout.write(f'  Processados {processados}/{total}...')
        
        self.stdout.write(self.style.SUCCESS(f'[OK] Concluído! {total} registros atualizados'))
