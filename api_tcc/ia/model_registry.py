import os
import joblib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

MODELS_DIR = Path('media/models')
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class ModelRegistry:
    @staticmethod
    def get_model_path(machine_id: str) -> Optional[Path]:
        files = list(MODELS_DIR.glob(f'anomaly_{machine_id}_*.pkl'))
        if not files:
            return None
        return max(files, key=os.path.getctime)

    @classmethod
    def save_model(cls, machine_id: str, model: Any, metadata: Dict[str, Any]) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'anomaly_{machine_id}_{timestamp}.pkl'
        path = MODELS_DIR / filename
        payload = {'model': model, 'metadata': metadata}
        joblib.dump(payload, path)
        return path

    @classmethod
    def load_model(cls, machine_id: str) -> Optional[Tuple[Any, Dict[str, Any]]]:
        path = cls.get_model_path(machine_id)
        if path is None or not path.exists():
            return None
        try:
            payload = joblib.load(path)
            return payload['model'], payload['metadata']
        except Exception:
            return None

registry = ModelRegistry()
