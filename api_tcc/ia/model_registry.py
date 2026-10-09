"""Persistência local dos artefatos de detecção de anomalias."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
from django.conf import settings


class ModelNotFoundError(FileNotFoundError):
    """Não existe artefato persistido para a máquina informada."""


class ModelArtifactError(RuntimeError):
    """O artefato existe, mas não pôde ser carregado ou não é válido."""


class ModelRegistry:
    _filename_pattern = re.compile(r"^anomaly_(?P<machine>.+)_(?P<timestamp>\d{8}T\d{12}Z)\.pkl$")

    @property
    def models_dir(self) -> Path:
        directory = Path(settings.BASE_DIR) / "media" / "models"
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    @staticmethod
    def _machine_token(machine_id: str) -> str:
        token = str(machine_id).strip()
        if not token or token in {".", ".."} or "/" in token or "\\" in token:
            raise ValueError("machine_id inválido para resolução do artefato")
        return re.sub(r"[^A-Za-z0-9_.-]", "_", token)

    def get_model_path(self, machine_id: str) -> Path | None:
        token = self._machine_token(machine_id)
        candidates = []
        for path in self.models_dir.glob(f"anomaly_{token}_*.pkl"):
            match = self._filename_pattern.match(path.name)
            if match and match.group("machine") == token:
                candidates.append(path)
        return max(candidates, key=lambda path: path.name) if candidates else None

    def save_model(self, machine_id: str, model: Any, metadata: dict[str, Any]) -> Path:
        token = self._machine_token(machine_id)
        trained_at = str(metadata.get("treinado_em", ""))
        if not trained_at:
            raise ValueError("metadata.treinado_em é obrigatório")
        try:
            iso_value = trained_at[:-1] + "+00:00" if trained_at.endswith("Z") else trained_at
            timestamp = datetime.fromisoformat(iso_value).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        except ValueError as exc:
            raise ValueError("metadata.treinado_em deve ser um timestamp ISO-8601") from exc
        path = self.models_dir / f"anomaly_{token}_{timestamp}.pkl"
        if path.exists():
            raise FileExistsError(f"artefato já existe: {path.name}")
        joblib.dump({"model": model, "metadata": metadata}, path)
        return path

    def load_latest_model(self, machine_id: str) -> tuple[Any, dict[str, Any]]:
        path = self.get_model_path(machine_id)
        if path is None:
            raise ModelNotFoundError(f"nenhum modelo encontrado para {machine_id}")
        try:
            payload = joblib.load(path)
        except Exception as exc:
            raise ModelArtifactError(f"não foi possível carregar {path.name}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("metadata"), dict) or "model" not in payload:
            raise ModelArtifactError(f"estrutura inválida no artefato {path.name}")
        return payload["model"], payload["metadata"]

    def load_model(self, machine_id: str) -> tuple[Any, dict[str, Any]] | None:
        try:
            return self.load_latest_model(machine_id)
        except ModelNotFoundError:
            return None


registry = ModelRegistry()
