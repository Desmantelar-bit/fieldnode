from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api_tcc import models


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
