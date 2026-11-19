"""Decodificador J1939 puro, sem dependencias de Django."""

from dataclasses import dataclass
import json
from pathlib import Path


TABLE_PATH = Path(__file__).resolve().parent.parent / "adapters" / "j1939_pgn_table.json"
with TABLE_PATH.open(encoding="utf-8") as _table_file:
    PGN_TABLE = json.load(_table_file)["pgns"]


class InvalidFrame(ValueError):
    """Quadro CAN incompatível com o contrato J1939 deste decodificador."""


@dataclass(frozen=True)
class Param:
    canonical: str | None
    value: float | None
    unit: str | None
    spn: int | None = None
    pgn: int | None = None
    status: str = "decoded"
    origem: str = "medido"
    fonte: str | None = None
    raw_value: int | None = None
    quality: str = "mapped"
    mapping_version: str = ""
    raw_field: str | None = None

    @classmethod
    def unsupported(cls, pgn: int):
        return cls(None, None, None, pgn=pgn, status="unsupported", origem="medido", fonte=f"j1939:pgn={pgn}", raw_field=f"pgn:{pgn}")

    @classmethod
    def ausente(cls, spec, pgn, status):
        return cls(
            spec.get("canonical"), None, spec.get("unit"), spn=spec["spn"], pgn=pgn,
            status=status, origem="medido", fonte=f"j1939:pgn={pgn}:spn={spec['spn']}"
        )


def pgn_from_id(can_id: int) -> int:
    if (isinstance(can_id, bool) or not isinstance(can_id, int)
            or not 0x800 < can_id <= 0x1FFFFFFF):
        raise InvalidFrame("CAN ID deve ser um identificador estendido de 29 bits")
    pdu_format = (can_id >> 16) & 0xFF
    pdu_specific = (can_id >> 8) & 0xFF
    data_page = (can_id >> 24) & 0x01
    pgn = (data_page << 16) | (pdu_format << 8)
    if pdu_format >= 240:  # PDU2: PS participa do PGN.
        pgn |= pdu_specific
    return pgn


def extract_bits(data: bytes, start: int, length: int) -> int:
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("payload deve ser bytes")
    if isinstance(start, bool) or isinstance(length, bool) or start < 0 or length <= 0:
        raise ValueError("campo de bits invalido")
    if start + length > len(data) * 8:
        raise InvalidFrame("campo de bits fora do payload")
    integer = int.from_bytes(data, "little")
    return (integer >> start) & ((1 << length) - 1)


def _special_status(raw: int, length: int, spec: dict) -> str | None:
    specials = spec.get("special_values", {})
    if raw in specials.get("unavailable", []):
        return "unavailable"
    if raw in specials.get("error", []):
        return "error"
    if raw in ((1 << length) - 1,):
        return "unavailable"
    return None


def decode(can_id: int, data: bytes) -> list[Param]:
    if not isinstance(data, (bytes, bytearray)) or len(data) != 8:
        raise InvalidFrame("payload J1939 deve conter exatamente 8 bytes")
    pgn = pgn_from_id(can_id)
    spec = PGN_TABLE.get(str(pgn))
    if not spec:
        return [Param.unsupported(pgn)]
    output = []
    for spn in spec["spns"]:
        raw = extract_bits(data, spn["start_bit"], spn["length"])
        status = _special_status(raw, spn["length"], spn)
        if status:
            output.append(Param.ausente(spn, pgn, status))
            continue
        output.append(Param(
            spn["canonical"], raw * spn["resolution"] + spn["offset"], spn["unit"],
            spn=spn["spn"], pgn=pgn, origem="medido",
            fonte=f"j1939:pgn={pgn}:spn={spn['spn']}", raw_value=raw,
        ))
    return output
