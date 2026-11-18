"""Consultas e mutações do Operation Graph v0.1."""

from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from api_tcc.models import Front, Machine, MachineLink, Organization


def _reference_time(em: datetime | None) -> datetime:
    return em or timezone.now()


def _validate_organization(machine: Machine, organization: Organization | None) -> Organization:
    if organization is None:
        if machine.organization_id is None:
            raise ValidationError("A organização confiável é obrigatória para consultar o grafo.")
        return machine.organization
    if machine.organization_id != organization.pk:
        raise ValidationError("A máquina não pertence à organização informada.")
    return organization


@transaction.atomic
def criar_machine_link(
    *,
    origem: Machine,
    destino: Machine,
    tipo: str,
    valido_de: datetime,
    valido_ate: datetime | None = None,
    front: Front | None = None,
    organization: Organization | None = None,
) -> MachineLink:
    """Cria um vínculo sem cruzar organizações nem sobrepor o mesmo intervalo."""

    if origem.pk == destino.pk:
        raise ValidationError("Origem e destino devem ser máquinas distintas.")
    organization = _validate_organization(origem, organization)
    _validate_organization(destino, organization)
    if front is not None and front.organization_id != organization.pk:
        raise ValidationError("A frente não pertence à organização do vínculo.")
    if tipo not in MachineLink.Tipo.values:
        raise ValidationError({"tipo": "Tipo de vínculo não suportado."})
    if valido_ate is not None and valido_de >= valido_ate:
        raise ValidationError({"valido_ate": "valido_de deve ser anterior a valido_ate."})

    candidate = MachineLink(
        organization=organization,
        origem=origem,
        destino=destino,
        tipo=tipo,
        front=front,
        valido_de=valido_de,
        valido_ate=valido_ate,
    )
    candidate.full_clean()

    overlap = MachineLink.objects.filter(
        organization=organization,
        origem=origem,
        destino=destino,
        tipo=tipo,
    ).filter(Q(valido_ate__isnull=True) | Q(valido_ate__gt=valido_de))
    if valido_ate is not None:
        overlap = overlap.filter(valido_de__lt=valido_ate)
    if overlap.exists():
        raise ValidationError("Já existe vínculo equivalente com período sobreposto.")
    return MachineLink.objects.create(
        organization=organization,
        origem=origem,
        destino=destino,
        tipo=tipo,
        front=front,
        valido_de=valido_de,
        valido_ate=valido_ate,
    )


@transaction.atomic
def encerrar_machine_link(link: MachineLink, *, valido_ate: datetime) -> MachineLink:
    """Encerra um vínculo preservando a linha histórica."""

    if valido_ate <= link.valido_de:
        raise ValidationError("O encerramento deve ocorrer depois do início.")
    if link.valido_ate is not None and valido_ate > link.valido_ate:
        raise ValidationError("O encerramento não pode ampliar o período existente.")
    link.valido_ate = valido_ate
    link.full_clean()
    link.save(update_fields=["valido_ate", "atualizado_em"])
    return link


def afetados_por(
    machine: Machine,
    em: datetime | None = None,
    max_hops: int = 3,
    *,
    organization: Organization | None = None,
) -> list[dict[str, Any]]:
    """Retorna máquinas alcançáveis por BFS limitado e com caminho auditável.

    ALIMENTA e TRANSPORTA_PARA seguem a direção cadastrada. DEPENDE_DE é
    percorrido no sentido inverso, da dependência para o dependente.
    """

    if max_hops < 0:
        raise ValueError("max_hops não pode ser negativo")
    if max_hops == 0:
        return []
    organization = _validate_organization(machine, organization)
    reference = _reference_time(em)
    active = MachineLink.objects.filter(
        organization=organization,
        valido_de__lte=reference,
    ).filter(Q(valido_ate__isnull=True) | Q(valido_ate__gt=reference)).select_related(
        "origem", "destino", "front"
    )

    outgoing: dict[Any, list[tuple[Machine, MachineLink]]] = {}
    incoming_dependencies: dict[Any, list[tuple[Machine, MachineLink]]] = {}
    for link in active:
        if link.tipo in (MachineLink.Tipo.ALIMENTA, MachineLink.Tipo.TRANSPORTA_PARA):
            outgoing.setdefault(link.origem_id, []).append((link.destino, link))
        elif link.tipo == MachineLink.Tipo.DEPENDE_DE:
            incoming_dependencies.setdefault(link.destino_id, []).append((link.origem, link))

    queue = deque([(machine, 0, tuple())])
    visited = {machine.pk}
    result: list[dict[str, Any]] = []
    while queue:
        current, distance, path = queue.popleft()
        if distance >= max_hops:
            continue
        neighbors = outgoing.get(current.pk, []) + incoming_dependencies.get(current.pk, [])
        for neighbor, link in neighbors:
            if neighbor.pk in visited:
                continue
            visited.add(neighbor.pk)
            next_path = path + (link,)
            result.append({"machine": neighbor, "distance": distance + 1, "path": list(next_path)})
            queue.append((neighbor, distance + 1, next_path))
    return result
