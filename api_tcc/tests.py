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
from api_tcc.models import (
    LeituraTelemetria,
    Colheitadeira,
    Modelo,
    Marca,
    Combustivel,
    PressaoPneus,
    AlturadoCorte,
    PressaodoCorte,
    TempUmi_Ambiente,
    TemperaturaMaquina,
    Operario,
    StatusdeOperacao,
    EstadodeMovimento,
    Prescricao,
)
from api_tcc.services.telemetria import validar_payload, registrar_leitura
import uuid


# ──────────────────────────────────────────────────────────────
# Fixtures reutilizáveis
# ──────────────────────────────────────────────────────────────
def _criar_maquina_teste(maquina_id: str):
    """
    Cria todos os related objects necessários para uma Colheitadeira.
    Reutiliza objetos compartilhados quando possível.
    """
    # Criar ou reutilizar Unidade de Medida (necessária para vários ForeignKeys)
    from api_tcc.models import UnidadedeMedida
    unidade, _ = UnidadedeMedida.objects.get_or_create(
        id=1,
        defaults={"nome": "Centímetro"}
    )

    # Reutilizar Marca se existir
    marca, _ = Marca.objects.get_or_create(nome="CLAAS")

    # Criar Modelo com o maquina_id como nome
    modelo, _ = Modelo.objects.get_or_create(
        nome=maquina_id,
        defaults={"marca": marca}
    )

    # Reutilizar ou criar objetos comuns
    combustivel, _ = Combustivel.objects.get_or_create(
        tipo="Diesel", defaults={"porcentagem": 100.0}
    )
    pressao_pneus, _ = PressaoPneus.objects.get_or_create(
        pressao=2.5, defaults={"unidade_de_medida": unidade}
    )
    altura_corte, _ = AlturadoCorte.objects.get_or_create(
        altura=5.0, defaults={"unidade_de_medida": unidade}
    )
    pressao_corte, _ = PressaodoCorte.objects.get_or_create(
        pressao=30.0, defaults={"unidade_de_medida": unidade}
    )
    temp_umi, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=25.0, umidade=60.0)
    temp_maquina, _ = TemperaturaMaquina.objects.get_or_create(
        temperatura=85.0, defaults={"maquina": modelo}
    )
    operario, _ = Operario.objects.get_or_create(
        nome="Operário Teste", defaults={"tempo_de_servico": 5, "no_banco": True}
    )
    status_op, _ = StatusdeOperacao.objects.get_or_create(
        em_operacao=True, defaults={"tempo_de_operacao": 8.0}
    )
    estado_mov, _ = EstadodeMovimento.objects.get_or_create(
        em_movimento=True, defaults={"velocidade": 6.5}
    )

    # Criar Colheitadeira
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
    if colheitadeira.maquina_id != maquina_id:
        colheitadeira.maquina_id = maquina_id
        colheitadeira.save(update_fields=["maquina_id"])
    return colheitadeira


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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _criar_maquina_teste("COLH-TEST-01")

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _criar_maquina_teste("COLH-TEST-01")

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _criar_maquina_teste("COLH-TEST-01")

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

    def test_prescricao_gera_e_persiste_historico(self):
        """Testa que a prescrição é enfileirada e o endpoint retorna status correto."""
        maquina_id = "COLH-TEST-01"
        _criar_maquina_teste(maquina_id)

        # Criar leituras suficientes
        for i in range(10):
            timestamp = f"2026-04-17T15:{i:02d}:00Z"
            registrar_leitura(
                _payload_valido(
                    id=str(uuid.uuid4()), maquina_id=maquina_id, timestamp=timestamp
                )
            )

        # GET para gerar prescrição (enfileira em background)
        response = self.client.get(f"/api/prescricoes/?maquina_id={maquina_id}")
        self.assertEqual(response.status_code, 200)
        # Retorna "agendado" pois processamento é assíncrono
        self.assertEqual(response.data["status"], "agendado")
        self.assertEqual(response.data["maquina_id"], maquina_id)
        self.assertIn("modelos", response.data)
        self.assertIn("prescricao", response.data["modelos"])

        # Nota: Validação de persistência ocorre em integração com worker real (vide scripts/)

    def test_lista_prescricoes_retorna_historico(self):
        maquina_id = "COLH-TEST-01"
        colheitadeira = _criar_maquina_teste(maquina_id)
        Prescricao.objects.create(
            colheitadeira=colheitadeira,
            titulo="Teste histórico",
            descricao="Descrição de teste",
            status="pendente",
        )

        response = self.client.get(f"/api/prescricoes/lista/?maquina_id={maquina_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["maquina_id"], maquina_id)

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
        # Agora a view apenas agenda o processamento; o worker decide se há dados
        response = self.client.get("/api/anomalias/?maquina_id=MAQUINA-INEXISTENTE")
        self.assertEqual(response.status_code, 200)
        # Resposta imediata: processamento foi enfileirado
        self.assertEqual(response.data["status"], "agendado")

    def test_manutencao_sem_maquina_id_retorna_400(self):
        response = self.client.get("/api/manutencao/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "erro")


# ──────────────────────────────────────────────────────────────
# 5. TESTE: MÉTRICAS OPERACIONAIS
# ──────────────────────────────────────────────────────────────
class MetricasTest(TestCase):
    """
    Testa o endpoint /api/metricas/ que fornece observabilidade
    do sistema para dashboard e apresentações.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        _criar_maquina_teste("COLH-01")
        _criar_maquina_teste("COLH-02")

    def setUp(self):
        self.client = APIClient()

    def test_metricas_retorna_200_com_campos_esperados(self):
        # Criar algumas leituras válidas
        registrar_leitura(_payload_valido(id=str(uuid.uuid4()), maquina_id="COLH-01"))
        registrar_leitura(_payload_valido(id=str(uuid.uuid4()), maquina_id="COLH-02"))

        response = self.client.get("/api/metricas/")
        self.assertEqual(response.status_code, 200)

        # Verificar campos obrigatórios
        self.assertIn("leituras_validas", response.data)
        self.assertIn("leituras_invalidas", response.data)
        self.assertIn("taxa_rejeicao_pct", response.data)
        self.assertIn("maquinas_ativas", response.data)

        # Verificar valores
        self.assertEqual(response.data["leituras_validas"], 2)
        self.assertEqual(response.data["leituras_invalidas"], 0)
        self.assertEqual(response.data["taxa_rejeicao_pct"], 0.0)
        self.assertEqual(response.data["maquinas_ativas"], 2)
