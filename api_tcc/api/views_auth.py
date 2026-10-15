"""
api_tcc/api/views_auth.py

View de autenticação com renovação de token expirado.
"""
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from api_tcc.authentication import is_token_expired, token_expires_in


class ExpiringAuthTokenView(ObtainAuthToken):
    """
    POST /api/auth/login/

    Gera ou renova o token para credenciais válidas.
    Se o token existente já expirou, ele é removido e um novo é criado.
    Retorna o token e metadados de expiração.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, created = Token.objects.get_or_create(user=user)
        if not created and is_token_expired(token):
            token.delete()
            token = Token.objects.create(user=user)

        return Response({
            "token": token.key,
            "expires_in": token_expires_in(token),
            "user_id": user.id,
            "username": user.username,
        })

