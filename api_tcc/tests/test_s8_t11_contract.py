import math

from django.test import SimpleTestCase

from api_tcc.services.telemetria import validar_payload


class S8T11ContractTests(SimpleTestCase):
    def payload(self):
        return {
            "maquina_id": "bench-01",
            "temperatura": 70.0,
            "vibracao": 0.4,
            "time_source": "unsynced",
        }

    def test_rpm_ausente_continua_ausente(self):
        valido, motivo = validar_payload(self.payload())
        self.assertTrue(valido, motivo)
        self.assertNotIn("rpm", self.payload())

    def test_gps_valido_e_velocidade_zero_sao_aceitos(self):
        payload = self.payload() | {
            "rpm": 1200,
            "gps_fix": True,
            "gps_hdop": 1.1,
            "latitude": -23.5,
            "longitude": -46.6,
            "velocidade_kmh": 0.0,
        }
        self.assertEqual(validar_payload(payload), (True, ""))

    def test_hdop_nan_e_coordenada_sem_fix_sao_rejeitados(self):
        payload = self.payload() | {"gps_hdop": math.nan}
        self.assertFalse(validar_payload(payload)[0])
        payload = self.payload() | {
            "gps_fix": False,
            "latitude": -23.5,
            "longitude": -46.6,
        }
        self.assertFalse(validar_payload(payload)[0])
