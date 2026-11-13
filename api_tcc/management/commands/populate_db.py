from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api_tcc.models import (
    UnidadedeMedida, Marca, Modelo, Combustivel, Operario,
    PressaoPneus, AlturadoCorte, PressaodoCorte, TempUmi_Ambiente,
    Transbordo, StatusdeOperacao, EstadodeMovimento, TemperaturaMaquina,
    Colheitadeira, LeituraTelemetria
)
from django.utils import timezone
import random
import uuid


class Command(BaseCommand):
    help = 'Popula o banco de dados com registros de exemplo'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando dados de exemplo...')

        # Criar superusuario automatico
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superusuario criado: admin / admin123'))
        else:
            self.stdout.write('Superusuario admin ja existe.')

        # Unidades de Medida (campo: nome)
        um_bar, _ = UnidadedeMedida.objects.get_or_create(nome='bar')
        um_psi, _ = UnidadedeMedida.objects.get_or_create(nome='psi')
        um_cm, _ = UnidadedeMedida.objects.get_or_create(nome='cm')
        um_mm, _ = UnidadedeMedida.objects.get_or_create(nome='mm')
        um_c, _ = UnidadedeMedida.objects.get_or_create(nome='°C')
        um_pct, _ = UnidadedeMedida.objects.get_or_create(nome='%')
        um_kmh, _ = UnidadedeMedida.objects.get_or_create(nome='km/h')
        um_h, _ = UnidadedeMedida.objects.get_or_create(nome='h')
        um_litros, _ = UnidadedeMedida.objects.get_or_create(nome='litros')

        # Marcas (campo: nome)
        marca_jd, _ = Marca.objects.get_or_create(nome='John Deere')
        marca_case, _ = Marca.objects.get_or_create(nome='Case IH')
        marca_massey, _ = Marca.objects.get_or_create(nome='Massey Ferguson')

        # Modelos (campos: nome, marca)
        modelo_s770, _ = Modelo.objects.get_or_create(nome='S770', marca=marca_jd)
        modelo_7240, _ = Modelo.objects.get_or_create(nome='7240', marca=marca_case)
        modelo_mf34, _ = Modelo.objects.get_or_create(nome='MF 34', marca=marca_massey)
        modelo_x9, _ = Modelo.objects.get_or_create(nome='X9 1000', marca=marca_jd)

        # Combustíveis (campos: tipo, porcentagem)
        comb_diesel, _ = Combustivel.objects.get_or_create(tipo='Diesel', porcentagem=75.0)
        comb_etanol, _ = Combustivel.objects.get_or_create(tipo='Etanol', porcentagem=50.0)
        comb_biodiesel, _ = Combustivel.objects.get_or_create(tipo='Biodiesel', porcentagem=100.0)

        # Operários (campos: nome, tempo_de_servico, no_banco)
        op_joao, _ = Operario.objects.get_or_create(nome='João Silva', tempo_de_servico=5, no_banco=True)
        op_maria, _ = Operario.objects.get_or_create(nome='Maria Oliveira', tempo_de_servico=8, no_banco=True)
        op_pedro, _ = Operario.objects.get_or_create(nome='Pedro Souza', tempo_de_servico=2, no_banco=False)

        # Pressão dos Pneus (campos: pressao, unidade_de_medida)
        pp1, _ = PressaoPneus.objects.get_or_create(pressao=2.5, unidade_de_medida=um_bar)
        pp2, _ = PressaoPneus.objects.get_or_create(pressao=32.0, unidade_de_medida=um_psi)
        pp3, _ = PressaoPneus.objects.get_or_create(pressao=2.8, unidade_de_medida=um_bar)

        # Altura do Corte (campos: altura, unidade_de_medida)
        ac1, _ = AlturadoCorte.objects.get_or_create(altura=15.0, unidade_de_medida=um_cm)
        ac2, _ = AlturadoCorte.objects.get_or_create(altura=200.0, unidade_de_medida=um_mm)
        ac3, _ = AlturadoCorte.objects.get_or_create(altura=10.0, unidade_de_medida=um_cm)

        # Pressão do Corte (campos: pressao, unidade_de_medida)
        pc1, _ = PressaodoCorte.objects.get_or_create(pressao=1.2, unidade_de_medida=um_bar)
        pc2, _ = PressaodoCorte.objects.get_or_create(pressao=1.5, unidade_de_medida=um_bar)
        pc3, _ = PressaodoCorte.objects.get_or_create(pressao=0.9, unidade_de_medida=um_bar)

        # Temperatura e Umidade do Ambiente (campos: temperatura, umidade)
        tua1, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=28.5, umidade=65.0)
        tua2, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=22.0, umidade=45.0)
        tua3, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=35.0, umidade=80.0)

        # Transbordos (campos: modelo, capacidade)
        Transbordo.objects.get_or_create(modelo=modelo_s770, capacidade=12000.0)
        Transbordo.objects.get_or_create(modelo=modelo_7240, capacidade=10500.0)
        Transbordo.objects.get_or_create(modelo=modelo_x9, capacidade=16000.0)

        # Status de Operação (campos: em_operacao, tempo_de_operacao)
        so1 = StatusdeOperacao.objects.filter(em_operacao=True, tempo_de_operacao=8.5).first() or \
              StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=8.5)
        so2 = StatusdeOperacao.objects.filter(em_operacao=False, tempo_de_operacao=0.0).first() or \
              StatusdeOperacao.objects.create(em_operacao=False, tempo_de_operacao=0.0)
        so3 = StatusdeOperacao.objects.filter(em_operacao=True, tempo_de_operacao=5.0).first() or \
              StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=5.0)

        # Estado de Movimento (campos: em_movimento, velocidade)
        em1 = EstadodeMovimento.objects.filter(em_movimento=True, velocidade=12.5).first() or \
              EstadodeMovimento.objects.create(em_movimento=True, velocidade=12.5)
        em2 = EstadodeMovimento.objects.filter(em_movimento=False, velocidade=0.0).first() or \
              EstadodeMovimento.objects.create(em_movimento=False, velocidade=0.0)
        em3 = EstadodeMovimento.objects.filter(em_movimento=True, velocidade=8.0).first() or \
              EstadodeMovimento.objects.create(em_movimento=True, velocidade=8.0)

        # Temperatura da Máquina (campos: temperatura, maquina)
        tm1 = TemperaturaMaquina.objects.filter(temperatura=85.0, maquina=modelo_s770).first() or \
              TemperaturaMaquina.objects.create(temperatura=85.0, maquina=modelo_s770)
        tm2 = TemperaturaMaquina.objects.filter(temperatura=92.0, maquina=modelo_7240).first() or \
              TemperaturaMaquina.objects.create(temperatura=92.0, maquina=modelo_7240)
        tm3 = TemperaturaMaquina.objects.filter(temperatura=78.0, maquina=modelo_mf34).first() or \
              TemperaturaMaquina.objects.create(temperatura=78.0, maquina=modelo_mf34)

        # Colheitadeiras (campos snake_case)
        Colheitadeira.objects.get_or_create(
            modelo=modelo_s770, combustivel=comb_diesel, pressao_pneus=pp1,
            altura_do_corte=ac1, pressao_do_corte=pc1, temp_umi_ambiente=tua1,
            temperatura_maquina=tm1, operario=op_joao, status_de_operacao=so1,
            estado_de_movimento=em1
        )
        Colheitadeira.objects.get_or_create(
            modelo=modelo_7240, combustivel=comb_etanol, pressao_pneus=pp2,
            altura_do_corte=ac2, pressao_do_corte=pc2, temp_umi_ambiente=tua2,
            temperatura_maquina=tm2, operario=op_maria, status_de_operacao=so3,
            estado_de_movimento=em3
        )
        Colheitadeira.objects.get_or_create(
            modelo=modelo_mf34, combustivel=comb_biodiesel, pressao_pneus=pp3,
            altura_do_corte=ac3, pressao_do_corte=pc3, temp_umi_ambiente=tua3,
            temperatura_maquina=tm3, operario=op_pedro, status_de_operacao=so2,
            estado_de_movimento=em2
        )

        # Leituras de Telemetria (20 registros simulados, idempotentes via message_id único)
        maquinas = list(Colheitadeira.objects.all())
        created_count = 0
        for i in range(20):
            device_id = f'MAQ-{random.randint(100, 999)}'
            message_id = str(uuid.uuid4())
            _, created = LeituraTelemetria.objects.get_or_create(
                device_id=device_id,
                message_id=message_id,
                defaults=dict(
                    maquina_id=device_id,
                    temperatura=round(random.uniform(60.0, 120.0), 1),
                    vibracao=round(random.uniform(0.1, 5.0), 2),
                    rpm=random.randint(800, 2500),
                    timestamp=timezone.now(),
                    data_origin='simulado',
                )
            )
            if created:
                created_count += 1
        self.stdout.write(f'  Leituras de telemetria criadas: {created_count}')

        self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso!'))
