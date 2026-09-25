import uuid
import numpy as np
from unittest.mock import patch, MagicMock
from django.test import TransactionTestCase

from api_tcc.models import Machine, LeituraTelemetria
from api_tcc.services.anomaly_detection import REGISTRY, detect_anomaly
from api_tcc.ia.model_registry import registry
from sklearn.ensemble import IsolationForest

class AnomalyPersistenceTest(TransactionTestCase):
    def setUp(self):
        REGISTRY.clear()
        # Clean up persisted models for the test machine
        self.machine_id = "TEST-PERSIST-01"
        import os
        import shutil
        from pathlib import Path
        model_dir = Path('media/models')
        for f in model_dir.glob(f'anomaly_{self.machine_id}_*.pkl'):
            f.unlink()

    def tearDown(self):
        REGISTRY.clear()

    def test_persistence_and_consistency_and_no_fit(self):
        """
        Test that:
        1. A persisted model is loaded.
        2. Two consecutive calls return exactly the same result.
        3. IsolationForest.fit is NOT called when a model is loaded.
        """
        # 1. Setup Machine and Data
        Machine.objects.get_or_create(external_code=self.machine_id)
        
        # Create 100 readings to allow Isolation Forest training
        for i in range(100):
            LeituraTelemetria.objects.create(
                machine=Machine.objects.get(external_code=self.machine_id),
                device_id=f"dev-{i}",
                message_id=f"msg-{i}",
                temperatura=70.0 + (i % 5),
                vibracao=0.4,
                rpm=1800.0,
                timestamp="2026-09-25T10:00:00Z"
            )

        # 2. Manually train and save a model to simulate the management command
        X = np.array([[70.0 + (i % 5), 0.4, 1800.0] for i in range(100)])
        mean = X.mean(axis=0)
        std = np.where(X.std(axis=0) > 1e-9, X.std(axis=0), 1.0)
        X_scaled = (X - mean) / std
        
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(X_scaled)
        
        metadata = {
            'treinado_em': '2026-09-25T12:00:00Z',
            'contamination': 0.05,
            'n_amostras': 100,
            'versao': '1.0',
            'scale_mean': mean.tolist(),
            'scale_std': std.tolist()
        }
        registry.save_model(self.machine_id, model, metadata)

        # 3. Execute two calls and verify consistency
        # We use a specific reading that should be an anomaly
        reading = {"temperatura": 150.0, "vibracao": 5.0, "rpm": 500.0}
        
        # Use a spy on IsolationForest.fit to ensure it's not called
        with patch('api_tcc.services.anomaly_detection.IsolationForest.fit') as mock_fit:
            res1 = detect_anomaly(self.machine_id, reading)
            res2 = detect_anomaly(self.machine_id, reading)
            
            # Criterion: Two consecutive calls must return exactly the same result
            self.assertEqual(res1.anomaly_score, res2.anomaly_score)
            self.assertEqual(res1.is_anomaly, res2.is_anomaly)
            self.assertEqual(res1.explanation, res2.explanation)
            
            # Criterion: fit() must NOT be called if persisted model exists
            mock_fit.assert_not_called()

    def test_management_command_generates_valid_pkl(self):
        """Verify that the management command creates a .pkl with expected metadata."""
        from django.core.management import call_command
        
        # Ensure machine has enough data
        Machine.objects.get_or_create(external_code=self.machine_id)
        for i in range(100):
            LeituraTelemetria.objects.create(
                machine=Machine.objects.get(external_code=self.machine_id),
                device_id=f"dev-cmd-{i}",
                message_id=f"msg-cmd-{i}",
                temperatura=70.0, vibracao=0.4, rpm=1800.0, timestamp="2026-09-25T10:00:00Z"
            )
            
        call_command('treinar_modelo_anomalia', machine=self.machine_id)
        
        path = registry.get_model_path(self.machine_id)
        self.assertIsNotNone(path)
        self.assertTrue(path.exists())
        
        import joblib
        payload = joblib.load(path)
        self.assertIn('model', payload)
        self.assertIn('metadata', payload)
        
        meta = payload['metadata']
        required_keys = ['treinado_em', 'contamination', 'n_amostras', 'versao', 'scale_mean', 'scale_std']
        for key in required_keys:
            self.assertIn(key, meta)
