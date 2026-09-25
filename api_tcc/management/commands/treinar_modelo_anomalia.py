import numpy as np
from datetime import datetime
from django.core.management.base import BaseCommand
from api_tcc.models import LeituraTelemetria
from api_tcc.ia.model_registry import registry
from sklearn.ensemble import IsolationForest

FEATURES = ('temperatura', 'vibracao', 'rpm')
MINIMUM_TRAINING_READINGS = 100

class Command(BaseCommand):
    help = 'Treina e persiste o modelo de anomalias para uma máquina ou todas.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--machine',
            type=str,
            help='External code da máquina. Use "all" para treinar todas.'
        )

    def handle(self, *args, **options):
        machine_arg = options.get('machine')

        
        if not machine_arg:
            self.stdout.write(self.style.ERROR('O argumento --machine é obrigatório.'))
            return

        if machine_arg.lower() == 'all':
            machines = LeituraTelemetria.objects.values_list('machine__external_code', flat=True).distinct()
            for m_code in machines:
                self.train_single_machine(m_code)
        else:
            self.train_single_machine(machine_arg)

    def train_single_machine(self, machine_code: str):
        self.stdout.write(f'Treinando modelo para: {machine_code}...')
        rows = LeituraTelemetria.objects.filter(
            machine__external_code=machine_code,
        ).values(*FEATURES)

        data = []
        for row in rows:
            data.append([float(row[f]) if row[f] is not None else 0.0 for f in FEATURES])

        if len(data) < MINIMUM_TRAINING_READINGS:
            self.stdout.write(self.style.WARNING(f'Amostras insuficientes para {machine_code} ({len(data)}). Pulando.'))
            return

        X = np.asarray(data, dtype=float)
        mean = X.mean(axis=0)
        std = np.where(X.std(axis=0) > 1e-9, X.std(axis=0), 1.0)
        X_scaled = (X - mean) / std

        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(X_scaled)

        metadata = {
            'treinado_em': datetime.now().isoformat(),
            'contamination': 0.05,
            'n_amostras': len(data),
            'versao': '1.0',
            'scale_mean': mean.tolist(),
            'scale_std': std.tolist()
        }

        path = registry.save_model(machine_code, model, metadata)
        self.stdout.write(self.style.SUCCESS(f'Modelo salvo em {path}'))
