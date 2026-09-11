"""
api_tcc/tests/test_identity_contract.py
S1-T5 — Testes do Contrato de Identidade e Sincronização da Telemetria

Cobertura:
- TestIdempotenciaComposta   : (device_id, message_id) como chave única
- TestCursorMonotonico       : last_acked_sequence nunca retrocede
- TestDispositivosDiferentes : device-A + msg-X ≠ device-B + msg-X
- TestMensagensDiferentes    : device-A + msg-X ≠ device-A + msg-Y
- TestReplayNaoRetrocedeCursor : replay não avança nem retrocede cursor
- TestCompatibilidadeLegada  : payload sem device_id/message_id usa fallbacks
- TestPrimeiroCursor         : primeiro evento cria SyncCursor corretamente
- TestConcorrencia           : constraint de banco protege contra race condition
- TestCamposNovas            : novos campos persistidos corretamente
"""
import uuid

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import LeituraTelemetria, Machine, SyncCursor
from api_tcc.services.telemetria import (
    _atualizar_sync_cursor,
    registrar_leitura,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _payload_base(**overrides) -> dict:
    """Payload mínimo válido com device_id e message_id explícitos."""
    base = {
        "maquina_id":   "COLH-S1T5",
        "device_id":    "esp32-s1t5",
        "message_id":   f"msg-{uuid.uuid4()}",
        "sequence_number": 1,
        "temperatura":  80.0,
        "vibracao":     0.5,
        "rpm":          1800,
        "timestamp":    "2026-09-11T10:00:00Z",
        "schema_version": "1.0",
    }
    base.update(overrides)
    return base


def _registrar_cinco_replays(device_id: str, message_id: str) -> list[tuple]:
    """
    Registra 5 tentativas do mesmo (device_id, message_id) com UUIDs diferentes.
    Retorna lista de (status, id_retornado).
    """
    resultados = []
    for _ in range(5):
        payload = _payload_base(
            device_id=device_id,
            message_id=message_id,
            id=str(uuid.uuid4()),   # UUID diferente a cada tentativa
        )
        resultado = registrar_leitura(payload)
        resultados.append(resultado)
    return resultados


# ---------------------------------------------------------------------------
# TESTE 1 — Idempotência composta: 5 UUIDs → 1 leitura
# ---------------------------------------------------------------------------

class TestIdempotenciaComposta(TestCase):
    """
    Invariante principal: (device_id, message_id) idênticos com UUIDs diferentes
    devem resultar em exatamente 1 linha no banco.

    5 tentativas com UUIDs distintos = 1 LeituraTelemetria.
    """

    def test_cinco_uuids_diferentes_geram_uma_leitura(self):
        """
        Cenário do bloco S1-T5:
        tentativa 1: id=UUID-A, device_id=esp32-01, message_id=msg-100
        tentativa 2: id=UUID-B, device_id=esp32-01, message_id=msg-100
        ...
        tentativa 5: id=UUID-E, device_id=esp32-01, message_id=msg-100

        Resultado: count(LeituraTelemetria) == 1
        """
        device_id  = "ESP32-01"
        message_id = "msg-100"

        resultados = _registrar_cinco_replays(device_id, message_id)

        # Exatamente 1 leitura no banco
        self.assertEqual(
            LeituraTelemetria.objects.count(), 1,
            "5 replays com UUIDs diferentes devem gerar exatamente 1 leitura.",
        )

        # Primeiro resultado: "criado"
        self.assertEqual(resultados[0][0], "criado")

        # Demais resultados: "duplicata"
        for status, _ in resultados[1:]:
            self.assertEqual(
                status, "duplicata",
                f"Replay com UUID diferente deveria retornar 'duplicata', não '{status}'.",
            )

        # Todos os IDs retornados apontam para a mesma leitura
        ids_retornados = {r[1] for r in resultados}
        self.assertEqual(
            len(ids_retornados), 1,
            "Todos os 5 retornos devem apontar para o mesmo id de leitura.",
        )

    def test_uuid_diferente_nao_burla_idempotencia(self):
        """UUID da linha não é a chave de idempotência."""
        device_id  = "ESP32-IDEM"
        message_id = "msg-idem-999"

        # Primeira inserção
        s1, id1 = registrar_leitura(_payload_base(
            device_id=device_id, message_id=message_id, id=str(uuid.uuid4()),
        ))
        self.assertEqual(s1, "criado")

        # Segunda tentativa com UUID completamente diferente
        s2, id2 = registrar_leitura(_payload_base(
            device_id=device_id, message_id=message_id, id=str(uuid.uuid4()),
        ))
        self.assertEqual(s2, "duplicata", "UUID diferente não deve burlar idempotência.")
        self.assertEqual(id1, id2, "Ambos devem referenciar a mesma leitura.")
        self.assertEqual(LeituraTelemetria.objects.count(), 1)

    def test_constraint_banco_unica_existe(self):
        """
        Verificar que a constraint unique_together está ativa no banco.
        Inserção direta via ORM deve levantar IntegrityError.
        """
        agora = timezone.now()
        Machine.objects.get_or_create(external_code="TESTE-CONSTRAINT")

        # Primeira inserção direta
        LeituraTelemetria.objects.create(
            device_id="CONSTR-DEV",
            message_id="CONSTR-MSG",
            maquina_id="TESTE-CONSTRAINT",
            temperatura=80.0,
            vibracao=0.5,
            rpm=1800,
            timestamp=agora,
        )

        # Segunda inserção com mesmo (device_id, message_id) → IntegrityError
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                LeituraTelemetria.objects.create(
                    device_id="CONSTR-DEV",
                    message_id="CONSTR-MSG",
                    maquina_id="TESTE-CONSTRAINT",
                    temperatura=85.0,
                    vibracao=0.6,
                    rpm=1900,
                    timestamp=agora,
                )


# ---------------------------------------------------------------------------
# TESTE 2 — Cursor monotônico: 10 → 11 → 15 → 12 → 20 = 20 final
# ---------------------------------------------------------------------------

class TestCursorMonotonico(TestCase):
    """
    Invariante: last_acked_sequence nunca retrocede.

    Sequência: 11, 15, 12, 20 (cursor começa em 10)
    Esperado:  11, 15, 15, 20  (sem retrocesso)
    """

    DEVICE = "CURSOR-DEV-01"

    def _cursor_seq(self) -> int:
        """Retorna last_acked_sequence atual do cursor."""
        return SyncCursor.objects.get(device_id=self.DEVICE).last_acked_sequence

    def test_cursor_monotônico_sequência_exata(self):
        """
        Estado inicial: cursor = 10
        Chega 11 → cursor = 11
        Chega 15 → cursor = 15
        Chega 12 → cursor = 15 (não retrocede)
        Chega 20 → cursor = 20
        """
        # Criar cursor com sequência inicial 10
        SyncCursor.objects.create(device_id=self.DEVICE, last_acked_sequence=10)
        self.assertEqual(self._cursor_seq(), 10)

        _atualizar_sync_cursor(self.DEVICE, 11)
        self.assertEqual(self._cursor_seq(), 11, "Após seq=11, cursor deve ser 11.")

        _atualizar_sync_cursor(self.DEVICE, 15)
        self.assertEqual(self._cursor_seq(), 15, "Após seq=15, cursor deve ser 15.")

        _atualizar_sync_cursor(self.DEVICE, 12)
        self.assertEqual(self._cursor_seq(), 15, "seq=12 não deve retroceder cursor=15.")

        _atualizar_sync_cursor(self.DEVICE, 20)
        self.assertEqual(self._cursor_seq(), 20, "Após seq=20, cursor deve ser 20.")

    def test_cursor_nao_retrocede_em_nenhum_momento(self):
        """Em nenhum ponto intermediário o cursor pode ser menor que o máximo já visto."""
        SyncCursor.objects.create(device_id=self.DEVICE, last_acked_sequence=10)
        max_visto = 10

        for seq in [11, 15, 12, 20]:
            _atualizar_sync_cursor(self.DEVICE, seq)
            max_visto = max(max_visto, seq)
            atual = self._cursor_seq()
            self.assertGreaterEqual(
                atual, max_visto,
                f"Cursor ({atual}) não pode ser menor que máximo já visto ({max_visto}) após seq={seq}.",
            )

    def test_cursor_resultado_final_e_20(self):
        """Verificação direta: resultado final após sequência 11, 15, 12, 20 deve ser 20."""
        SyncCursor.objects.create(device_id=self.DEVICE, last_acked_sequence=10)
        for seq in [11, 15, 12, 20]:
            _atualizar_sync_cursor(self.DEVICE, seq)
        self.assertEqual(self._cursor_seq(), 20)


# ---------------------------------------------------------------------------
# Testes adicionais recomendados
# ---------------------------------------------------------------------------

class TestDispositivosDiferentes(TestCase):
    """device-A + msg-X e device-B + msg-X são eventos distintos."""

    def test_mesmo_message_id_dispositivos_diferentes_geram_duas_leituras(self):
        message_id = "msg-shared-001"
        registrar_leitura(_payload_base(device_id="DEVICE-A", message_id=message_id))
        registrar_leitura(_payload_base(device_id="DEVICE-B", message_id=message_id))
        self.assertEqual(LeituraTelemetria.objects.count(), 2)

    def test_cursores_de_dispositivos_diferentes_sao_independentes(self):
        registrar_leitura(_payload_base(device_id="DEV-X", message_id="m1", sequence_number=5))
        registrar_leitura(_payload_base(device_id="DEV-Y", message_id="m2", sequence_number=100))
        self.assertEqual(SyncCursor.objects.get(device_id="DEV-X").last_acked_sequence, 5)
        self.assertEqual(SyncCursor.objects.get(device_id="DEV-Y").last_acked_sequence, 100)


class TestMensagensDiferentes(TestCase):
    """device-A + msg-X e device-A + msg-Y são eventos distintos."""

    def test_mesmo_device_mensagens_diferentes_geram_duas_leituras(self):
        registrar_leitura(_payload_base(device_id="DEVICE-A", message_id="msg-X"))
        registrar_leitura(_payload_base(
            device_id="DEVICE-A", message_id="msg-Y",
            timestamp="2026-09-11T10:01:00Z",
        ))
        self.assertEqual(LeituraTelemetria.objects.count(), 2)


class TestReplayNaoRetrocedeCursor(TestCase):
    """
    Um replay de mensagem já processada:
    - não deve criar nova linha
    - não deve retroceder o cursor
    """

    DEVICE = "REPLAY-DEV"

    def test_replay_nao_retrocede_cursor(self):
        # Mensagem 1: seq=5 → cursor = 5
        registrar_leitura(_payload_base(device_id=self.DEVICE, message_id="msg-1", sequence_number=5))
        self.assertEqual(SyncCursor.objects.get(device_id=self.DEVICE).last_acked_sequence, 5)

        # Mensagem 2: seq=10 → cursor = 10
        registrar_leitura(_payload_base(
            device_id=self.DEVICE, message_id="msg-2", sequence_number=10,
            timestamp="2026-09-11T10:01:00Z",
        ))
        self.assertEqual(SyncCursor.objects.get(device_id=self.DEVICE).last_acked_sequence, 10)

        # Replay da mensagem 1 (seq=5) → cursor deve permanecer em 10
        status, _ = registrar_leitura(_payload_base(
            device_id=self.DEVICE, message_id="msg-1", sequence_number=5,
        ))
        self.assertEqual(status, "duplicata", "Replay deve retornar 'duplicata'.")
        self.assertEqual(
            SyncCursor.objects.get(device_id=self.DEVICE).last_acked_sequence, 10,
            "Cursor não deve retroceder de 10 para 5 por causa de replay.",
        )


class TestCompatibilidadeLegada(TestCase):
    """
    Payload legado sem device_id/message_id deve usar fallbacks.
    Os simuladores existentes NÃO podem ser quebrados.
    """

    def test_payload_sem_device_id_usa_maquina_id_como_fallback(self):
        """Quando device_id ausente, device_id ← maquina_id.strip().upper()"""
        payload = {
            "maquina_id": " colh-legado-01 ",
            "temperatura": 75.0,
            "vibracao": 0.4,
            "rpm": 1700,
            "timestamp": "2026-09-11T10:00:00Z",
            # Sem device_id, sem message_id
        }
        status, _ = registrar_leitura(payload)
        self.assertEqual(status, "criado")

        leitura = LeituraTelemetria.objects.get()
        self.assertEqual(leitura.device_id, "COLH-LEGADO-01")
        self.assertIsNotNone(leitura.message_id)  # UUID gerado automaticamente

    def test_payload_sem_message_id_nao_e_idempotente(self):
        """
        Sem message_id, cada envio gera um UUID diferente → NÃO idempotente.
        Isso é comportamento intencional e documentado para simuladores legados.
        """
        payload_base = {
            "maquina_id": "COLH-LEGADO-02",
            "temperatura": 75.0,
            "vibracao": 0.4,
            "rpm": 1700,
            "timestamp": "2026-09-11T10:00:00Z",
        }
        registrar_leitura(dict(payload_base))
        registrar_leitura(dict(payload_base))  # segundo envio sem message_id
        # Dois envios sem message_id → 2 linhas (NÃO idempotente — comportamento documentado)
        self.assertEqual(LeituraTelemetria.objects.count(), 2)

    def test_simulador_adicionar_telemetrias_funciona(self):
        """Simula exatamente o comportamento de scripts/adicionar_telemetrias.py"""
        import uuid as uuid_mod
        from django.utils import timezone

        LeituraTelemetria.objects.create(
            id=uuid_mod.uuid4(),
            maquina_id="COLH-01",
            device_id="COLH-01",          # seria populado pelo serviço
            message_id=str(uuid_mod.uuid4()),
            temperatura=78.5,
            vibracao=0.42,
            rpm=1850,
            timestamp=timezone.now(),
        )
        self.assertEqual(LeituraTelemetria.objects.count(), 1)


class TestPrimeiroCursor(TestCase):
    """Primeiro evento de um device_id deve criar SyncCursor do zero."""

    def test_primeiro_evento_cria_sync_cursor(self):
        device_id = "NOVO-DEV-CURSOR"
        self.assertEqual(SyncCursor.objects.filter(device_id=device_id).count(), 0)

        registrar_leitura(_payload_base(
            device_id=device_id, message_id="msg-first", sequence_number=42,
        ))

        cursor = SyncCursor.objects.get(device_id=device_id)
        self.assertEqual(cursor.last_acked_sequence, 42)

    def test_payload_legado_sem_sequence_nao_cria_ack_falso(self):
        payload = _payload_base(
            device_id="LEGADO-SEM-SEQUENCIA",
            message_id="msg-legada-001",
        )
        payload.pop("sequence_number")

        status, _ = registrar_leitura(payload)

        self.assertEqual(status, "criado")
        leitura = LeituraTelemetria.objects.get(device_id="LEGADO-SEM-SEQUENCIA")
        self.assertEqual(leitura.sequence_number, 0)
        self.assertFalse(
            SyncCursor.objects.filter(device_id="LEGADO-SEM-SEQUENCIA").exists()
        )

    def test_sequence_zero_explicito_cria_cursor(self):
        registrar_leitura(_payload_base(
            device_id="EXPLICITO-ZERO",
            message_id="msg-zero-001",
            sequence_number=0,
        ))

        self.assertEqual(
            SyncCursor.objects.get(device_id="EXPLICITO-ZERO").last_acked_sequence,
            0,
        )

    def test_cursor_device_id_e_unico(self):
        """device_id é UNIQUE em SyncCursor — duplicata levanta IntegrityError."""
        SyncCursor.objects.create(device_id="UNIQUE-DEV", last_acked_sequence=0)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SyncCursor.objects.create(device_id="UNIQUE-DEV", last_acked_sequence=1)


class TestCursorForaDeOrdem(TestCase):
    """Eventos fora de ordem não devem retroceder o cursor."""

    DEVICE = "FORA-ORDEM-DEV"

    def test_sequencia_fora_de_ordem_nao_retrocede(self):
        SyncCursor.objects.create(device_id=self.DEVICE, last_acked_sequence=15)
        _atualizar_sync_cursor(self.DEVICE, 12)  # fora de ordem
        self.assertEqual(
            SyncCursor.objects.get(device_id=self.DEVICE).last_acked_sequence,
            15,
            "seq=12 chegando após cursor=15 não deve retroceder.",
        )


class TestCamposNovosPersistidos(TestCase):
    """Novos campos S1-T5 são persistidos corretamente no banco."""

    def test_campos_identidade_persistidos(self):
        status, id_str = registrar_leitura(_payload_base(
            device_id="DEVICE-CAMPOS",
            message_id="msg-campos-001",
            sequence_number=77,
            source="mqtt",
            transport="mqtt",
        ))
        self.assertEqual(status, "criado")

        leitura = LeituraTelemetria.objects.get(id=id_str)
        self.assertEqual(leitura.device_id, "DEVICE-CAMPOS")
        self.assertEqual(leitura.message_id, "msg-campos-001")
        self.assertEqual(leitura.sequence_number, 77)
        self.assertEqual(leitura.source, "mqtt")
        self.assertEqual(leitura.transport, "mqtt")
        self.assertEqual(leitura.sync_status, "sincronizado")
        self.assertIsNotNone(leitura.payload_hash)
        self.assertEqual(len(leitura.payload_hash), 64)  # SHA-256 hex = 64 chars

    def test_sync_status_default_e_sincronizado(self):
        registrar_leitura(_payload_base(device_id="DEV-STATUS", message_id="msg-status"))
        leitura = LeituraTelemetria.objects.get()
        self.assertEqual(leitura.sync_status, "sincronizado")
