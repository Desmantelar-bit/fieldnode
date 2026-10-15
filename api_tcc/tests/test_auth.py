from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_tcc import models


@override_settings(DEMO_MODE=False)
class TokenAuthTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="admin-token",
            password="senha-forte-123",
        )

    def test_login_com_credencial_valida_retorna_token(self):
        response = self.client.post(
            reverse("auth-login"),
            {"username": "admin-token", "password": "senha-forte-123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["token"], Token.objects.get(user=self.user).key)

    def test_login_com_credencial_invalida_retorna_400(self):
        response = self.client.post(
            reverse("auth-login"),
            {"username": "admin-token", "password": "senha-errada"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_cadastro_publico_cria_usuario_comum_e_retorna_token(self):
        response = self.client.post(
            reverse("auth-register"),
            {
                "username": "operador-novo",
                "email": "operador@example.com",
                "password": "Senha-forte-123!",
                "first_name": "Operador",
                "last_name": "Novo",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="operador-novo")
        self.assertTrue(user.check_password("Senha-forte-123!"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(response.data["token"], Token.objects.get(user=user).key)

    def test_cadastro_rejeita_usuario_duplicado(self):
        response = self.client.post(
            reverse("auth-register"),
            {"username": "ADMIN-TOKEN", "password": "Senha-forte-123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("username", response.data["errors"])

    def test_token_autoriza_escrita_em_endpoint_de_cadastro(self):
        login_response = self.client.post(
            reverse("auth-login"),
            {"username": "admin-token", "password": "senha-forte-123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {login_response.data['token']}"
        )

        response = self.client.post(
            reverse("marca-list"),
            {"nome": "Marca via Token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Marca.objects.filter(nome="Marca via Token").exists())

    def test_escrita_sem_token_e_rejeitada(self):
        response = self.client.post(
            reverse("marca-list"),
            {"nome": "Marca sem Token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(models.Marca.objects.filter(nome="Marca sem Token").exists())

    def test_token_invalido_nao_autoriza_escrita(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token token-invalido")

        response = self.client.post(
            reverse("marca-list"),
            {"nome": "Marca Token Invalido"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(models.Marca.objects.filter(nome="Marca Token Invalido").exists())
