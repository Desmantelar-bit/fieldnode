"""Create/rotate the dedicated worker account and its local Compose secret."""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BROKER_SECRET_DIR = ROOT / "mosquitto" / "broker-secrets"
WORKER_SECRET_DIR = ROOT / "mosquitto" / "worker-secrets"
PASSWORD_FILE = BROKER_SECRET_DIR / "passwordfile"
WORKER_SECRET = WORKER_SECRET_DIR / "worker_password"


def reload_broker_if_running() -> None:
    docker = shutil.which("docker")
    if not docker:
        return
    status = subprocess.run(
        [docker, "compose", "ps", "--status", "running", "-q", "mosquitto"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if status.returncode:
        raise RuntimeError("Não foi possível confirmar o estado do broker Compose.")
    if status.stdout.strip():
        subprocess.run(
            [docker, "compose", "restart", "mosquitto"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rotate", action="store_true")
    args = parser.parse_args()
    mosquitto_passwd = shutil.which("mosquitto_passwd")
    if not mosquitto_passwd:
        parser.error("mosquitto_passwd não encontrado no PATH do host")
    if WORKER_SECRET.exists() and not args.rotate:
        parser.error("segredo de worker já existe; use --rotate explicitamente")

    BROKER_SECRET_DIR.mkdir(parents=True, exist_ok=True)
    WORKER_SECRET_DIR.mkdir(parents=True, exist_ok=True)
    password = secrets.token_urlsafe(32)
    previous_password_file = PASSWORD_FILE.read_bytes() if PASSWORD_FILE.exists() else None
    previous_secret = WORKER_SECRET.read_bytes() if WORKER_SECRET.exists() else None
    password_fd, password_temp_name = tempfile.mkstemp(prefix=".passwordfile-", dir=BROKER_SECRET_DIR)
    secret_fd, secret_temp_name = tempfile.mkstemp(prefix=".worker-secret-", dir=WORKER_SECRET_DIR)
    os.close(password_fd)
    os.close(secret_fd)
    password_temp = Path(password_temp_name)
    secret_temp = Path(secret_temp_name)
    try:
        if previous_password_file is not None:
            password_temp.write_bytes(previous_password_file)
        argv = [mosquitto_passwd]
        if previous_password_file is None:
            argv.append("-c")
        argv.extend([str(password_temp), "fieldnode-worker"])
        result = subprocess.run(
            argv, input=f"{password}\n{password}\n", text=True,
            capture_output=True, check=False,
        )
        if result.returncode:
            raise RuntimeError("mosquitto_passwd falhou ao atualizar conta do worker")
        secret_temp.write_text(password, encoding="utf-8")
        os.chmod(password_temp, 0o600)
        os.chmod(secret_temp, 0o600)
        os.replace(password_temp, PASSWORD_FILE)
        os.replace(secret_temp, WORKER_SECRET)
        reload_broker_if_running()
    except Exception:
        if previous_password_file is None:
            PASSWORD_FILE.unlink(missing_ok=True)
        else:
            PASSWORD_FILE.write_bytes(previous_password_file)
            os.chmod(PASSWORD_FILE, 0o600)
        if previous_secret is None:
            WORKER_SECRET.unlink(missing_ok=True)
        else:
            WORKER_SECRET.write_bytes(previous_secret)
            os.chmod(WORKER_SECRET, 0o600)
        try:
            reload_broker_if_running()
        except Exception:
            pass
        raise
    finally:
        password_temp.unlink(missing_ok=True)
        secret_temp.unlink(missing_ok=True)

    print("Usuário MQTT fieldnode-worker provisionado.")
    print("O segredo está no arquivo local ignorado pelo Git: mosquitto/worker-secrets/worker_password.")
    print("O broker é recarregado se estiver ativo; reinicie o worker após rotação.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
