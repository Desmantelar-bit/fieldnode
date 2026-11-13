import importlib

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import clear_url_caches
from rest_framework.test import APIClient

import setup.urls


class DocumentacaoUrlsTestCase(TestCase):
    def _reload_urls(self):
        clear_url_caches()
        importlib.reload(setup.urls)
        clear_url_caches()

    def tearDown(self):
        self._reload_urls()

    @override_settings(DEBUG=True, SWAGGER_ENABLED=True)
    def test_documentacao_publica_em_desenvolvimento(self):
        self._reload_urls()
        client = APIClient()
        for path in ("/swagger/", "/swagger.json/", "/redoc/"):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 200)

    @override_settings(DEBUG=False, SWAGGER_ENABLED=True, FIELDNODE_FRONTEND_URL="https://frontend.example")
    def test_documentacao_exige_staff_fora_de_debug_em_todas_as_rotas(self):
        self._reload_urls()
        client = APIClient()
        user = User.objects.create_user(username="regular")
        staff = User.objects.create_user(username="staff", is_staff=True)
        for path in ("/swagger/", "/swagger.json/", "/redoc/"):
            with self.subTest(path=path):
                self.assertIn(client.get(path).status_code, (401, 403))
                client.force_authenticate(user=user)
                self.assertEqual(client.get(path).status_code, 403)
                client.force_authenticate(user=staff)
                self.assertEqual(client.get(path).status_code, 200)
                client.force_authenticate(user=None)

    @override_settings(DEBUG=True, SWAGGER_ENABLED=False)
    def test_flag_desligada_protege_documentacao_com_is_admin(self):
        self._reload_urls()
        self.assertIn(APIClient().get("/swagger/").status_code, (401, 403))

    @override_settings(DEBUG=True, SWAGGER_ENABLED=True, FIELDNODE_FRONTEND_URL="https://frontend.example")
    def test_raiz_redireciona_para_frontend(self):
        self._reload_urls()
        response = APIClient().get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://frontend.example")
