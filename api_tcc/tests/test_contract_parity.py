import json
from pathlib import Path

from django.test import SimpleTestCase

from api_tcc.contracts import ContractError, classify, classify_combined, severity_contract, transmission_class
from simulators.edge_client import classify_priority


FIXTURE_PATH = Path(__file__).resolve().parents[2] / "contracts" / "fixtures" / "classificacao.json"
FIXTURES = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


class ContractParityTests(SimpleTestCase):
    def test_backend_and_edge_match_golden_cases(self):
        for case in FIXTURES:
            with self.subTest(case_id=case["id"]):
                if case.get("expected_error") == "range":
                    metric = "temperatura" if case["id"].startswith("temperatura_") else "vibracao"
                    with self.assertRaises(ContractError, msg=f"backend aceitou {case['id']}"):
                        classify(metric, case[metric])
                    with self.assertRaises(ContractError, msg=f"edge aceitou {case['id']}"):
                        classify_priority(case)
                    continue

                self.assertIn(case["vibracao_unit"], severity_contract()["metrics"]["vibracao"]["allowed_units"])

                temperature_severity = classify("temperatura", case["temperatura"])
                vibration_severity = classify("vibracao", case["vibracao"])
                self.assertEqual(
                    case["severidade_temperatura"], temperature_severity,
                    f"backend temperatura: esperado={case['severidade_temperatura']} obtido={temperature_severity}",
                )
                self.assertEqual(
                    case["severidade_vibracao"], vibration_severity,
                    f"backend vibração: esperado={case['severidade_vibracao']} obtido={vibration_severity}",
                )
                severity = classify_combined([temperature_severity, vibration_severity])
                self.assertEqual(
                    case["severidade"], severity,
                    f"backend consolidada: esperado={case['severidade']} obtido={severity}",
                )
                backend_class = transmission_class(
                    severity, case["evidence_quality"], case["atrasado"]
                )
                edge_class = classify_priority(case)
                self.assertEqual(
                    case["classe"], backend_class,
                    f"backend transmissão: esperado={case['classe']} obtido={backend_class}",
                )
                self.assertEqual(
                    case["classe"], edge_class,
                    f"edge transmissão: esperado={case['classe']} obtido={edge_class}",
                )

    def test_golden_comparison_detects_a_deliberate_backend_divergence(self):
        from unittest.mock import patch

        case = next(item for item in FIXTURES if item["id"] == "temperatura_critico_limite")
        with patch("api_tcc.tests.test_contract_parity.classify", return_value="NORMAL"):
            actual = classify("temperatura", case["temperatura"])
        self.assertNotEqual(case["severidade_temperatura"], actual)
