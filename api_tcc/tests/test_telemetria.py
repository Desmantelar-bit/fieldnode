import uuid
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import requests

from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.api.serializers import LeituraTelemetriaSerializer
from api_tcc.services.telemetria import registrar_leitura, validar_payload

from api_tcc.models import (
    AlturadoCorte,
    Colheitadeira,
    Combustivel,
    EstadodeMovimento,
    LeituraTelemetria,
    DeadLetterEntry,
    Machine,
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
from simulators.edge_client import EdgeBuffer, EdgeClient, generate_payload


class _APIResponseAdapter:
    def __init__(self, response):
        self.status_code = response.status_code
        self._data = response.data

    def json(self):
        return self._data


class _DropFirstAckSession:
    def __init__(self, api_client, api_key):
        self.api_client = api_client
        self.api_key = api_key
        self.drop = True

    def post(self, _url, *, json, headers, timeout):
        response = self.api_client.post("/api/telemetria/", json, format="json",
                                        HTTP_X_API_KEY=self.api_key)
        if self.drop:
            self.drop = False
            raise requests.ConnectionError("response lost after server commit")
        return _APIResponseAdapter(response)


class _APIClientSession:
    def __init__(self, api_client, api_key):
        self.api_client = api_client
        self.api_key = api_key

    def post(self, _url, *, json, headers, timeout):
        response = self.api_client.post("/api/telemetria/", json, format="json",
                                        HTTP_X_API_KEY=self.api_key)
        return _APIResponseAdapter(response)


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
        self.headers = {"HTTP_X_API_KEY": getattr(settings, "FIELDNODE_API_KEY", "00000000-0000-4000-8000-000000000000")}

    def test_edge_recupera_queda_apos_persistencia_com_uma_linha(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "edge.sqlite3"
            api_key = getattr(settings, "FIELDNODE_API_KEY", "00000000-0000-4000-8000-000000000000")
            payload = generate_payload("EDGE-RECOVERY", 1, 0, boot_id=str(uuid.uuid4()))
            buffer = EdgeBuffer(db_path, "EDGE-RECOVERY")
            buffer.enqueue(payload)
            client = EdgeClient(buffer, "http://fieldnode/api/telemetria/", api_key,
                                session=_DropFirstAckSession(self.client, api_key), backoff_base=0)
            self.assertEqual(client.synchronize(), 0)
            self.assertEqual(LeituraTelemetria.objects.filter(message_id=payload["message_id"]).count(), 1)
            self.assertEqual(buffer.counts().get("PENDENTE"), 1)
            buffer.close()

            restarted = EdgeBuffer(db_path, "EDGE-RECOVERY")
            session = _DropFirstAckSession(self.client, api_key)
            session.drop = False
            replay_client = EdgeClient(restarted, "http://fieldnode/api/telemetria/", api_key,
                                       session=session, backoff_base=0)
            self.assertEqual(replay_client.synchronize(), 1)
            self.assertEqual(LeituraTelemetria.objects.filter(message_id=payload["message_id"]).count(), 1)
            self.assertEqual(restarted.counts(), {})
            self.assertEqual(restarted.cursor(), 1)
            restarted.close()

    def test_edge_conflict_registra_dlq_e_fica_blocked(self):
        api_key = getattr(settings, "FIELDNODE_API_KEY", "00000000-0000-4000-8000-000000000000")
        original = generate_payload("EDGE-CONFLICT", 1, 0, boot_id=str(uuid.uuid4()))
        original["message_id"] = "stable-conflict-id"
        self.client.post("/api/telemetria/", original, format="json", HTTP_X_API_KEY=api_key)
        changed = {**original, "temperatura": 73.0}
        with tempfile.TemporaryDirectory() as temp_dir:
            buffer = EdgeBuffer(Path(temp_dir) / "edge.sqlite3", "EDGE-CONFLICT")
            buffer.enqueue(changed)
            EdgeClient(buffer, "http://fieldnode/api/telemetria/", api_key,
                       session=_APIClientSession(self.client, api_key), backoff_base=0).synchronize()
            row = buffer.connection.execute("SELECT status FROM outbox").fetchone()
            self.assertEqual(row["status"], "BLOCKED")
            self.assertEqual(buffer.cursor(), 0)
            self.assertTrue(DeadLetterEntry.objects.filter(contexto="SYNC").exists())
            self.assertEqual(LeituraTelemetria.objects.filter(message_id="stable-conflict-id").count(), 1)
            buffer.close()

    def test_lote_http_500_preserva_confirmados_e_identifica_pendentes(self):
        first = _payload(device_id="BATCH-500", message_id="confirmed-1", sequence_number=1,
                         maquina_id="BATCH-500")
        status_item, reading_id = registrar_leitura(first)
        self.assertEqual(status_item, "criado")
        payloads = [first, {**first, "message_id": "failed-2", "sequence_number": 2},
                    {**first, "message_id": "pending-3", "sequence_number": 3}]
        with patch("api_tcc.api.views_ingestao.registrar_leitura",
                   side_effect=[("criado", reading_id), ("erro", "db down")]):
            response = self.client.post("/api/telemetria/lote/", {"leituras": payloads},
                                        format="json", **self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertEqual([item["status"] for item in response.data["items"]], ["acked"])
        self.assertEqual(response.data["failure"]["message_id"], "failed-2")
        self.assertEqual(response.data["pending_message_ids"], ["pending-3"])
        self.assertEqual(LeituraTelemetria.objects.filter(device_id="BATCH-500").count(), 1)

    def test_ingestao_valida_retorna_201(self):
        response = self.client.post(
            "/api/telemetria/", _payload(maquina_id=" colh-t01 "), format="json", **self.headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "acked")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)
        leitura = LeituraTelemetria.objects.get()
        self.assertIsNotNone(leitura.machine)
        self.assertIsNotNone(leitura.trust_score)
        self.assertEqual(leitura.maquina_id, "COLH-T01")
        self.assertEqual(leitura.machine.external_code, "COLH-T01")
        serialized = LeituraTelemetriaSerializer(leitura).data
        self.assertIn("machine", serialized)
        self.assertIn("machine_id", serialized)
        self.assertNotIn("seq_id", serialized)

    def test_ingestao_com_schema_version_retorna_201(self):
        response = self.client.post(
            "/api/telemetria/",
            _payload(schema_version="1.0", maquina_id="schema-01"),
            format="json",
            **self.headers,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(LeituraTelemetria.objects.count(), 1)

    def test_ingestao_sem_schema_version_retorna_201(self):
        payload = _payload(maquina_id="schema-legacy-01")

        with self.assertLogs("api_tcc.services.telemetria", level="WARNING") as logs:
            response = self.client.post(
                "/api/telemetria/", payload, format="json", **self.headers
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(LeituraTelemetria.objects.count(), 1)
        self.assertTrue(any("schema_version" in mensagem for mensagem in logs.output))

    def test_ingestao_sem_api_key_retorna_401(self):
        response = self.client.post(
            "/api/telemetria/", _payload(maquina_id="sem-chave-01"), format="json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

    def test_ingestao_com_api_key_invalida_retorna_401(self):
        response = self.client.post(
            "/api/telemetria/",
            _payload(maquina_id="chave-invalida-01"),
            format="json",
            HTTP_X_API_KEY="chave-invalida",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

    def test_ingestao_mqtt_reutiliza_machine_normalizada(self):
        status_1, _ = registrar_leitura(_payload(maquina_id=" mqtt-01 "))
        status_2, _ = registrar_leitura(
            _payload(maquina_id="MQTT-01", timestamp="2026-06-01T10:01:00Z")
        )

        self.assertEqual(status_1, "criado")
        self.assertEqual(status_2, "criado")
        self.assertEqual(Machine.objects.filter(external_code="MQTT-01").count(), 1)
        leituras = LeituraTelemetria.objects.order_by("timestamp")
        self.assertEqual(leituras.count(), 2)
        self.assertIsNotNone(leituras[0].machine)
        self.assertEqual(leituras[0].machine_id, leituras[1].machine_id)
        self.assertEqual(leituras[0].machine.external_code, "MQTT-01")

    def test_ingestao_em_lote_grava_machine(self):
        response = self.client.post(
            "/api/telemetria/lote/",
            {"leituras": [_payload(maquina_id=" lote-01 ")]},
            format="json",
            **self.headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["salvas"], 1)
        leitura = LeituraTelemetria.objects.get()
        self.assertIsNotNone(leitura.machine)
        self.assertEqual(leitura.machine.external_code, "LOTE-01")

    def test_ingestao_em_lote_sem_api_key_retorna_401(self):
        response = self.client.post(
            "/api/telemetria/lote/",
            {"leituras": [_payload(maquina_id="lote-sem-chave-01")]},
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

    def test_ingestao_em_lote_com_api_key_invalida_retorna_401(self):
        response = self.client.post(
            "/api/telemetria/lote/",
            {"leituras": [_payload(maquina_id="lote-chave-invalida-01")]},
            format="json",
            HTTP_X_API_KEY="chave-invalida",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

    def test_ingestao_invalida_retorna_400(self):
        response = self.client.post(
            "/api/telemetria/", _payload(temperatura=-999, message_id="rejected-1"), format="json", **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "rejected")
        self.assertEqual(response.data["message_id"], "rejected-1")
        self.assertEqual(LeituraTelemetria.objects.count(), 0)

    def test_ingestao_duplicada_retorna_200_sem_duplicar(self):
        payload = _payload()
        self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        response = self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "duplicate")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)

    def test_ingestao_retorna_ack_verificavel_para_o_edge(self):
        payload = _payload(
            device_id="EDGE-ACK-01",
            message_id="edge-msg-001",
            sequence_number=7,
            maquina_id="EDGE-ACK-01",
        )
        response = self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        leitura = LeituraTelemetria.objects.get()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["device_id"], leitura.device_id)
        self.assertEqual(response.data["message_id"], leitura.message_id)
        self.assertEqual(response.data["sequence_number"], 7)
        self.assertEqual(response.data["payload_hash"], leitura.payload_hash)
        self.assertEqual(response.data["sync_cursor"], 0)
        self.assertEqual(response.data["last_acked_sequence"], 0)
        self.assertEqual(response.data["status"], "acked")

    def test_hash_divergente_para_mesma_identidade_retorna_conflict(self):
        payload = _payload(device_id="SYNC-CONFLICT", message_id="same-message", maquina_id="SYNC-CONFLICT")
        first = self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        changed = {**payload, "temperatura": 73.0}
        second = self.client.post("/api/telemetria/", changed, format="json", **self.headers)
        self.assertEqual(first.data["status"], "acked")
        self.assertEqual(second.status_code, 409)
        self.assertEqual(second.data["status"], "conflict")
        self.assertEqual(LeituraTelemetria.objects.filter(message_id="same-message").count(), 1)
        self.assertTrue(DeadLetterEntry.objects.filter(contexto="SYNC").exists())

    def test_temporal_unsynced_reconstroi_lote_atrasado_por_boot(self):
        boot = uuid.uuid4()
        base = {"maquina_id": "TIME-BOOT", "device_id": "TIME-BOOT", "temperatura": 72,
                "vibracao": 0.4, "rpm": 1700, "time_source": "unsynced", "boot_id": str(boot)}
        old = {**base, "message_id": "old", "sequence_number": 1, "uptime_ms": 0}
        self.assertEqual(registrar_leitura(old)[0], "criado")
        middle = {**base, "message_id": "middle", "sequence_number": 2, "uptime_ms": 5000}
        self.assertEqual(registrar_leitura(middle)[0], "criado")
        anchor_time = timezone.now()
        anchor = {**base, "message_id": "anchor", "sequence_number": 3,
                  "uptime_ms": 21_600_000, "time_source": "gateway", "timestamp": anchor_time.isoformat()}
        self.assertEqual(registrar_leitura(anchor)[0], "criado")
        from api_tcc.services.event_time import reconstruct_boot
        self.assertEqual(reconstruct_boot(boot), 2)
        reading = LeituraTelemetria.objects.get(message_id="old")
        first_provenance = reading.time_provenance
        self.assertEqual(reading.timestamp, anchor_time - timedelta(hours=6))
        self.assertNotEqual(reading.timestamp, reading.recebido_em)
        self.assertAlmostEqual((reading.recebido_em - reading.timestamp).total_seconds(), 6 * 3600, delta=2)
        self.assertEqual(reading.time_source, "unsynced")
        self.assertEqual(reading.event_time_confidence, 0.65)
        ordered = list(LeituraTelemetria.objects.filter(boot_id=boot).order_by("timestamp").values_list("message_id", flat=True))
        self.assertEqual(ordered, ["old", "middle", "anchor"])
        self.assertEqual(reconstruct_boot(boot), 0)
        reading.refresh_from_db()
        self.assertEqual(reading.time_provenance, first_provenance)
        self.assertEqual(reading.time_provenance["original"]["resolution"], "unresolved")

    def test_validacao_campos_temporais(self):
        self.assertTrue(validar_payload(_payload(time_source="unsynced", timestamp=None))[0])
        self.assertFalse(validar_payload(_payload(time_source="unknown"))[0])
        self.assertFalse(validar_payload(_payload(boot_id="not-a-uuid"))[0])
        self.assertFalse(validar_payload(_payload(uptime_ms=-1))[0])
        self.assertFalse(validar_payload(_payload(uptime_ms=1.5))[0])
        self.assertFalse(validar_payload(_payload(time_source="ntp", timestamp=None))[0])

    def test_leitura_sem_relogio_persiste_fator_temporal_no_trust(self):
        payload = _payload(maquina_id="TIME-UNSYNCED", device_id="TIME-UNSYNCED",
                           message_id="unsynced-1", time_source="unsynced",
                           boot_id=str(uuid.uuid4()), uptime_ms=2500, timestamp=None)
        response = self.client.post("/api/telemetria/", payload, format="json", **self.headers)
        self.assertEqual(response.status_code, 201)
        reading = LeituraTelemetria.objects.get(message_id="unsynced-1")
        self.assertIsNone(reading.timestamp)
        self.assertEqual(reading.event_time_confidence, 0.0)
        self.assertIn("hora_do_dispositivo_nao_confiavel", reading.trust_factors)

    def test_temporal_boots_isolados_e_sem_ancora_nao_inventa_hora(self):
        boot_a, boot_b = uuid.uuid4(), uuid.uuid4()
        for boot, message in ((boot_a, "unresolved-a"), (boot_b, "unresolved-b")):
            payload = {"maquina_id": "TIME-ISOLATION", "device_id": "TIME-ISOLATION",
                       "message_id": message, "sequence_number": 1, "temperatura": 72,
                       "vibracao": 0.4, "rpm": 1700, "time_source": "unsynced",
                       "boot_id": str(boot), "uptime_ms": 5000}
            self.assertEqual(registrar_leitura(payload)[0], "criado")
        anchor = {"maquina_id": "TIME-ISOLATION", "device_id": "TIME-ISOLATION",
                  "message_id": "anchor-a", "sequence_number": 2, "temperatura": 72,
                  "vibracao": 0.4, "rpm": 1700, "time_source": "ntp",
                  "boot_id": str(boot_a), "uptime_ms": 6000,
                  "timestamp": timezone.now().isoformat()}
        registrar_leitura(anchor)
        from api_tcc.services.event_time import reconstruct_boot
        reconstruct_boot(boot_a)
        a = LeituraTelemetria.objects.get(message_id="unresolved-a")
        b = LeituraTelemetria.objects.get(message_id="unresolved-b")
        self.assertIsNotNone(a.timestamp)
        self.assertIsNone(b.timestamp)


class SchemaVersionTest(TestCase):
    def test_payload_sem_schema_version_injeta_versao_e_registra_warning(self):
        payload = _payload()

        with self.assertLogs("api_tcc.services.telemetria", level="WARNING") as logs:
            valido, motivo = validar_payload(payload)

        self.assertTrue(valido, motivo)
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertTrue(any("schema_version" in mensagem for mensagem in logs.output))
        self.assertTrue(any("Assumindo '1.0'" in mensagem for mensagem in logs.output))

    def test_payload_com_schema_version_none_injeta_versao_e_registra_warning(self):
        payload = _payload(schema_version=None)

        with self.assertLogs("api_tcc.services.telemetria", level="WARNING") as logs:
            valido, motivo = validar_payload(payload)

        self.assertTrue(valido, motivo)
        self.assertEqual(payload["schema_version"], "1.0")
        self.assertTrue(any("schema_version" in mensagem for mensagem in logs.output))
