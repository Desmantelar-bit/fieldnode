"""
api_tcc/authentication.py

Autenticação por token com expiração configurável.
Protege contra tokens e sessões permanentes em produção (OWASP A07:2021).
"""
from datetime import timedelta
import logging

from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from api_tcc.models import OrganizationToken

logger = logging.getLogger(__name__)

# TTL padrão do token: 24 horas (configurável via settings.TOKEN_TTL_HOURS)
DEFAULT_TOKEN_TTL_HOURS = 24


def get_token_ttl() -> timedelta:
    hours = getattr(settings, "TOKEN_TTL_HOURS", DEFAULT_TOKEN_TTL_HOURS)
    try:
        return timedelta(hours=int(hours))
    except (TypeError, ValueError):
        return timedelta(hours=DEFAULT_TOKEN_TTL_HOURS)


def is_token_expired(token: Token) -> bool:
    ttl = get_token_ttl()
    return (timezone.now() - token.created) > ttl


def token_expires_in(token: Token) -> int:
    """Retorna segundos restantes até a expiração (mínimo 0)."""
    ttl = get_token_ttl()
    remaining = ttl - (timezone.now() - token.created)
    return max(0, int(remaining.total_seconds()))


class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Autenticação por token com verificação de tempo de vida (TTL).
    Rejeita tokens expirados com 401 Unauthorized e mensagem clara.
    """

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Token inválido.")

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("Usuário inativo ou excluído.")

        if is_token_expired(token):
            logger.warning(
                "Tentativa de uso de token expirado para usuário %s.",
                token.user.username,
            )
            raise exceptions.AuthenticationFailed(
                "Token expirado. Efetue login novamente para renovar as credenciais."
            )

        return (token.user, token)


class OrganizationTokenAuthentication:
    """Autentica tokens de integração Bearer, preservando a organização no request."""
    www_authenticate_realm = "api"

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        import hashlib
        from rest_framework import exceptions
        raw = header[7:].strip()
        token = OrganizationToken.objects.select_related("created_by", "organization").filter(token_hash=hashlib.sha256(raw.encode()).hexdigest()).first()
        if not token or not token.is_active or not token.created_by.is_active:
            raise exceptions.AuthenticationFailed("Token de integração inválido, expirado ou revogado.")
        request.organization_token = token
        return token.created_by, token

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
