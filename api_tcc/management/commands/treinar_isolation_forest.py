import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand

from api_tcc.ia.deteccao_multivariada import MODELO_PATH, treinar_modelo


def gerar_cenario_normal(n_leituras: int = 1000) -> pd.DataFrame:
    """Gera a faixa operacional normal usada pelos cenários de bancada."""
    gerador = np.random.default_rng(42)
    return pd.DataFrame(
        {
            'temperatura': gerador.uniform(60.0, 80.0, n_leituras),
            'vibracao': gerador.uniform(0.2, 2.0, n_leituras),
            'rpm': gerador.uniform(1400.0, 1900.0, n_leituras),
        }
    )


class Command(BaseCommand):
    help = 'Treina offline o Isolation Forest com o cenário normal de bancada.'

    def add_arguments(self, parser):
        parser.add_argument('--leituras', type=int, default=1000)

    def handle(self, *args, **options):
        n_leituras = options['leituras']
        if n_leituras < 100:
            raise ValueError('--leituras deve ser no mínimo 100.')

        treinar_modelo(gerar_cenario_normal(n_leituras))
        self.stdout.write(self.style.SUCCESS(f'Modelo salvo em {MODELO_PATH}'))
