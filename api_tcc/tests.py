"""
api_tcc/tests.py — Testes de integração reais

Cobertura focada nos comportamentos críticos do sistema:
  1. Deduplicação de UUID (evita duplicatas mesmo sob retry do ESP32)
  2. Rejeição de dados fora do range operacional (sensores com defeito)
  3. Idempotência do endpoint (enviar 2x não quebra nada)
  4. Resposta correta para payload malformado

Decisão: usamos APIClient em vez de requests reais para evitar
dependência de servidor em execução durante CI/CD.

Para rodar:
    python manage.py test api_tcc.tests
"""
from django.test import TestCase
from rest_framework.test import APIClient
from django.conf import settings
from api_tcc.models import LeituraTelemetria
from api_tcc.services.telemetria import validar_payload, registrar_leitura
import uuid


# ──────────────────────────────────────────────────────────────
# Fixtures reutilizáveis
# ──────────────────────────────────────────────────────────────
def _payload_valido(**overrides):
    base = {
        "id":          "123e4567-e89b-12d3-a456-426614174000",
        "maquina_id":  "COLH-TEST-01",
        "temperatura": 78.5,
        "vibracao":    0.42,
        "rpm":         1850,
        "timestamp":   "2026-04-17T15:00:00Z",
    }
    base.update(overrides)
    return base


# ──────────────────────────────────────────────────────────────
# 1. TESTES DE VALIDAÇÃO DE PAYLOAD
# ──────────────────────────────────────────────────────────────
class ValidacaoPayloadTest(TestCase):
    """
    Garante que a função de validação rejeita exatamente o que deve rejeitar
    e aceita o que é válido — sem depender de banco ou HTTP.
    """

    def test_payload_valido_aceito(self):
        valido, motivo = validar_payload(_payload_valido())
        self.assertTrue(valido, f"Payload válido foi rejeitado: {motivo}")

    def test_temperatura_negativa_rejeitada(self):
        """
        Temperatura -999 é fisicamente impossível em campo.
        Isso acontece quando o sensor do ESP32 perde conexão e retorna -999.
        """
        valido, motivo = validar_payload(_payload_valido(temperatura=-999))
        self.assertFalse(valido)
        self.assertIn("temperatura", motivo)

    def test_temperatura_acima_limite_rejeitada(self):
        valido, motivo = validar_payload(_payload_valido(temperatura=200))
        self.assertFalse(valido)
        self.assertIn("temperatura", motivo)

    def test_vibracao_negativa_rejeitada(self):
        valido, motivo = validar_payload(_payload_valido(vibracao=-0.1))
        self.assertFalse(valido)
        self.assertIn("vibracao", motivo)

    def test_rpm_texto_rejeitado(self):
        """
        Firmware com bug pode mandar "rpm": "erro" em vez de inteiro.
        """
        valido, motivo = validar_payload(_payload_valido(rpm="erro"))
        self.assertFalse(valido)
        self.assertIn("rpm", motivo)

    def test_maquina_id_vazio_rejeitado(self):
        valido, motivo = validar_payload(_payload_valido(maquina_id=""))
        self.assertFalse(valido)
        self.assertIn("maquina_id", motivo)

    def test_campo_obrigatorio_ausente_rejeitado(self):
        payload = _payload_valido()
        del payload["temperatura"]
        valido, motivo = validar_payload(payload)
        self.assertFalse(valido)
        self.assertIn("temperatura", motivo)

    def test_temperatura_como_string_numerica_aceita(self):
        """
        Alguns firmwares mandam "85.5" (string) em vez de 85.5 (float).
        O sistema deve aceitar e converter.
        """
        valido, motivo = validar_payload(_payload_valido(temperatura="85.5"))
        self.assertTrue(valido, f"String numérica válida foi rejeitada: {motivo}")


# ──────────────────────────────────────────────────────────────
# 2. TESTES DE DEDUPLICAÇÃO (O MAIS CRÍTICO)
# ──────────────────────────────────────────────────────────────
class DeduplicacaoUUIDTest(TestCase):
    """
    O ESP32 implementa retry com backoff exponencial.
    Se o servidor recebeu mas a confirmação se perdeu no WiFi,
    o firmware reenvía o mesmo pacote.
    O banco não pode ter duplicatas — isso corromperia análises de IA.
    """

    def test_primeira_leitura_salva(self):
        status, id_retornado = registrar_leitura(_payload_valido())
        self.assertEqual(status, "criado")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)

    def test_segundo_envio_mesmo_uuid_ignorado(self):
        """
        Garantia de idempotência: enviar 2x o mesmo UUID
        deve resultar em exatamente 1 registro no banco.
        """
        payload = _payload_valido()
        registrar_leitura(payload)
        status, _ = registrar_leitura(payload)  # segundo envio

        self.assertEqual(status, "duplicata")
        self.assertEqual(LeituraTelemetria.objects.count(), 1,
                         "UUID duplicado foi salvo no banco — violação de idempotência")

    def test_uuids_diferentes_salvos_separadamente(self):
        registrar_leitura(_payload_valido(id=str(uuid.uuid4())))
        registrar_leitura(_payload_valido(id=str(uuid.uuid4())))
        self.assertEqual(LeituraTelemetria.objects.count(), 2)


# ──────────────────────────────────────────────────────────────
# 3. TESTES DE INTEGRAÇÃO VIA HTTP (endpoint real)
# ──────────────────────────────────────────────────────────────
class EndpointIngestaoTest(TestCase):
    """
    Testa o endpoint /api/telemetria/ end-to-end via HTTP.
    Cobre o fluxo completo: request → view → service → banco.
    """

    def setUp(self):
        self.client = APIClient()
        self.headers = {"HTTP_X_API_KEY": getattr(settings, "FIELDNODE_API_KEY", "fieldnode-demo-2024")}

    def test_ingestao_valida_retorna_201(self):
        payload = _payload_valido(id=str(uuid.uuid4()))
        response = self.client.post(
            "/api/telemetria/", payload, format="json", **self.headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "ok")

    def test_duplicata_retorna_200_sem_duplicar_banco(self):
        payload = _payload_valido(id=str(uuid.uuid4()))
        self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        response = self.client.post("/api/telemetria/", payload, format="json", **self.headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "duplicata ignorada")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)

    def test_sem_api_key_retorna_401(self):
        payload = _payload_valido(id=str(uuid.uuid4()))
        response = self.client.post("/api/telemetria/", payload, format="json")
        self.assertEqual(response.status_code, 401)

    def test_temperatura_invalida_retorna_400(self):
        """
        Dado absurdo de sensor deve ser rejeitado na camada de serviço,
        não chegar ao banco nem à IA.
        """
        payload = _payload_valido(id=str(uuid.uuid4()), temperatura=-999)
        response = self.client.post(
            "/api/telemetria/", payload, format="json", **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

    def test_payload_sem_maquina_id_retorna_400(self):
        payload = _payload_valido(id=str(uuid.uuid4()))
        del payload["maquina_id"]
        response = self.client.post(
            "/api/telemetria/", payload, format="json", **self.headers
        )
        self.assertEqual(response.status_code, 400)


# ──────────────────────────────────────────────────────────────
# 4. TESTE: IA NÃO QUEBRA COM DADOS INSUFICIENTES
# ──────────────────────────────────────────────────────────────
class IAResilienciaTest(TestCase):
    """
    A IA exige mínimo de leituras para funcionar.
    Garantir que ela retorna status claro em vez de erro 500
    quando há poucos dados — situação comum no início da implantação.
    """

    def setUp(self):
        self.client = APIClient()

    def test_anomalias_sem_dados_retorna_dados_insuficientes(self):
        response = self.client.get("/api/anomalias/?maquina_id=MAQUINA-INEXISTENTE")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "dados_insuficientes")

    def test_manutencao_sem_maquina_id_retorna_400(self):
        response = self.client.get("/api/manutencao/")
        self.assertEqual(response.status_code, 400)
