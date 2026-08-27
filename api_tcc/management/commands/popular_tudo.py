from django.core.management.base import BaseCommand
from api_tcc.models import (
    UnidadedeMedida, Marca, Modelo, Combustivel, PressaoPneus,
    AlturadoCorte, PressaodoCorte, TempUmi_Ambiente, TemperaturaMaquina,
    Transbordo, StatusdeOperacao, EstadodeMovimento, Operario, Colheitadeira,
    LeituraTelemetria
)
import random
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

# Coordenadas GPS reais em área agrícola (Goiás/DF)
GPS_BASE = [
    (-15.7939, -47.8828),
    (-15.7955, -47.8850),
    (-15.7980, -47.8885),
    (-15.8010, -47.8920),
    (-15.8035, -47.8895),
    (-15.8020, -47.8850),
    (-15.7990, -47.8815),
    (-15.7960, -47.8790),
    (-15.7940, -47.8810),
    (-15.7925, -47.8840),
]

NUM_MAQUINAS = 10
LEITURAS_POR_MAQUINA = 50


class Command(BaseCommand):
    help = 'Popula banco de dados com valores realistas para apresentação'

    def handle(self, *args, **options):
        self.stdout.write('[INFO] Populando banco de dados...')

        unidade, _ = UnidadedeMedida.objects.get_or_create(nome='bar')
        marca_case, _ = Marca.objects.get_or_create(nome='CASE')
        modelo_tc5000, _ = Modelo.objects.get_or_create(nome='TC5000', marca=marca_case)
        marca_new_holland, _ = Marca.objects.get_or_create(nome='New Holland')
        modelo_cr9090, _ = Modelo.objects.get_or_create(nome='CR 9090', marca=marca_new_holland)
        marca_john_deere, _ = Marca.objects.get_or_create(nome='John Deere')
        modelo_s780, _ = Modelo.objects.get_or_create(nome='S780', marca=marca_john_deere)
        combustivel_diesel, _ = Combustivel.objects.get_or_create(tipo='Diesel S10', porcentagem=75.0)

        pressao_pneus, _ = PressaoPneus.objects.get_or_create(pressao=28.5, unidade_de_medida=unidade)
        altura_corte, _ = AlturadoCorte.objects.get_or_create(altura=6.5, unidade_de_medida=unidade)
        pressao_corte, _ = PressaodoCorte.objects.get_or_create(pressao=120.0, unidade_de_medida=unidade)
        temp_ambiente, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=32.0, umidade=65.0)
        temp_maquina, _ = TemperaturaMaquina.objects.get_or_create(temperatura=82.0, maquina=modelo_tc5000)
        Transbordo.objects.get_or_create(modelo=modelo_tc5000, capacidade=3500.0)

        modelos = [modelo_tc5000, modelo_cr9090, modelo_s780]

        status_ativos = []
        for i in range(NUM_MAQUINAS):
            ativo = i < 7
            status_ativos.append(StatusdeOperacao.objects.get_or_create(
                em_operacao=ativo,
                tempo_de_operacao=round(random.uniform(120, 1800), 1) if ativo else round(random.uniform(0, 120), 1),
            )[0])

        movimentos = []
        for i in range(NUM_MAQUINAS):
            mov = i < 5
            movimentos.append(EstadodeMovimento.objects.get_or_create(
                em_movimento=mov,
                velocidade=round(random.uniform(4.5, 8.2), 1) if mov else 0.0,
            )[0])

        nomes_operarios = [
            'Carlos Silva', 'Ana Santos', 'Bruno Costa', 'Mariana Oliveira',
            'João Pereira', 'Patricia Lima', 'Ricardo Souza', 'Fernanda Alves',
        ]
        operarios = []
        for nome in nomes_operarios:
            op, _ = Operario.objects.get_or_create(
                nome=nome,
                defaults={'tempo_de_servico': random.randint(1, 15), 'no_banco': True},
            )
            operarios.append(op)

        for i in range(NUM_MAQUINAS):
            maquina_id = f'COLH-{i+1:02d}'
            modelo = modelos[i % len(modelos)]
            operario = operarios[i % len(operarios)]
            colheitadeira, created = Colheitadeira.objects.get_or_create(
                maquina_id=maquina_id,
                defaults={
                    'modelo': modelo,
                    'combustivel': combustivel_diesel,
                    'pressao_pneus': pressao_pneus,
                    'altura_do_corte': altura_corte,
                    'pressao_do_corte': pressao_corte,
                    'temp_umi_ambiente': temp_ambiente,
                    'temperatura_maquina': temp_maquina,
                    'operario': operario,
                    'status_de_operacao': status_ativos[i],
                    'estado_de_movimento': movimentos[i],
                },
            )
            if created:
                self.stdout.write(f'  [OK] Colheitadeira {maquina_id} criada')

        base = make_aware(datetime.now())
        leituras_criadas = 0
        for i in range(NUM_MAQUINAS):
            maquina_id = f'COLH-{i+1:02d}'
            lat_base, lng_base = GPS_BASE[i]
            for j in range(LEITURAS_POR_MAQUINA):
                ts = base - timedelta(minutes=j * 5)
                # Simula drift GPS realista (máquina se movendo)
                lat = round(lat_base + (random.random() - 0.5) * 0.002, 6)
                lng = round(lng_base + (random.random() - 0.5) * 0.002, 6)
                temp = round(random.uniform(65, 98), 1)
                vib = round(random.uniform(0.15, 0.95), 2)
                rpm = random.randint(1300, 2300)

                leitura, created = LeituraTelemetria.objects.get_or_create(
                    maquina_id=maquina_id,
                    timestamp=ts,
                    defaults={
                        'temperatura': temp,
                        'vibracao': vib,
                        'rpm': rpm,
                        'latitude': lat,
                        'longitude': lng,
                    },
                )
                if created:
                    leituras_criadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'[OK] Concluído: {NUM_MAQUINAS} colheitadeiras e {leituras_criadas} leituras criadas.'
        ))
