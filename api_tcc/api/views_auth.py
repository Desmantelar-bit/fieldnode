"""
api_tcc/api/views_auth.py

View de autenticação com renovação de token expirado.
"""
import logging

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api_tcc.authentication import is_token_expired, token_expires_in

logger = logging.getLogger(__name__)


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


def _user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


class RegisterView(APIView):
    """Cria uma conta comum sem conceder privilégios administrativos."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password", "")
        first_name = str(request.data.get("first_name", "")).strip()
        last_name = str(request.data.get("last_name", "")).strip()

        errors = {}
        if not username:
            errors["username"] = "O nome de usuário é obrigatório."
        if not password:
            errors["password"] = "A senha é obrigatória."
        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username__iexact=username).exists():
            return Response(
                {"errors": {"username": "Este nome de usuário já está em uso."}},
                status=status.HTTP_409_CONFLICT,
            )
        if email and User.objects.filter(email__iexact=email).exists():
            return Response(
                {"errors": {"email": "Este e-mail já está cadastrado."}},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            validate_password(password)
        except DjangoValidationError as exc:
            return Response(
                {"errors": {"password": " ".join(exc.messages)}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                token = Token.objects.create(user=user)
        except IntegrityError:
            return Response(
                {"errors": {"username": "Este nome de usuário já está em uso."}},
                status=status.HTTP_409_CONFLICT,
            )
        except Exception:
            logger.exception("Falha ao criar conta pública")
            return Response(
                {"error": "Não foi possível criar a conta. Tente novamente."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"token": token.key, "user": _user_payload(user)},
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"message": "Logout realizado com sucesso."})


class MeView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_user_payload(request.user))

