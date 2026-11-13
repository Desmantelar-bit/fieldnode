"""Provision an individual MQTT identity; the generated password is shown once."""

from __future__ import annotations

import argparse
import os
import re
import secrets
import shutil
import subprocess
import tempfile
from pathlib import Path

import django
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone


DEVICE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
ROOT = Path(__file__).resolve().parents[1]
PASSWORD_FILE = ROOT / "mosquitto" / "broker-secrets" / "passwordfile"


def _reload_broker_if_running() -> None:
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


def _set_mosquitto_password(path: Path, username: str, password: str) -> None:
    executable = shutil.which("mosquitto_passwd")
    if not executable:
        raise RuntimeError("mosquitto_passwd não encontrado no PATH do host.")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=".passwordfile-", dir=path.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        if path.exists():
            shutil.copyfile(path, temporary)
        # Interactive mode receives the secret through stdin; it never appears in argv.
        argv = [executable]
        if not path.exists():
            argv.append("-c")
        argv.extend([str(temporary), username])
        result = subprocess.run(
            argv,
            input=f"{password}\n{password}\n",
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError("mosquitto_passwd falhou ao atualizar o arquivo protegido.")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _delete_mosquitto_user(path: Path, username: str) -> None:
    executable = shutil.which("mosquitto_passwd")
    if not executable or not path.exists():
        raise RuntimeError("mosquitto_passwd ou password file ausente.")
    fd, temporary_name = tempfile.mkstemp(prefix=".passwordfile-", dir=path.parent)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        shutil.copyfile(path, temporary)
        result = subprocess.run(
            [executable, "-D", str(temporary), username],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise RuntimeError("mosquitto_passwd falhou ao revogar a identidade.")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("device_id")
    parser.add_argument("--http", action="store_true", help="provisiona credencial HTTP de ingestão")
    parser.add_argument("--rotate", action="store_true", help="revoga e substitui a credencial ativa")
    parser.add_argument("--revoke", action="store_true", help="revoga a credencial existente")
    args = parser.parse_args()
    if args.rotate and args.revoke:
        parser.error("--rotate e --revoke não podem ser usados juntos")
    if not DEVICE_ID.fullmatch(args.device_id):
        parser.error("device_id inválido; use letras, números, ponto, hífen ou underscore")
    if args.device_id == "fieldnode-worker":
        parser.error("fieldnode-worker é uma identidade reservada")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
    django.setup()
    if args.http:
        from api_tcc.services.device_credentials import provision_http_credential
        try:
            key = provision_http_credential(args.device_id, rotate=args.rotate, revoke=args.revoke)
        except ValueError as exc:
            parser.error(str(exc))
        if key:
            print(f"X-Device-Id: {args.device_id}")
            print(f"X-Device-Key (exibida uma vez): {key}")
        else:
            print(f"Credencial HTTP revogada para {args.device_id}.")
        return 0
    from api_tcc.models import DeviceCredential
    from api_tcc.services.audit import record as audit_record

    existing = DeviceCredential.objects.filter(device_id=args.device_id).first()
    has_mqtt_credential = bool(existing and existing.credential_hash != "!")
    if args.revoke:
        if not existing or not existing.active:
            parser.error("nenhuma credencial ativa encontrada para revogação")
        old_bytes = PASSWORD_FILE.read_bytes() if PASSWORD_FILE.exists() else None
        try:
            with transaction.atomic():
                existing.active = False
                existing.revoked_at = timezone.now()
                existing.provisioning_state = "revoked"
                existing.save(update_fields=["active", "revoked_at", "provisioning_state"])
                _delete_mosquitto_user(PASSWORD_FILE, existing.username)
                _reload_broker_if_running()
                audit_record("credential.revoked", existing, before={"active": True}, after={"active": False}, metadata={"purpose": "mqtt"})
        except Exception:
            if old_bytes is not None:
                PASSWORD_FILE.write_bytes(old_bytes)
                os.chmod(PASSWORD_FILE, 0o600)
            try:
                _reload_broker_if_running()
            except Exception:
                pass
            raise
        print(f"Credencial MQTT revogada para {args.device_id}.")
        return 0

    if has_mqtt_credential and not args.rotate:
        parser.error("credencial existente; use --rotate para uma rotação explícita")
    if PASSWORD_FILE.exists():
        usernames = {
            line.partition(":")[0]
            for line in PASSWORD_FILE.read_text(encoding="utf-8").splitlines()
            if ":" in line
        }
        if args.device_id in usernames and not existing:
            parser.error("usuário já existe no password file sem registro DeviceCredential; revise manualmente")

    password = secrets.token_urlsafe(32)
    old_bytes = PASSWORD_FILE.read_bytes() if PASSWORD_FILE.exists() else None
    try:
        # Database and broker file are committed as one controlled operation with rollback.
        with transaction.atomic():
            if existing:
                existing.active = False
                existing.revoked_at = timezone.now()
                existing.save(update_fields=["active", "revoked_at"])
            if existing:
                credential = existing
                credential.username = args.device_id
                credential.credential_hash = make_password(password)
                credential.active = False
                credential.revoked_at = None
                credential.rotated_at = timezone.now()
                credential.provisioning_state = "pending"
                credential.save()
            else:
                credential = DeviceCredential.objects.create(
                    device_id=args.device_id,
                    username=args.device_id,
                    credential_hash=make_password(password),
                    active=False,
                    provisioning_state="pending",
                )
            _set_mosquitto_password(PASSWORD_FILE, args.device_id, password)
            _reload_broker_if_running()
            credential.active = True
            credential.provisioning_state = "active"
            credential.save(update_fields=["active", "provisioning_state"])
            audit_record(
                "credential.rotated" if has_mqtt_credential else "credential.created",
                credential,
                before={"active": bool(existing)},
                after={"active": True},
                metadata={"purpose": "mqtt"},
            )
    except Exception:
        if old_bytes is None:
            PASSWORD_FILE.unlink(missing_ok=True)
        else:
            PASSWORD_FILE.write_bytes(old_bytes)
            os.chmod(PASSWORD_FILE, 0o600)
        try:
            _reload_broker_if_running()
        except Exception:
            pass
        raise

    print(f"device_id: {args.device_id}")
    print(f"username: {args.device_id}")
    print(f"password (exibida uma vez): {password}")
    print("Atualize/recarregue o broker após provisionar; descarte este segredo após gravar o firmware.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
