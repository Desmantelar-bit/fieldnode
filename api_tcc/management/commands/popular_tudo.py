from django.core.management.base import BaseCommand
from api_tcc.models import (
    UnidadedeMedida, Marca, Modelo, Combustivel, PressaoPneus,
    AlturadoCorte, PressaodoCorte, TempUmi_Ambiente, TemperaturaMaquina,
    Transbordo, StatusdeOperacao, EstadodeMovimento, Operario, Colheitadeira,
    LeituraTelemetria
)
import random


class Command(BaseCommand):
    help = 'Popula banco de dados com valores realistas para apresentação'

    def handle(self, *args, **options):
        self.stdout.write('[INFO] Populando banco de dados...')

        unidade, _ = UnidadedeMedida.objects.get_or_create(nome='bar')
        marca_case, _ = Marca.objects.get_or_create(nome='CASE')
        modelo_tc5000, _ = Modelo.objects.get_or_create(nome='TC5000', marca=marca_case)
        marca_new_holland, _ = Marca.objects.get_or_create(nome='New Holland')
        modelo_cr9090, _ = Modelo.objects.get_or_create(nome='CR 9090', marca=marca_new_holland)
        combustivel_diesel, _ = Combustivel.objects.get_or_create(tipo='Diesel S10', porcentagem=75.0)

        pressao_pneus, _ = PressaoPneus.objects.get_or_create(pressao=28.5, unidade_de_medida=unidade)
        altura_corte, _ = AlturadoCorte.objects.get_or_create(altura=6.5, unidade_de_medida=unidade)
        pressao_corte, _ = PressaodoCorte.objects.get_or_create(pressao=120.0, unidade_de_medida=unidade)
        temp_ambiente, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=32.0, umidade=65.0)
        temp_maquina, _ = TemperaturaMaquina.objects.get_or_create(temperatura=82.0, maquina=modelo_tc5000)
        transbordo, _ = Transbordo.objects.get_or_create(modelo=modelo_tc5000, capacidade=3500.0)

        status_ativos = []
        for i in range(6):
            ativo = i < 4
            status_ativos.append(StatusdeOperacao.objects.get_or_create(
                em_operacao=ativo,
                tempo_de_operacao=round(random.uniform(120, 1800), 1) if ativo else round(random.uniform(0, 120), 1),
            )[0])

        movimentos = []
        for i in range(6):
            mov = i < 3
            movimentos.append(EstadodeMovimento.objects.get_or_create(
                em_movimento=mov,
                velocidade=round(random.uniform(4.5, 8.2), 1) if mov else 0.0,
            )[0])

        operarios = []
        for nome in ['Carlos Silva', 'Ana Santos', 'Bruno Costa', 'Mariana Oliveira', 'João Pereira', 'Patricia Lima']:
            op, _ = Operario.objects.get_or_create(
                nome=nome,
                tempo_de_servico=random.randint(1, 15),
                no_banco=True,
            )
            operarios.append(op)

        operarios_mapeados = [operarios[0], operarios[1], operarios[2]]

        for i in range(6):
            maquina_id = f'COLH-{i+1:02d}'
            modelo = modelo_tc5000 if i % 2 == 0 else modelo_cr9090
            operario = operarios_mapeados[i % len(operarios_mapeados)]
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

        # Cria telemetrias falsas para os gráficos
        from datetime import datetime, timedelta
        from django.utils.timezone import make_aware

        base = make_aware(datetime.now())
        leituras_criadas = 0
        for i in range(6):
            maquina_id = f'COLH-{i+1:02d}'
            for j in range(30):
                ts = base - timedelta(minutes=j*10)
                temp = round(random.uniform(68, 96), 1)
                vib = round(random.uniform(0.2, 0.9), 2)
                rpm = random.randint(1400, 2200)

                leitura, created = LeituraTelemetria.objects.get_or_create(
                    maquina_id=maquina_id,
                    timestamp=ts,
                    defaults={
                        'temperatura': temp,
                        'vibracao': vib,
                        'rpm': rpm,
                    },
                )
                if created:
                    leituras_criadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'[OK] Concluído: 6 colheitadeiras e {leituras_criadas} leituras criadas.'
        ))
