"""
Testes obrigatórios S1-T5 — Contrato temporal, proveniência e reconstrução offline.

Cobre os 7 cenários especificados:
  Teste 1: lote fora de ordem (reordenação por uptime)
  Teste 2: lote atrasado de 6 horas (event_time ≠ ingested_at)
  Teste 3: boots diferentes (isolamento de âncoras)
  Teste 4: horário não sincronizado (unsynced → confiança baixa + Trust Score)
  Teste 5: NTP posterior (reconstrução rastreável)
  Teste 6: RTC com deriva (confiança reflete incerteza)
  Teste 7: ausência de âncora (sem event_time reconstruído precisamente)
"""
from __future__ import annotations

import uuid
from datetime import timedelta
from types import SimpleNamespace

from django.test import TestCase
from django.utils import timezone

from api_tcc.models import DeviceClockAnchor, LeituraTelemetria, MachineDataHealth
from api_tcc.services.data_health import UNSYNCED_TIME_PENALTY, calcular_trust_score
from api_tcc.services.telemetria import registrar_leitura


def _payload(
    device_id: str,
    boot_id: str,
    uptime_ms: int,
    *,
    seq: int | None = None,
    time_source: str = "unsynced",
    timestamp: str | None = None,
    temperatura: float = 72.0,
) -> dict:
    p = {
        "device_id": device_id,
        "maquina_id": device_id,
        "message_id": str(uuid.uuid4()),
        "sequence_number": seq if seq is not None else uptime_ms,
        "boot_id": boot_id,
        "uptime_ms": uptime_ms,
        "time_source": time_source,
        "temperatura": temperatura,
        "vibracao": 0.35,
        "vibracao_unit": "indice_0_10",
        "rpm": 1800,
    }
    if timestamp is not None:
        p["timestamp"] = timestamp
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Teste 1 — lote fora de ordem
# ─────────────────────────────────────────────────────────────────────────────
class TestLoteFora_de_Ordem(TestCase):
    """Envio de uptime 10.000 → 5.000 → 15.000 ms; ordem cronológica = uptime."""

    def test_leituras_fora_de_ordem_reconstruidas_pelo_uptime(self):
        device = "T5-OUT-ORDER-01"
        boot_id = str(uuid.uuid4())

        # Âncora confiável em uptime 10.000 ms
        anchor_ts = "2026-11-05T14:00:00+00:00"
        s_anchor, id_anchor = registrar_leitura(
            _payload(device, boot_id, 10_000, time_source="gateway", timestamp=anchor_ts, seq=2)
        )
        self.assertEqual(s_anchor, "criado")

        # Leitura anterior à âncora: uptime 5.000 ms
        s_before, id_before = registrar_leitura(
            _payload(device, boot_id, 5_000, seq=1)
        )
        self.assertEqual(s_before, "criado")

        # Leitura posterior: uptime 15.000 ms
        s_after, id_after = registrar_leitura(
            _payload(device, boot_id, 15_000, seq=3)
        )
        self.assertEqual(s_after, "criado")

        anchor_reading = LeituraTelemetria.objects.get(id=id_anchor)
        before_reading = LeituraTelemetria.objects.get(id=id_before)
        after_reading = LeituraTelemetria.objects.get(id=id_after)

        # Reconstrução: âncora em 14:00 com uptime 10.000 ms
        # before: 14:00 + (5.000 - 10.000) ms = 13:59:55
        # after:  14:00 + (15.000 - 10.000) ms = 14:00:05
        self.assertEqual(
            before_reading.timestamp,
            anchor_reading.timestamp - timedelta(milliseconds=5_000),
            "uptime 5.000 deve ser 5 segundos antes da âncora de uptime 10.000",
        )
        self.assertEqual(
            after_reading.timestamp,
            anchor_reading.timestamp + timedelta(milliseconds=5_000),
            "uptime 15.000 deve ser 5 segundos depois da âncora",
        )

        # Ordenação cronológica: before < anchor < after
        self.assertLess(before_reading.timestamp, anchor_reading.timestamp)
        self.assertLess(anchor_reading.timestamp, after_reading.timestamp)

        # ingested_at preservado independente de event_time
        for reading in [before_reading, anchor_reading, after_reading]:
            self.assertIsNotNone(reading.recebido_em)

    def test_ingested_at_preservado_independente_da_reconstrucao(self):
        device = "T5-OUT-ORDER-02"
        boot_id = str(uuid.uuid4())

        ts_before_anchor = timezone.now()
        _, id_early = registrar_leitura(
            _payload(device, boot_id, 1_000, seq=1)
        )
        ts_after_anchor = timezone.now()

        _, _ = registrar_leitura(
            _payload(device, boot_id, 10_000, time_source="gateway", timestamp="2026-11-05T18:00:00+00:00", seq=2)
        )

        leitura = LeituraTelemetria.objects.get(id=id_early)
        # recebido_em deve estar entre os dois registros de tempo do teste
        self.assertGreaterEqual(leitura.recebido_em, ts_before_anchor)
        self.assertLessEqual(leitura.recebido_em, ts_after_anchor + timedelta(seconds=5))


# ─────────────────────────────────────────────────────────────────────────────
# Teste 2 — lote atrasado de 6 horas
# ─────────────────────────────────────────────────────────────────────────────
class TestLoteAtrasado6Horas(TestCase):
    """Dispositivo offline 6h; após reconexão, leituras não aparecem como 'agora'."""

    def test_leitura_6h_atrasada_tem_event_time_diferente_de_ingested_at(self):
        device = "T5-DELAY-01"
        boot_id = str(uuid.uuid4())

        # Âncora: NTP marca 14:00, uptime = 21.600.000 ms (6h desde boot)
        # Usamos time_source=ntp para que o timestamp explícito seja respeitado.
        # time_source=gateway usaria received_at (horário de ingestão do servidor).
        anchor_ts = "2026-11-05T14:00:00+00:00"
        s_anchor, id_anchor = registrar_leitura(
            _payload(device, boot_id, 21_600_000, time_source="ntp", timestamp=anchor_ts, seq=100)
        )
        self.assertEqual(s_anchor, "criado")

        # Leitura coletada na hora do boot (uptime 0 → 08:00)
        s_early, id_early = registrar_leitura(
            _payload(device, boot_id, 0, seq=1)
        )
        self.assertEqual(s_early, "criado")

        anchor = LeituraTelemetria.objects.get(id=id_anchor)
        early = LeituraTelemetria.objects.get(id=id_early)

        # event_time da leitura inicial deve ser ~08:00 (14:00 - 6h)
        from django.utils.dateparse import parse_datetime
        anchor_dt = parse_datetime(anchor_ts)
        expected_early_time = anchor_dt - timedelta(milliseconds=21_600_000)
        self.assertEqual(
            early.timestamp,
            expected_early_time,
            "leitura com uptime 0 deve ter event_time = anchor_time - 6h",
        )

        # event_time NÃO deve ser igual ao ingested_at (que é o horário de recepção)
        delta = abs((early.timestamp - early.recebido_em).total_seconds())
        self.assertGreater(
            delta,
            3600,
            "event_time da leitura atrasada deve diferir de ingested_at em pelo menos 1h",
        )

    def test_leitura_intermediaria_reconstruida_corretamente(self):
        device = "T5-DELAY-02"
        boot_id = str(uuid.uuid4())

        # Âncora NTP: uptime 21.600.000 ms = 6h desde o boot
        anchor_ts = "2026-11-05T14:00:00+00:00"
        registrar_leitura(
            _payload(device, boot_id, 21_600_000, time_source="ntp", timestamp=anchor_ts, seq=10)
        )

        # Leitura intermediária: uptime 18.000.000 ms = 5h desde o boot → event_time ~13:00
        s_mid, id_mid = registrar_leitura(
            _payload(device, boot_id, 18_000_000, seq=5)
        )
        self.assertEqual(s_mid, "criado")

        mid = LeituraTelemetria.objects.get(id=id_mid)

        from django.utils.dateparse import parse_datetime
        anchor_dt = parse_datetime(anchor_ts)
        expected = anchor_dt - timedelta(milliseconds=(21_600_000 - 18_000_000))
        self.assertEqual(mid.timestamp, expected)


# ─────────────────────────────────────────────────────────────────────────────
# Teste 3 — boots diferentes são isolados
# ─────────────────────────────────────────────────────────────────────────────
class TestBootsDiferentes(TestCase):
    """Âncora de boot_b não deve afetar leituras de boot_a."""

    def test_ancoras_de_boots_distintos_sao_independentes(self):
        device = "T5-BOOTS-01"
        boot_a = str(uuid.uuid4())
        boot_b = str(uuid.uuid4())

        # Leitura unsynced no boot_a
        s_a, id_a = registrar_leitura(
            _payload(device, boot_a, 5_000, seq=1)
        )
        self.assertEqual(s_a, "criado")
        leitura_a = LeituraTelemetria.objects.get(id=id_a)
        ts_before = leitura_a.timestamp

        # Âncora confiável, mas no boot_b
        registrar_leitura(
            _payload(device, boot_b, 5_000, time_source="ntp", timestamp="2026-11-05T10:00:00+00:00", seq=100)
        )

        # Leitura de boot_a não deve ter sido reconstruída com a âncora de boot_b
        leitura_a.refresh_from_db()
        self.assertEqual(
            leitura_a.timestamp,
            ts_before,
            "âncora de boot_b não deve afetar leituras de boot_a",
        )

    def test_dois_boots_tem_ancoras_independentes(self):
        device = "T5-BOOTS-02"
        boot_a = str(uuid.uuid4())
        boot_b = str(uuid.uuid4())

        # Âncora do boot_a: 10:00
        registrar_leitura(
            _payload(device, boot_a, 0, time_source="ntp", timestamp="2026-11-05T10:00:00+00:00", seq=1)
        )
        # Âncora do boot_b: 14:00
        registrar_leitura(
            _payload(device, boot_b, 0, time_source="ntp", timestamp="2026-11-05T14:00:00+00:00", seq=2)
        )

        anchors = DeviceClockAnchor.objects.filter(device_id=device)
        self.assertEqual(anchors.count(), 2, "cada boot deve ter sua âncora independente")

        boot_ids = set(str(a.boot_id) for a in anchors)
        self.assertIn(boot_a, boot_ids)
        self.assertIn(boot_b, boot_ids)

    def test_reinicializacao_gera_boot_id_diferente(self):
        """Leituras de dois boots não compartilham âncora (simulação de reboot)."""
        device = "T5-BOOTS-03"
        boot_a = str(uuid.uuid4())
        boot_b = str(uuid.uuid4())

        # boot_a acumula leituras unsynced
        for i in range(3):
            registrar_leitura(_payload(device, boot_a, i * 5_000, seq=i))

        # boot_b recebe âncora NTP
        registrar_leitura(
            _payload(device, boot_b, 0, time_source="ntp", timestamp="2026-11-05T12:00:00+00:00", seq=10)
        )

        # Leituras de boot_a não foram alteradas pela âncora de boot_b
        leituras_a = LeituraTelemetria.objects.filter(device_id=device, boot_id=boot_a)
        self.assertEqual(leituras_a.count(), 3)
        for lr in leituras_a:
            self.assertEqual(lr.time_source, "unsynced")


# ─────────────────────────────────────────────────────────────────────────────
# Teste 4 — horário não sincronizado
# ─────────────────────────────────────────────────────────────────────────────
class TestHorarioNaoSincronizado(TestCase):
    """unsynced → confiança baixa + penalidade no Trust Score."""

    def test_unsynced_reduz_trust_score(self):
        base = {
            "timestamp": timezone.now(),
            "temperatura": 72.0,
            "vibracao": 0.35,
            "rpm": 1800,
        }
        trusted = SimpleNamespace(**base, time_source="ntp")
        unsynced = SimpleNamespace(**base, time_source="unsynced")

        trusted_score, _ = calcular_trust_score(trusted, [])
        unsynced_score, reasons = calcular_trust_score(unsynced, [])

        self.assertLess(unsynced_score, trusted_score)
        self.assertAlmostEqual(trusted_score - unsynced_score, UNSYNCED_TIME_PENALTY, places=4)

    def test_unsynced_aparece_nos_motivos_do_trust_score(self):
        leitura = SimpleNamespace(
            timestamp=timezone.now(),
            temperatura=72.0,
            vibracao=0.35,
            rpm=1800,
            time_source="unsynced",
        )
        _, reasons = calcular_trust_score(leitura, [])
        self.assertTrue(
            any("hora do dispositivo nao confiavel" in r for r in reasons),
            f"penalidade temporal deve aparecer nos motivos: {reasons}",
        )

    def test_unsynced_sem_boot_sem_ancora_nao_tem_horario_reconstruido(self):
        """Sem boot_id/uptime, leitura unsynced recebe apenas ingested_at como timestamp."""
        device = "T5-UNSYNC-01"
        # Payload sem boot_id e uptime — ingestão via timestamp do servidor
        payload = {
            "device_id": device,
            "maquina_id": device,
            "message_id": str(uuid.uuid4()),
            "sequence_number": 1,
            "time_source": "gateway",
            "temperatura": 72.0,
            "vibracao": 0.35,
            "vibracao_unit": "indice_0_10",
            "rpm": 1800,
        }
        s, reading_id = registrar_leitura(payload)
        self.assertEqual(s, "criado")
        leitura = LeituraTelemetria.objects.get(id=reading_id)
        self.assertIsNone(leitura.boot_id)
        self.assertIsNone(leitura.uptime_ms)

    def test_fator_temporal_visivel_no_data_health(self):
        device = "T5-UNSYNC-02"
        boot_id = str(uuid.uuid4())
        s, reading_id = registrar_leitura(
            _payload(device, boot_id, 1_000, seq=1)
        )
        self.assertEqual(s, "criado")
        leitura = LeituraTelemetria.objects.get(id=reading_id)
        health = MachineDataHealth.objects.get(machine=leitura.machine)
        sinais = health.sinais_de_alerta
        self.assertTrue(
            sinais.get("hora_dispositivo_nao_confiavel"),
            "sinal hora_dispositivo_nao_confiavel deve ser True para unsynced",
        )

    def test_event_time_confidence_low_para_unsynced(self):
        device = "T5-UNSYNC-03"
        boot_id = str(uuid.uuid4())
        _, reading_id = registrar_leitura(
            _payload(device, boot_id, 500, seq=1)
        )
        leitura = LeituraTelemetria.objects.get(id=reading_id)
        self.assertEqual(leitura.event_time_confidence, "low")
        self.assertEqual(leitura.time_source, "unsynced")


# ─────────────────────────────────────────────────────────────────────────────
# Teste 5 — NTP posterior (device começa offline, sincroniza depois)
# ─────────────────────────────────────────────────────────────────────────────
class TestNTPPosterior(TestCase):
    """Dispositivo começa offline; sincronização NTP posterior reconstrói histórico."""

    def test_ntp_posterior_reconstroi_leituras_anteriores(self):
        device = "T5-NTP-POST-01"
        boot_id = str(uuid.uuid4())

        # Fase 1: dispositivo offline → 3 leituras unsynced
        uptimes = [0, 5_000, 10_000]
        reading_ids = []
        for i, uptime in enumerate(uptimes):
            s, rid = registrar_leitura(
                _payload(device, boot_id, uptime, seq=i + 1)
            )
            self.assertEqual(s, "criado")
            reading_ids.append(rid)

        ts_provisorios = [
            LeituraTelemetria.objects.get(id=rid).timestamp
            for rid in reading_ids
        ]

        # Fase 2: NTP é obtido — uptime 15.000 ms = 15s após boot, horário = 10:00:15
        ntp_ts = "2026-11-05T10:00:15+00:00"
        s_ntp, id_ntp = registrar_leitura(
            _payload(device, boot_id, 15_000, time_source="ntp", timestamp=ntp_ts, seq=4)
        )
        self.assertEqual(s_ntp, "criado")

        # Leituras anteriores devem ter sido reconstruídas
        from django.utils.dateparse import parse_datetime
        ntp_dt = parse_datetime(ntp_ts)
        for i, (rid, uptime) in enumerate(zip(reading_ids, uptimes)):
            leitura = LeituraTelemetria.objects.get(id=rid)
            expected = ntp_dt - timedelta(milliseconds=(15_000 - uptime))
            self.assertEqual(
                leitura.timestamp,
                expected,
                f"leitura {i} com uptime={uptime} deveria ser reconstruída para {expected}",
            )
            # Ainda unsynced: time_source preservado
            self.assertEqual(leitura.time_source, "unsynced")

    def test_ntp_posterior_preserva_ingested_at(self):
        device = "T5-NTP-POST-02"
        boot_id = str(uuid.uuid4())

        _, rid = registrar_leitura(_payload(device, boot_id, 0, seq=1))
        leitura = LeituraTelemetria.objects.get(id=rid)
        ingested_at_original = leitura.recebido_em

        # Registra âncora NTP
        registrar_leitura(
            _payload(device, boot_id, 10_000, time_source="ntp", timestamp="2026-11-05T10:00:10+00:00", seq=2)
        )

        leitura.refresh_from_db()
        self.assertEqual(
            leitura.recebido_em,
            ingested_at_original,
            "recebido_em não deve ser alterado pela reconstrução temporal",
        )

    def test_historico_rastreavel_apos_sincronizacao_ntp(self):
        """A reconstrução não deve gerar inconsistências na cadeia de leituras."""
        device = "T5-NTP-POST-03"
        boot_id = str(uuid.uuid4())

        # 5 leituras offline com uptime crescente
        for i in range(5):
            registrar_leitura(_payload(device, boot_id, i * 1_000, seq=i + 1))

        # Âncora NTP: uptime 5.000 ms = 10:00:05
        registrar_leitura(
            _payload(device, boot_id, 5_000, time_source="ntp", timestamp="2026-11-05T10:00:05+00:00", seq=6)
        )

        leituras = list(
            LeituraTelemetria.objects.filter(device_id=device, boot_id=boot_id, time_source="unsynced")
            .order_by("uptime_ms")
        )
        self.assertEqual(len(leituras), 5)

        # Verificar que timestamps estão monotonicamente crescentes por uptime
        for a, b in zip(leituras, leituras[1:]):
            self.assertLess(
                a.timestamp,
                b.timestamp,
                f"uptime {a.uptime_ms} deveria ter timestamp menor que uptime {b.uptime_ms}",
            )


# ─────────────────────────────────────────────────────────────────────────────
# Teste 6 — RTC com deriva
# ─────────────────────────────────────────────────────────────────────────────
class TestRTCComDeriva(TestCase):
    """RTC com pequena deriva: confiança reflete incerteza sem precisão artificial."""

    def test_rtc_time_source_configura_confianca_alta(self):
        """Leitura com time_source=rtc tem event_time_confidence=high."""
        device = "T5-RTC-01"
        boot_id = str(uuid.uuid4())
        payload = _payload(
            device, boot_id, 1_000,
            time_source="rtc",
            timestamp="2026-11-05T10:00:01+00:00",
            seq=1,
        )
        s, rid = registrar_leitura(payload)
        self.assertEqual(s, "criado")
        leitura = LeituraTelemetria.objects.get(id=rid)
        self.assertEqual(leitura.time_source, "rtc")
        self.assertEqual(leitura.event_time_confidence, "high")

    def test_rtc_sem_ntp_de_referencia_nao_calcula_clock_skew(self):
        """clock_skew_ms só pode ser fornecido pelo gateway; RTC sem medição externa → null."""
        device = "T5-RTC-02"
        boot_id = str(uuid.uuid4())
        payload = _payload(
            device, boot_id, 0,
            time_source="rtc",
            timestamp="2026-11-05T08:00:00+00:00",
            seq=1,
        )
        # clock_skew_ms sem time_source=gateway deve ser rejeitado
        payload["clock_skew_ms"] = 1200
        s, motivo = registrar_leitura(payload)
        self.assertEqual(s, "invalido")
        self.assertIn("clock_skew_ms", motivo)

    def test_rtc_nao_gera_penalidade_trust_score(self):
        """Leitura RTC não deve receber penalidade de hora não confiável."""
        leitura = SimpleNamespace(
            timestamp=timezone.now(),
            temperatura=72.0,
            vibracao=0.35,
            rpm=1800,
            time_source="rtc",
        )
        _, reasons = calcular_trust_score(leitura, [])
        self.assertFalse(
            any("hora do dispositivo nao confiavel" in r for r in reasons),
            "time_source=rtc não deve gerar penalidade temporal",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Teste 7 — ausência de âncora
# ─────────────────────────────────────────────────────────────────────────────
class TestAusenciaDeAncora(TestCase):
    """Leituras sem âncora válida não recebem event_time reconstruído como confiável."""

    def test_sem_ancora_leitura_unsynced_preserva_uptime_e_ingested_at(self):
        device = "T5-NO-ANCHOR-01"
        boot_id = str(uuid.uuid4())

        s, rid = registrar_leitura(
            _payload(device, boot_id, 3_600_000, seq=1)
        )
        self.assertEqual(s, "criado")
        leitura = LeituraTelemetria.objects.get(id=rid)

        # uptime preservado
        self.assertEqual(leitura.uptime_ms, 3_600_000)
        # boot_id preservado
        self.assertEqual(str(leitura.boot_id), boot_id)
        # time_source preservado
        self.assertEqual(leitura.time_source, "unsynced")
        # event_time_confidence baixa
        self.assertEqual(leitura.event_time_confidence, "low")
        # clock_skew_ms nulo (sem referência externa)
        self.assertIsNone(leitura.clock_skew_ms)
        # Sem âncora: não há DeviceClockAnchor para este boot
        self.assertFalse(
            DeviceClockAnchor.objects.filter(device_id=device, boot_id=boot_id).exists(),
            "sem âncora confiável, DeviceClockAnchor não deve ser criado para unsynced",
        )

    def test_sem_ancora_confianca_temporal_baixa_no_trust_score(self):
        device = "T5-NO-ANCHOR-02"
        boot_id = str(uuid.uuid4())

        s, rid = registrar_leitura(
            _payload(device, boot_id, 0, seq=1)
        )
        self.assertEqual(s, "criado")
        leitura = LeituraTelemetria.objects.get(id=rid)
        self.assertIsNotNone(leitura.trust_score)
        self.assertLess(
            leitura.trust_score, 0.85,
            "trust_score sem âncora e time_source=unsynced deve ser penalizado",
        )

    def test_boots_diferentes_nao_compartilham_ancora(self):
        """Dois boots com âncoras distintas nunca se misturam."""
        device = "T5-NO-ANCHOR-03"
        boot_a = str(uuid.uuid4())
        boot_b = str(uuid.uuid4())

        # Âncora para boot_a
        registrar_leitura(
            _payload(device, boot_a, 0, time_source="ntp", timestamp="2026-11-05T10:00:00+00:00", seq=1)
        )
        # Leitura unsynced em boot_b — sem âncora própria
        s, rid = registrar_leitura(_payload(device, boot_b, 5_000, seq=2))
        self.assertEqual(s, "criado")

        leitura_b = LeituraTelemetria.objects.get(id=rid)
        # A âncora de boot_a não deve ter sido aplicada em boot_b
        self.assertFalse(
            DeviceClockAnchor.objects.filter(device_id=device, boot_id=boot_b).exists(),
            "âncora de boot_a não deve criar âncora para boot_b",
        )
        # Timestamp de boot_b não deve ser em torno de 10:00 (âncora de boot_a)
        from django.utils.dateparse import parse_datetime
        anchor_a_time = parse_datetime("2026-11-05T10:00:00+00:00")
        delta = abs((leitura_b.timestamp - anchor_a_time).total_seconds())
        self.assertGreater(
            delta, 60,
            "leitura de boot_b não deve usar âncora de boot_a para reconstrução",
        )
