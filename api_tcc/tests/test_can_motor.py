from datetime import timedelta
import random

from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from api_tcc.ia.prescricao_motor import gerar_prescricoes
from api_tcc.models import DTCMotor, LeituraCANMotor, Machine
from api_tcc.services.can_motor import (
    estimar_horas_ate_limite,
    resumir_qualidade,
    validar_leitura,
)
from canmotor import gerar_leitura, simular


def leitura(maquina="CAN-01", **overrides):
    dados = {
        "maquina_id": maquina,
        "timestamp": timezone.now(),
        "rpm": 1500,
        "carga_pct": 45,
        "horimetro_h": 1200,
        "oleo_pressao_kpa": 340,
        "oleo_temp_c": 95,
        "oleo_nivel_pct": 75,
        "liquido_temp_c": 88,
        "liquido_nivel_pct": 85,
        "rail_pressao_kpa": 150000,
        "combustivel_temp_c": 45,
        "consumo_lh": 30,
        "turbo_pressao_kpa": 210,
        "escape_temp_c": 500,
        "bateria_v": 13.8,
        "simulado": True,
    }
    dados.update(overrides)
    return LeituraCANMotor.objects.create(**dados)


class QualidadeCANMotorTest(TestCase):
    def test_leitura_fora_de_faixa_e_contabilizada_como_descartada(self):
        leitura(bateria_v=55)
        leitura(maquina="CAN-02")
        qualidade = resumir_qualidade("CAN-01")
        self.assertEqual(qualidade["recebidas"], 1)
        self.assertEqual(qualidade["aceitas"], 0)
        self.assertEqual(qualidade["descartadas"], 1)
        self.assertEqual(qualidade["motivos"]["bateria_v_fora_faixa_fisica"], 1)

    def test_sinal_congelado_e_detectado(self):
        base = timezone.now()
        anteriores = []
        for n in range(4):
            anteriores.append(LeituraCANMotor(
                maquina_id="CAN-01", timestamp=base + timedelta(seconds=n),
                rpm=1500, oleo_pressao_kpa=340, liquido_temp_c=88,
            ))
        atual = LeituraCANMotor(
            maquina_id="CAN-01", timestamp=base + timedelta(seconds=4),
            rpm=1500, oleo_pressao_kpa=340, liquido_temp_c=88,
        )
        resultado = validar_leitura(atual, anteriores)
        self.assertFalse(resultado["valida"])
        self.assertIn("rpm", resultado["sinais_congelados"])

    def test_leitura_parcial_informa_campos_ausentes_sem_descartar(self):
        registro = LeituraCANMotor(maquina_id="CAN-01", timestamp=timezone.now(), rpm=1200)
        resultado = validar_leitura(registro)
        self.assertTrue(resultado["valida"])
        self.assertIn("oleo_pressao_kpa", resultado["campos_ausentes"])

    def test_duplicidade_maquina_timestamp_e_impedida_no_banco(self):
        registro = leitura()
        with self.assertRaises(IntegrityError), transaction.atomic():
            leitura(timestamp=registro.timestamp)

    def test_fmi_fora_do_intervalo_j1939_e_rejeitado(self):
        agora = timezone.now()
        with self.assertRaises(IntegrityError), transaction.atomic():
            DTCMotor.objects.create(
                maquina_id="CAN-01", spn=100, fmi=32, ocorrencias=1,
                ativo=True, simulado=True, primeira_vez=agora, ultima_vez=agora,
            )


class PrescricaoCANMotorTest(TestCase):
    def test_pressao_baixa_e_temperatura_alta_geram_criticidade(self):
        registro = leitura(
            oleo_pressao_kpa=90,
            oleo_temp_c=135,
            oleo_nivel_pct=70,
        )
        resultado = gerar_prescricoes([registro])
        lubrificacao = next(item for item in resultado if item["subsistema"] == "lubrificacao")
        self.assertEqual(lubrificacao["status"], "CRITICO")
        self.assertEqual(lubrificacao["dtcs_relacionados"][0]["spn"], 100)
        self.assertEqual(lubrificacao["evidencia_nivel"], "MEDIA")
        self.assertEqual(lubrificacao["limite_referencia"]["valor"], 120)
        self.assertEqual(lubrificacao["prazo"], "Imediata")
        self.assertEqual(DTCMotor.objects.count(), 0, "GET/regra não deve persistir DTC")

    def test_estimativa_sem_tendencia_retorna_null_e_motivo(self):
        atual = leitura()
        estimativa, motivo = estimar_horas_ate_limite(
            atual, [atual], "oleo_pressao_kpa", 120, "baixo"
        )
        self.assertIsNone(estimativa)
        self.assertIn("12 observações", motivo)

    def test_evidencia_isolada_nao_produz_conclusao_forte(self):
        registro = leitura(liquido_temp_c=108, liquido_nivel_pct=85)
        resultado = gerar_prescricoes([registro])
        arrefecimento = next(item for item in resultado if item["subsistema"] == "arrefecimento")
        self.assertEqual(arrefecimento["status"], "ATENCAO")
        self.assertEqual(arrefecimento["evidencia_nivel"], "BAIXA")
        self.assertIn("baixa", arrefecimento["diagnostico"])


class SimuladorCANMotorTest(TestCase):
    def test_cenarios_degradam_sinais_correlacionados_progressivamente(self):
        inicio = timezone.now()
        relacoes = {
            "arrefecimento": ("liquido_temp_c", "liquido_nivel_pct", 1),
            "lubrificacao": ("oleo_pressao_kpa", "oleo_temp_c", -1),
            "combustivel": ("rail_pressao_kpa", "consumo_lh", -1),
            "admissao": ("turbo_pressao_kpa", "escape_temp_c", -1),
        }
        for cenario, (primeiro, segundo, sinal) in relacoes.items():
            normal = gerar_leitura("CAN-01", cenario, 0, inicio, random.Random(7), 40, 5)
            critica = gerar_leitura("CAN-01", cenario, 1, inicio, random.Random(7), 40, 5)
            if sinal > 0:
                self.assertGreater(critica[primeiro], normal[primeiro], cenario)
                self.assertLess(critica[segundo], normal[segundo], cenario)
            else:
                self.assertLess(critica[primeiro], normal[primeiro], cenario)
                self.assertGreater(critica[segundo], normal[segundo], cenario)
            self.assertTrue(critica["simulado"])

    def test_simulador_gera_dtc_simulado_correspondente_ao_cenario(self):
        simular(maquina="CAN-SIM-01", cenario="lubrificacao", intervalo=0.001, duracao=0.0001)
        dtc = DTCMotor.objects.get(maquina_id="CAN-SIM-01", ativo=True)
        self.assertEqual((dtc.spn, dtc.fmi), (100, 1))
        self.assertTrue(dtc.simulado)
        self.assertGreaterEqual(dtc.ocorrencias, 1)
        primeira_vez = dtc.ultima_vez
        simular(maquina="CAN-SIM-01", cenario="lubrificacao", intervalo=0.001, duracao=0.0001)
        dtc.refresh_from_db()
        self.assertGreaterEqual(dtc.ocorrencias, 2)
        self.assertGreater(dtc.ultima_vez, primeira_vez)


@override_settings(DEMO_MODE=True)
class EndpointCANMotorTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.m1 = Machine.objects.create(external_code="CAN-01", is_demo=True)
        self.m2 = Machine.objects.create(external_code="CAN-02", is_demo=True)

    def test_endpoint_sem_maquina_id_retorna_400(self):
        response = self.client.get("/api/can/motor/")
        self.assertEqual(response.status_code, 400)

    def test_endpoint_retorna_somente_maquina_solicitada_e_em_ordem(self):
        agora = timezone.now()
        leitura(maquina="CAN-01", timestamp=agora + timedelta(seconds=2))
        leitura(maquina="CAN-01", timestamp=agora)
        leitura(maquina="CAN-02", timestamp=agora + timedelta(seconds=1))
        response = self.client.get("/api/can/motor/?maquina_id=CAN-01")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["serie"]), 2)
        self.assertTrue(all(item["maquina_id"] == "CAN-01" for item in response.data["serie"]))
        self.assertEqual(
            [item["timestamp"] for item in response.data["serie"]],
            sorted(item["timestamp"] for item in response.data["serie"]),
        )
        self.assertTrue(response.data["simulado"])
        self.assertEqual(response.data["origem_dados"], "SIMULADO")
        self.assertEqual(response.data["qualidade"]["aceitas"], 2)
        self.assertIn("prescricoes", response.data)

    def test_dtc_ativo_retorna_campos_e_origem_simulada(self):
        agora = timezone.now()
        DTCMotor.objects.create(
            maquina_id="CAN-01", spn=100, fmi=1, ocorrencias=2, ativo=True,
            simulado=True, primeira_vez=agora - timedelta(minutes=1), ultima_vez=agora,
        )
        response = self.client.get("/api/can/motor/?maquina_id=CAN-01")
        self.assertEqual(response.data["dtcs_ativos"][0]["spn"], 100)
        self.assertEqual(response.data["dtcs_ativos"][0]["ocorrencias"], 2)
        self.assertEqual(response.data["dtcs_ativos"][0]["subsistema"], "lubrificacao")
        self.assertTrue(response.data["dtcs_ativos"][0]["simulado"])

    def test_maquina_ausente_no_dataset_demo_nao_expoe_telemetria(self):
        response = self.client.get("/api/can/motor/?maquina_id=NAO-EXISTE")
        self.assertEqual(response.status_code, 404)
