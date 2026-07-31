import uuid

from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from api_tcc.models import (
    AlturadoCorte,
    Colheitadeira,
    Combustivel,
    EstadodeMovimento,
    LeituraTelemetria,
    Marca,
    Modelo,
    Operario,
    PressaodoCorte,
    PressaoPneus,
    StatusdeOperacao,
    TempUmi_Ambiente,
    TemperaturaMaquina,
    UnidadedeMedida,
)


def _criar_maquina(maquina_id: str) -> Colheitadeira:
    unidade, _ = UnidadedeMedida.objects.get_or_create(id=1, defaults={"nome": "Centímetro"})
    marca, _ = Marca.objects.get_or_create(nome="CLAAS")
    modelo, _ = Modelo.objects.get_or_create(nome=maquina_id, defaults={"marca": marca})
    combustivel, _ = Combustivel.objects.get_or_create(tipo="Diesel", defaults={"porcentagem": 100.0})
    pressao_pneus, _ = PressaoPneus.objects.get_or_create(pressao=2.5, defaults={"unidade_de_medida": unidade})
    altura_corte, _ = AlturadoCorte.objects.get_or_create(altura=5.0, defaults={"unidade_de_medida": unidade})
    pressao_corte, _ = PressaodoCorte.objects.get_or_create(pressao=30.0, defaults={"unidade_de_medida": unidade})
    temp_umi, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=25.0, umidade=60.0)
    temp_maquina, _ = TemperaturaMaquina.objects.get_or_create(temperatura=85.0, defaults={"maquina": modelo})
    operario, _ = Operario.objects.get_or_create(nome="Operário Teste", defaults={"tempo_de_servico": 5, "no_banco": True})
    status_op, _ = StatusdeOperacao.objects.get_or_create(em_operacao=True, defaults={"tempo_de_operacao": 8.0})
    estado_mov, _ = EstadodeMovimento.objects.get_or_create(em_movimento=True, defaults={"velocidade": 6.5})
    colheitadeira, _ = Colheitadeira.objects.get_or_create(
        modelo=modelo,
        defaults={
            "maquina_id": maquina_id,
            "combustivel": combustivel,
            "pressao_pneus": pressao_pneus,
            "altura_do_corte": altura_corte,
            "pressao_do_corte": pressao_corte,
            "temp_umi_ambiente": temp_umi,
            "temperatura_maquina": temp_maquina,
            "operario": operario,
            "status_de_operacao": status_op,
            "estado_de_movimento": estado_mov,
        },
    )
    return colheitadeira


def _payload(**overrides):
    base = {
        "id": str(uuid.uuid4()),
        "maquina_id": "COLH-T01",
        "temperatura": 72.0,
        "vibracao": 0.35,
        "rpm": 1800,
        "timestamp": "2026-06-01T10:00:00Z",
    }
    base.update(overrides)
    return base


class IngestaoTelemetriaTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _criar_maquina("COLH-T01")

    def setUp(self):
        self.client = APIClient()
        self.headers = {"HTTP_X_API_KEY": getattr(settings, "FIELDNODE_API_KEY", "fieldnode-demo-2024")}

    def test_ingestao_valida_retorna_201(self):
        response = self.client.post("/api/telemetria/", _payload(), format="json", **self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)

    def test_ingestao_invalida_retorna_400(self):
        response = self.client.post(
            "/api/telemetria/", _payload(temperatura=-999), format="json", **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

    def test_ingestao_duplicada_retorna_200_sem_duplicar(self):
        payload = _payload()
        self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        response = self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "duplicata ignorada")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)
