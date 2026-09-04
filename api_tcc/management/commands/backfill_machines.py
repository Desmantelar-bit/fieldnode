"""
Management command: backfill_machines
=====================================
Varre todos os ``maquina_id`` distintos em ``LeituraTelemetria`` e cria uma
entrada ``Machine`` para cada código ainda não mapeado, normalizando a string
com ``.strip().upper()`` antes de gravar.

É **idempotente**: rodar N vezes não produz duplicatas porque usa
``get_or_create(external_code=codigo_normalizado)``.

Uso
---
    python manage.py backfill_machines

Saída (stdout)
--------------
    Backfill iniciado em 2026-09-04 10:20:00
    ----------------------------------------
    Total de IDs lidos  : 5
    Machines criadas    : 3
    Já existentes       : 2
    Ignorados (vazios)  : 0
    ----------------------------------------
    Backfill concluído com sucesso.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from api_tcc.models import LeituraTelemetria, Machine


class Command(BaseCommand):
    help = (
        "Migra maquina_id distintos de LeituraTelemetria para a tabela Machine "
        "(idempotente — execuções repetidas não criam duplicatas)."
    )

    def handle(self, *args, **options):
        agora = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

        self.stdout.write(f"Backfill iniciado em {agora}")
        self.stdout.write("-" * 40)

        # Coleta todos os maquina_id distintos do histórico de telemetria
        raw_ids = (
            LeituraTelemetria.objects
            .values_list("maquina_id", flat=True)
            .distinct()
        )

        total = criados = existentes = ignorados = 0

        for raw in raw_ids:
            total += 1

            # Ignora entradas nulas ou compostas apenas de espaços
            if not raw or not raw.strip():
                ignorados += 1
                self.stdout.write(
                    self.style.WARNING(f"  [IGNORADO] valor vazio/nulo: {raw!r}")
                )
                continue

            # Normalização: remove espaços laterais e padroniza para maiúsculas
            codigo = raw.strip().upper()

            _, created = Machine.objects.get_or_create(external_code=codigo)

            if created:
                criados += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  [CRIADO]   {codigo!r}")
                )
            else:
                existentes += 1
                self.stdout.write(f"  [EXISTENTE] {codigo!r}")

        self.stdout.write("-" * 40)
        self.stdout.write(f"Total de IDs lidos  : {total}")
        self.stdout.write(f"Machines criadas    : {criados}")
        self.stdout.write(f"Já existentes       : {existentes}")
        self.stdout.write(f"Ignorados (vazios)  : {ignorados}")
        self.stdout.write("-" * 40)

        if criados > 0 or existentes > 0:
            self.stdout.write(self.style.SUCCESS("Backfill concluído com sucesso."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Backfill concluído — nenhuma LeituraTelemetria encontrada no banco."
                )
            )
