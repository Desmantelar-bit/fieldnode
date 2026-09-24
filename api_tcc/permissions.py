from __future__ import annotations

from typing import Any

from django.conf import settings
from rest_framework.permissions import BasePermission

from api_tcc.models import Machine, Membership


MACHINE_WRITE_ROLES = frozenset({"admin", "member"})


def get_machines_for_user(user):
    """Return active machines belonging to organizations of an authenticated user."""
    if not user or not user.is_authenticated:
        return Machine.objects.none()

    return Machine.objects.filter(
        organization__membership__user=user,
        ativo=True,
    ).distinct()


def user_can_access_machine(user, machine: Machine | None, *, write: bool = False) -> bool:
    """Check organization membership and, for writes, the allowed role."""
    if not user or not user.is_authenticated or machine is None:
        return False

    memberships = Membership.objects.filter(
        user=user,
        organization_id=machine.organization_id,
    )
    if write:
        memberships = memberships.filter(role__in=MACHINE_WRITE_ROLES)
    return memberships.exists()


def is_public_demo_request(request) -> bool:
    return bool(settings.DEMO_MODE and not request.user.is_authenticated)


def request_can_access_machine(request, machine: Machine | None) -> bool:
    if is_public_demo_request(request):
        return bool(machine and machine.is_demo)
    return user_can_access_machine(request.user, machine)


def get_machines_for_request(request):
    if is_public_demo_request(request):
        return Machine.objects.filter(is_demo=True, ativo=True)
    return get_machines_for_user(request.user)


def get_machine_for_request(request, external_code: str):
    return get_machines_for_request(request).filter(
        external_code=str(external_code).strip().upper(),
    ).first()


def machine_from_object(obj: Any) -> Machine | None:
    """Resolve the canonical machine from common domain objects."""
    if isinstance(obj, Machine):
        return obj
    return getattr(obj, "machine", None)


class HasMachineAccess(BasePermission):
    """Allow access only to users belonging to the machine's organization."""

    def has_object_permission(self, request, view, obj):
        machine = machine_from_object(obj)
        return user_can_access_machine(request.user, machine)


class IsAuthenticatedOrPublicDemo(BasePermission):
    """Allow anonymous access only to the explicitly isolated demo dataset."""

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated or is_public_demo_request(request))
