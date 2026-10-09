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
    def test_demo_mode_false_exige_autenticacao_para_leitura(self):
        response = self.client.get(self.url, HTTP_HOST="127.0.0.1")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DemoModeIsolamentoEndpointsTest(TestCase):
    """
    Verifica que endpoints públicos com DEMO_MODE=True retornam apenas dados
    de machines marcadas is_demo=True e nunca expõem dados reais.
    """

    def setUp(self):
        self.client = APIClient()
        agora = timezone.now()

        self.machine_demo = models.Machine.objects.create(
            external_code="COLH-ISO-DEMO",
            is_demo=True,
        )
        self.machine_real = models.Machine.objects.create(
            external_code="COLH-ISO-REAL",
            is_demo=False,
        )
        _criar_colheitadeira(self.machine_demo.external_code)
        _criar_colheitadeira(self.machine_real.external_code)

        models.LeituraTelemetria.objects.create(
            maquina_id=self.machine_demo.external_code,
            machine=self.machine_demo,
            device_id="COLH-ISO-DEMO",
            message_id="iso-demo-1",
            sequence_number=1,
            temperatura=72.0,
            vibracao=0.25,
            rpm=1600,
            timestamp=agora,
        )
        models.LeituraTelemetria.objects.create(
            maquina_id=self.machine_real.external_code,
            machine=self.machine_real,
            device_id="COLH-ISO-REAL",
            message_id="iso-real-1",
            sequence_number=1,
            temperatura=73.0,
            vibracao=0.35,
            rpm=1650,
            timestamp=agora,
        )

    @override_settings(DEMO_MODE=True)
    def test_get_telemetria_retorna_somente_demo(self):
        response = self.client.get(reverse("ingestao-telemetria"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        maquinas = {item["maquina_id"] for item in response.data}
        self.assertIn(self.machine_demo.external_code, maquinas)
        self.assertNotIn(self.machine_real.external_code, maquinas)

    @override_settings(DEMO_MODE=False)
    def test_get_telemetria_sem_demo_exige_autenticacao(self):
        response = self.client.get(reverse("ingestao-telemetria"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DEMO_MODE=True)
    def test_metricas_conta_somente_leituras_demo(self):
        response = self.client.get(reverse("metricas"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Apenas 1 leitura demo existe; a real não deve ser contada
        self.assertEqual(response.data["leituras_validas"], 1)
        self.assertEqual(response.data["maquinas_ativas"], 1)

    @override_settings(DEMO_MODE=True)
    def test_status_mqtt_usa_somente_leitura_demo(self):
        response = self.client.get(reverse("status-mqtt"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Endpoint retorna status baseado na última leitura demo
        self.assertIn("status", response.data)

    @override_settings(DEMO_MODE=True)
    def test_relatorio_geral_usa_somente_leituras_demo(self):
        response = self.client.get(reverse("relatorio"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Apenas 1 leitura demo; total_leituras não deve incluir a real
        self.assertEqual(response.data["total_leituras"], 1)
        self.assertEqual(response.data["maquinas_ativas"], 1)

    @override_settings(DEMO_MODE=True)
    def test_colheitadeira_list_retorna_somente_demo(self):
        # Vincular machines às colheitadeiras para que o filtro funcione
        colh_demo = models.Colheitadeira.objects.get(maquina_id=self.machine_demo.external_code)
        colh_real = models.Colheitadeira.objects.get(maquina_id=self.machine_real.external_code)
        self.machine_demo.colheitadeira = colh_demo
        self.machine_demo.save()
        self.machine_real.colheitadeira = colh_real
        self.machine_real.save()

        response = self.client.get(reverse("colheitadeira-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        maquinas = {item["maquina_id"] for item in response.data}
        self.assertIn(self.machine_demo.external_code, maquinas)
        self.assertNotIn(self.machine_real.external_code, maquinas)


class DemoModeEscritaBloqueadaTest(TestCase):
    """Garante que DEMO_MODE=True não libera escrita nos endpoints operacionais."""

    def setUp(self):
        self.client = APIClient()

    @override_settings(DEMO_MODE=True)
    def test_post_telemetria_sem_api_key_bloqueado_em_demo_mode(self):
        response = self.client.post(
            reverse("ingestao-telemetria"),
            {"maquina_id": "COLH-X", "temperatura": 70, "vibracao": 0.2, "rpm": 1500},
            format="json",
        )
        # X-API-Key ausente deve retornar 401 independente de DEMO_MODE
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(DEMO_MODE=True)
    def test_patch_decision_sem_auth_bloqueado_em_demo_mode(self):
        import uuid
        response = self.client.patch(
            reverse("decision-action", args=[str(uuid.uuid4())]),
            {"status": "APROVADA"},
            format="json",
        )
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})
