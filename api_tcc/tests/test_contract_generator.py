import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from scripts import generate_classification_fixtures


class ContractFixtureGeneratorTests(SimpleTestCase):
    def test_check_mode_detects_stale_fixture_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            stale_path = Path(directory) / "classificacao.json"
            stale_contents = "[]\n"
            stale_path.write_text(stale_contents, encoding="utf-8")
            with (
                patch.object(generate_classification_fixtures, "FIXTURE_PATH", stale_path),
                patch.object(sys, "argv", ["generate_classification_fixtures.py", "--check"]),
            ):
                self.assertEqual(generate_classification_fixtures.main(), 1)
            self.assertEqual(stale_path.read_text(encoding="utf-8"), stale_contents)

    def test_generation_is_deterministic(self):
        contract = json.loads(
            generate_classification_fixtures.CONTRACT_PATH.read_text(encoding="utf-8")
        )
        self.assertEqual(
            generate_classification_fixtures.generate(contract),
            generate_classification_fixtures.generate(contract),
        )
