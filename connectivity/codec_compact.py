"""Codec deterministico do quadro compacto de telemetria classe A."""

from __future__ import annotations

import struct
from datetime import datetime, timezone
from typing import Any, Mapping

FRAME_VERSION = 1
FRAME_SIZE = 28
_BODY_SIZE = 26
_FRAME = struct.Struct("<BBHIIhHHiiH")
CLASS_BITS = {"A": 0, "B": 1, "C": 2}
CLASS_NAMES = {value: key for key, value in CLASS_BITS.items()}
REGIME_BITS = {None: 0, "desconhecido": 0, "desligada": 1, "marcha_lenta": 2, "trabalhando": 3, "deslocamento": 4}
REGIME_NAMES = {value: key for key, value in REGIME_BITS.items() if key is not None}
REGIME_NAMES[0] = None
TIME_BITS = {"rtc": 0, "gateway": 1, "ntp": 2, "unsynced": 3}
TIME_NAMES = {value: key for key, value in TIME_BITS.items()}
GPS_PRESENT = 0x80


class CompactFrameError(ValueError):
    """Quadro compacto invalido ou incompatível com o contrato."""


def crc16_ccitt_false(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def _scaled(value: Any, scale: int, minimum: int, maximum: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CompactFrameError(f"{field} deve ser numerico")
    scaled = int(round(float(value) * scale))
    if not minimum <= scaled <= maximum:
        raise CompactFrameError(f"{field} fora da faixa representável")
    return scaled


def _unix_seconds(payload: Mapping[str, Any]) -> int:
    time_source = payload.get("time_source", "unsynced")
    if time_source not in TIME_BITS:
        raise CompactFrameError("time_source desconhecido")
    raw = payload.get("event_time", payload.get("timestamp"))
    if raw is None:
        if time_source != "unsynced":
            raise CompactFrameError("timestamp obrigatório para relógio sincronizado")
        return 0
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        seconds = int(raw)
    else:
        try:
            parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError as exc:
            raise CompactFrameError("event_time/timestamp inválido") from exc
        if parsed.tzinfo is None:
            raise CompactFrameError("timestamp deve conter timezone")
        seconds = int(parsed.astimezone(timezone.utc).timestamp())
    if not 1 <= seconds <= 0xFFFFFFFF:
        raise CompactFrameError("event_time fora da faixa u32")
    return seconds


def encode_frame(payload: Mapping[str, Any], *, device_idx: int) -> bytes:
    if not isinstance(device_idx, int) or isinstance(device_idx, bool) or not 0 <= device_idx <= 0xFFFF:
        raise CompactFrameError("device_idx deve ser u16 registrado no gateway")
    priority = payload.get("priority_class", payload.get("priority"))
    if priority not in CLASS_BITS:
        raise CompactFrameError("priority_class deve ser A, B ou C")
    regime = payload.get("regime")
    if regime not in REGIME_BITS:
        raise CompactFrameError("regime não representável")
    time_source = payload.get("time_source", "unsynced")
    if time_source not in TIME_BITS:
        raise CompactFrameError("time_source desconhecido")
    flags = CLASS_BITS[priority] | (REGIME_BITS[regime] << 2) | (TIME_BITS[time_source] << 5)
    latitude = payload.get("latitude", payload.get("lat"))
    longitude = payload.get("longitude", payload.get("lon"))
    if (latitude is None) != (longitude is None):
        raise CompactFrameError("latitude e longitude devem aparecer juntas")
    if latitude is None:
        lat_e5 = lon_e5 = 0
    else:
        lat_e5 = _scaled(latitude, 100000, -9000000, 9000000, "latitude")
        lon_e5 = _scaled(longitude, 100000, -18000000, 18000000, "longitude")
        flags |= GPS_PRESENT
    sequence = payload.get("sequence_number", payload.get("sequence"))
    if not isinstance(sequence, int) or isinstance(sequence, bool) or not 1 <= sequence <= 0xFFFFFFFF:
        raise CompactFrameError("sequence deve ser u32 positivo")
    temperature = _scaled(payload.get("temperatura"), 100, -32768, 32767, "temperatura")
    vibration = _scaled(payload.get("vibracao"), 100, 0, 0xFFFF, "vibracao")
    rpm = _scaled(payload.get("rpm"), 1, 0, 0xFFFF, "rpm")
    body = struct.pack("<BBHIIhHHii", FRAME_VERSION, flags, device_idx, sequence, _unix_seconds(payload), temperature, vibration, rpm, lat_e5, lon_e5)
    return body + struct.pack("<H", crc16_ccitt_false(body))


def decode_frame(frame: bytes, *, device_id: str | None = None, device_registry: Mapping[int, str] | None = None) -> dict[str, Any]:
    if len(frame) != FRAME_SIZE:
        raise CompactFrameError("comprimento de quadro inválido")
    version, flags, device_idx, sequence, event_time, temp_x100, vib_x100, rpm, lat_e5, lon_e5, received_crc = _FRAME.unpack(frame)
    if version != FRAME_VERSION:
        raise CompactFrameError("versão de quadro desconhecida")
    if crc16_ccitt_false(frame[:_BODY_SIZE]) != received_crc:
        raise CompactFrameError("CRC inválido")
    class_id = flags & 0x03
    regime_id = (flags >> 2) & 0x07
    time_id = (flags >> 5) & 0x03
    if class_id not in CLASS_NAMES or regime_id not in REGIME_NAMES or time_id not in TIME_NAMES:
        raise CompactFrameError("flags inválidas")
    resolved = device_id or (device_registry or {}).get(device_idx)
    if not resolved:
        raise CompactFrameError("device_idx não registrado; identidade não pode ser inventada")
    has_gps = bool(flags & GPS_PRESENT)
    if not has_gps and (lat_e5 or lon_e5):
        raise CompactFrameError("coordenadas presentes sem flag GPS")
    time_source = TIME_NAMES[time_id]
    if time_source == "unsynced" and event_time != 0:
        raise CompactFrameError("timestamp não confiável deve ser zero")
    if time_source != "unsynced" and event_time == 0:
        raise CompactFrameError("timestamp sincronizado ausente")
    decoded: dict[str, Any] = {"device_id": resolved, "device_idx": device_idx, "sequence_number": sequence,
        "priority_class": CLASS_NAMES[class_id], "regime": REGIME_NAMES[regime_id], "time_source": time_source,
        "temperatura": temp_x100 / 100, "vibracao": vib_x100 / 100, "vibracao_unit": "indice_0_10", "rpm": rpm,
        "event_time_unix_s": event_time}
    decoded.update({"latitude": lat_e5 / 100000 if has_gps else None, "longitude": lon_e5 / 100000 if has_gps else None})
    return decoded


contract_to_frame = encode_frame
frame_to_contract = decode_frame
