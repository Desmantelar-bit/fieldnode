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

        # Unidades de Medida
        um_bar, _ = UnidadedeMedida.objects.get_or_create(Nome='bar')
        um_psi, _ = UnidadedeMedida.objects.get_or_create(Nome='psi')
        um_cm, _ = UnidadedeMedida.objects.get_or_create(Nome='cm')
        um_mm, _ = UnidadedeMedida.objects.get_or_create(Nome='mm')
        um_c, _ = UnidadedeMedida.objects.get_or_create(Nome='°C')
        um_pct, _ = UnidadedeMedida.objects.get_or_create(Nome='%')
        um_kmh, _ = UnidadedeMedida.objects.get_or_create(Nome='km/h')
        um_h, _ = UnidadedeMedida.objects.get_or_create(Nome='h')
        um_litros, _ = UnidadedeMedida.objects.get_or_create(Nome='litros')

        # Marcas
        marca_jd, _ = Marca.objects.get_or_create(Nome='John Deere')
        marca_case, _ = Marca.objects.get_or_create(Nome='Case IH')
        marca_massey, _ = Marca.objects.get_or_create(Nome='Massey Ferguson')

        # Modelos
        modelo_s770, _ = Modelo.objects.get_or_create(Nome='S770', Marca=marca_jd)
        modelo_7240, _ = Modelo.objects.get_or_create(Nome='7240', Marca=marca_case)
        modelo_mf34, _ = Modelo.objects.get_or_create(Nome='MF 34', Marca=marca_massey)
        modelo_x9, _ = Modelo.objects.get_or_create(Nome='X9 1000', Marca=marca_jd)

        # Combustíveis
        comb_diesel, _ = Combustivel.objects.get_or_create(Tipo='Diesel', Porcentagem=75.0)
        comb_etanol, _ = Combustivel.objects.get_or_create(Tipo='Etanol', Porcentagem=50.0)
        comb_biodiesel, _ = Combustivel.objects.get_or_create(Tipo='Biodiesel', Porcentagem=100.0)

        # Operários
        op_joao, _ = Operario.objects.get_or_create(Nome='João Silva', TempodeServico=5, Nobanco=True)
        op_maria, _ = Operario.objects.get_or_create(Nome='Maria Oliveira', TempodeServico=8, Nobanco=True)
        op_pedro, _ = Operario.objects.get_or_create(Nome='Pedro Souza', TempodeServico=2, Nobanco=False)

        # Pressão dos Pneus
        pp1, _ = PressaoPneus.objects.get_or_create(Pressao=2.5, UnidadedeMedida=um_bar)
        pp2, _ = PressaoPneus.objects.get_or_create(Pressao=32.0, UnidadedeMedida=um_psi)
        pp3, _ = PressaoPneus.objects.get_or_create(Pressao=2.8, UnidadedeMedida=um_bar)

        # Altura do Corte
        ac1, _ = AlturadoCorte.objects.get_or_create(Altura=15.0, UnidadedeMedida=um_cm)
        ac2, _ = AlturadoCorte.objects.get_or_create(Altura=200.0, UnidadedeMedida=um_mm)
        ac3, _ = AlturadoCorte.objects.get_or_create(Altura=10.0, UnidadedeMedida=um_cm)

        # Pressão do Corte
        pc1, _ = PressaodoCorte.objects.get_or_create(Pressao=1.2, UnidadedeMedida=um_bar)
        pc2, _ = PressaodoCorte.objects.get_or_create(Pressao=1.5, UnidadedeMedida=um_bar)
        pc3, _ = PressaodoCorte.objects.get_or_create(Pressao=0.9, UnidadedeMedida=um_bar)

        # Temperatura e Umidade do Ambiente
        tua1, _ = TempUmi_Ambiente.objects.get_or_create(Temperatura=28.5, Umidade=65.0)
        tua2, _ = TempUmi_Ambiente.objects.get_or_create(Temperatura=22.0, Umidade=45.0)
        tua3, _ = TempUmi_Ambiente.objects.get_or_create(Temperatura=35.0, Umidade=80.0)

        # Transbordos
        Transbordo.objects.get_or_create(Modelo=modelo_s770, Capacidade=12000.0)
        Transbordo.objects.get_or_create(Modelo=modelo_7240, Capacidade=10500.0)
        Transbordo.objects.get_or_create(Modelo=modelo_x9, Capacidade=16000.0)

        # Status de Operação
        so1, _ = StatusdeOperacao.objects.get_or_create(Em_Operacao=True, Tempo_de_Operacao=8.5)
        so2, _ = StatusdeOperacao.objects.get_or_create(Em_Operacao=False, Tempo_de_Operacao=0.0)
        so3, _ = StatusdeOperacao.objects.get_or_create(Em_Operacao=True, Tempo_de_Operacao=5.0)

        # Estado de Movimento
        em1, _ = EstadodeMovimento.objects.get_or_create(Em_Movimento=True, Velocidade=12.5)
        em2, _ = EstadodeMovimento.objects.get_or_create(Em_Movimento=False, Velocidade=0.0)
        em3, _ = EstadodeMovimento.objects.get_or_create(Em_Movimento=True, Velocidade=8.0)

        # Temperatura da Máquina
        tm1, _ = TemperaturaMaquina.objects.get_or_create(Temperatura=85.0, Maquina=modelo_s770)
        tm2, _ = TemperaturaMaquina.objects.get_or_create(Temperatura=92.0, Maquina=modelo_7240)
        tm3, _ = TemperaturaMaquina.objects.get_or_create(Temperatura=78.0, Maquina=modelo_mf34)

        # Colheitadeiras
        Colheitadeira.objects.get_or_create(
            Modelo=modelo_s770, Combustivel=comb_diesel, PressaoPneus=pp1,
            AlturadoCorte=ac1, PressaodoCorte=pc1, TempUmi_Ambiente=tua1,
            TemperaturaMaquina=tm1, Operario=op_joao, StatusdeOperacao=so1,
            EstadodeMovimento=em1
        )
        Colheitadeira.objects.get_or_create(
            Modelo=modelo_7240, Combustivel=comb_etanol, PressaoPneus=pp2,
            AlturadoCorte=ac2, PressaodoCorte=pc2, TempUmi_Ambiente=tua2,
            TemperaturaMaquina=tm2, Operario=op_maria, StatusdeOperacao=so3,
            EstadodeMovimento=em3
        )
        Colheitadeira.objects.get_or_create(
            Modelo=modelo_mf34, Combustivel=comb_biodiesel, PressaoPneus=pp3,
            AlturadoCorte=ac3, PressaodoCorte=pc3, TempUmi_Ambiente=tua3,
            TemperaturaMaquina=tm3, Operario=op_pedro, StatusdeOperacao=so2,
            EstadodeMovimento=em2
        )

        # Leituras de Telemetria
        for i in range(20):
            LeituraTelemetria.objects.create(
                maquina_id=f'MAQ-{random.randint(100,999)}',
                temperatura=round(random.uniform(60.0, 120.0), 1),
                vibracao=round(random.uniform(0.1, 5.0), 2),
                rpm=random.randint(800, 2500),
                timestamp=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS('Banco de dados populado com sucesso!'))

