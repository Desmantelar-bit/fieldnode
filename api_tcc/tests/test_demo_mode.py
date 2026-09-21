from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from api_tcc import models


def _criar_colheitadeira(maquina_id: str) -> models.Colheitadeira:
    unidade = models.UnidadedeMedida.objects.create(nome=f"Unidade {maquina_id}")
    marca = models.Marca.objects.create(nome=f"Marca {maquina_id}")
    modelo = models.Modelo.objects.create(nome=f"Modelo {maquina_id}", marca=marca)
    combustivel = models.Combustivel.objects.create(tipo="Diesel", porcentagem=100.0)
    pressao_pneus = models.PressaoPneus.objects.create(
        pressao=2.5,
        unidade_de_medida=unidade,
    )
    altura_corte = models.AlturadoCorte.objects.create(
        altura=5.0,
        unidade_de_medida=unidade,
    )
    pressao_corte = models.PressaodoCorte.objects.create(
        pressao=30.0,
        unidade_de_medida=unidade,
    )
    temp_umi = models.TempUmi_Ambiente.objects.create(
        temperatura=25.0,
        umidade=60.0,
    )
    temp_maquina = models.TemperaturaMaquina.objects.create(
        temperatura=85.0,
        maquina=modelo,
    )
    operario = models.Operario.objects.create(
        nome=f"Operario {maquina_id}",
        tempo_de_servico=5,
        no_banco=True,
    )
    status_operacao = models.StatusdeOperacao.objects.create(
        em_operacao=True,
        tempo_de_operacao=8.0,
    )
    estado_movimento = models.EstadodeMovimento.objects.create(
        em_movimento=True,
        velocidade=6.5,
    )
    return models.Colheitadeira.objects.create(
        maquina_id=maquina_id,
        modelo=modelo,
        combustivel=combustivel,
        pressao_pneus=pressao_pneus,
        altura_do_corte=altura_corte,
        pressao_do_corte=pressao_corte,
        temp_umi_ambiente=temp_umi,
        temperatura_maquina=temp_maquina,
        operario=operario,
        status_de_operacao=status_operacao,
        estado_de_movimento=estado_movimento,
    )


class DemoModeTelemetriaTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("ultimas-leituras")

        self.machine_demo = models.Machine.objects.create(
            external_code="COLH-DEMO-01",
            is_demo=True,
        )
        self.machine_real = models.Machine.objects.create(
            external_code="COLH-REAL-01",
            is_demo=False,
        )
        _criar_colheitadeira(self.machine_demo.external_code)
        _criar_colheitadeira(self.machine_real.external_code)

        agora = timezone.now()
        models.LeituraTelemetria.objects.create(
            maquina_id=self.machine_demo.external_code,
            machine=self.machine_demo,
            device_id="COLH-DEMO-01",
            message_id="msg-demo-1",
            sequence_number=1,
            temperatura=70.0,
            vibracao=0.2,
            rpm=1500,
            timestamp=agora,
        )
        models.LeituraTelemetria.objects.create(
            maquina_id=self.machine_real.external_code,
            machine=self.machine_real,
            device_id="COLH-REAL-01",
            message_id="msg-real-1",
            sequence_number=1,
            temperatura=71.0,
            vibracao=0.3,
            rpm=1550,
            timestamp=agora,
        )

    @override_settings(DEMO_MODE=True)
    def test_get_publico_ultimas_leituras_em_demo_mode_retorna_somente_machine_demo(self):
        response = self.client.get(self.url, HTTP_HOST="127.0.0.1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        maquinas = {item["maquina_id"] for item in response.data}
        self.assertIn(self.machine_demo.external_code, maquinas)
        self.assertNotIn(self.machine_real.external_code, maquinas)

    @override_settings(DEMO_MODE=True)
    def test_machine_real_com_telemetria_valida_nao_aparece_no_dataset_demo(self):
        response = self.client.get(self.url, HTTP_HOST="127.0.0.1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leituras_reais = [
            item for item in response.data
            if item["maquina_id"] == self.machine_real.external_code
        ]
        self.assertEqual(leituras_reais, [])

    @override_settings(DEMO_MODE=False)
    def test_demo_mode_false_mantem_contrato_publico_atual_de_leitura(self):
        response = self.client.get(self.url, HTTP_HOST="127.0.0.1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        maquinas = {item["maquina_id"] for item in response.data}
        self.assertIn(self.machine_demo.external_code, maquinas)
        self.assertIn(self.machine_real.external_code, maquinas)
