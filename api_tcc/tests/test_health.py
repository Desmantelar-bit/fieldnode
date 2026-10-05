"""
api_tcc/tests/test_health.py

Testes do endpoint GET /api/health/ (S7-T1).

Cobertura:
  1. Cenário saudável: 200, JSON com os quatro campos obrigatórios.
  2. Ausência de MQTT: mqtt_last_seen_seconds é null (não 0 fabricado).
  3. Presença de leitura: mqtt_last_seen_seconds é int >= 0.
  4. Falha de banco: database != 'ok', status != 'ok'.
"""
import uuid
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.api.views_health import _mqtt_last_seen_seconds, _verificar_banco
from api_tcc.models import LeituraTelemetria


# ──────────────────────────────────────────────────────────────────────────────
# Fixture mínima — cria uma LeituraTelemetria sem precisar de toda a árvore
# de related objects da Colheitadeira (que é usada nos testes de integração).
# A coluna maquina_id em LeituraTelemetria é CharField livre (sem FK obrigatória),
# conforme models.py linha 220 (blank=True, null=True na FK machine).
# ──────────────────────────────────────────────────────────────────────────────

def _criar_leitura_minima():
    """
    Cria o registro mínimo necessário para popular LeituraTelemetria.recebido_em.
    Não depende de Colheitadeira nem de Machine — apenas dos campos obrigatórios
    de LeituraTelemetria: id (UUID), maquina_id, temperatura, vibracao, rpm, timestamp.
    """
    return LeituraTelemetria.objects.create(
        id=uuid.uuid4(),
        maquina_id="HEALTH-TEST",
        temperatura=70.0,
        vibracao=0.30,
        rpm=1800,
        timestamp=timezone.now(),
    )


# ──────────────────────────────────────────────────────────────────────────────
# 1. Testes de unidade das funções auxiliares
# ──────────────────────────────────────────────────────────────────────────────

class VerificarBancoTest(TestCase):
    """_verificar_banco() deve executar SELECT 1 real e retornar 'ok'."""

    def test_banco_disponivel_retorna_ok(self):
        resultado = _verificar_banco()
        self.assertEqual(resultado, "ok")

    def test_banco_indisponivel_retorna_erro(self):
        from django.db.utils import OperationalError as DjangoOpError
        with patch(
            "api_tcc.api.views_health.connection.cursor",
            side_effect=DjangoOpError("banco fora"),
        ):
            resultado = _verificar_banco()
        self.assertEqual(resultado, "erro")

    def test_excecao_generica_retorna_erro(self):
        with patch(
            "api_tcc.api.views_health.connection.cursor",
            side_effect=RuntimeError("erro inesperado"),
        ):
            resultado = _verificar_banco()
        self.assertEqual(resultado, "erro")


class MqttLastSeenSecondsTest(TestCase):
    """_mqtt_last_seen_seconds() deve usar LeituraTelemetria.recebido_em como fonte."""

    def test_sem_leituras_retorna_none(self):
        """None — não fabrica 0, que significaria 'recebido agora'."""
        self.assertIsNone(_mqtt_last_seen_seconds())

    def test_com_leitura_retorna_int_nao_negativo(self):
        _criar_leitura_minima()
        segundos = _mqtt_last_seen_seconds()
        self.assertIsNotNone(segundos)
        self.assertIsInstance(segundos, int)
        self.assertGreaterEqual(segundos, 0)

    def test_valor_e_coerente_com_tempo_decorrido(self):
        """
        Verifica que o valor calculado é razoável.
        Cria leitura agora → deve retornar segundos próximos de 0.
        Usa margem de 5 segundos para absorver latência do setUp.
        """
        _criar_leitura_minima()
        segundos = _mqtt_last_seen_seconds()
        self.assertLessEqual(segundos, 5, "Valor esperado próximo de 0 para leitura recém-criada")


# ──────────────────────────────────────────────────────────────────────────────
# 2. Testes de integração via HTTP
# ──────────────────────────────────────────────────────────────────────────────

class HealthViewTest(TestCase):
    """
    Testa GET /api/health/ end-to-end.
    Endpoint é público (sem autenticação exigida).
    """

    def setUp(self):
        self.client = APIClient()

    # ── Cenário saudável (sem leituras MQTT ainda) ──────────────────────────

    def test_retorna_200(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)

    def test_resposta_e_json(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response["Content-Type"], "application/json")

    def test_campos_obrigatorios_presentes(self):
        """Os quatro campos do contrato devem estar presentes."""
        response = self.client.get("/api/health/")
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("database", data)
        self.assertIn("mqtt_last_seen_seconds", data)
        self.assertIn("version", data)

    def test_status_ok_com_banco_disponivel(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.json()["status"], "ok")

    def test_database_ok_com_banco_disponivel(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.json()["database"], "ok")

    def test_version_nao_e_vazia_nem_nula(self):
        response = self.client.get("/api/health/")
        version = response.json()["version"]
        self.assertIsNotNone(version)
        self.assertNotEqual(version, "")

    def test_nao_exige_autenticacao(self):
        """Healthcheck deve ser acessível sem token."""
        cliente_anonimo = APIClient()
        response = cliente_anonimo.get("/api/health/")
        self.assertEqual(response.status_code, 200)

    # ── Ausência de MQTT ────────────────────────────────────────────────────

    def test_sem_leituras_mqtt_last_seen_seconds_e_null(self):
        """
        Sem nenhuma leitura no banco, mqtt_last_seen_seconds deve ser null.
        Não deve retornar 0 (que seria falso positivo de 'recebido agora').
        """
        response = self.client.get("/api/health/")
        self.assertIsNone(response.json()["mqtt_last_seen_seconds"])

    # ── Com leitura MQTT presente ───────────────────────────────────────────

    def test_com_leitura_mqtt_last_seen_seconds_e_inteiro(self):
        _criar_leitura_minima()
        response = self.client.get("/api/health/")
        segundos = response.json()["mqtt_last_seen_seconds"]
        self.assertIsNotNone(segundos)
        self.assertIsInstance(segundos, int)

    def test_com_leitura_mqtt_last_seen_seconds_nao_e_negativo(self):
        _criar_leitura_minima()
        response = self.client.get("/api/health/")
        self.assertGreaterEqual(response.json()["mqtt_last_seen_seconds"], 0)

    # ── Falha de banco ──────────────────────────────────────────────────────

    def test_falha_banco_nao_retorna_database_ok(self):
        """
        Quando o banco falha, database NÃO deve ser 'ok'.

        Mocka _verificar_banco diretamente para isolar o comportamento da view
        sem afetar o ORM (que também usa connection.cursor internamente).
        A função _verificar_banco já tem seus próprios testes unitários de exceção.
        """
        with patch(
            "api_tcc.api.views_health._verificar_banco",
            return_value="erro",
        ):
            response = self.client.get("/api/health/")

        data = response.json()
        self.assertNotEqual(data["database"], "ok")
        self.assertNotEqual(data["status"], "ok")

    def test_falha_banco_status_e_degradado(self):
        with patch(
            "api_tcc.api.views_health._verificar_banco",
            return_value="erro",
        ):
            response = self.client.get("/api/health/")

        self.assertEqual(response.json()["status"], "degradado")
