import base64

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api_tcc import models


WRITE_BLOCKED_STATUS_CODES = {
    status.HTTP_401_UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN,
}


def _criar_colheitadeira(maquina_id="COLH-PERM-01"):
    unidade = models.UnidadedeMedida.objects.create(nome="Centimetro")
    marca = models.Marca.objects.create(nome="Marca Permissao")
    modelo = models.Modelo.objects.create(nome="Modelo Permissao", marca=marca)
    combustivel = models.Combustivel.objects.create(tipo="Diesel", porcentagem=100.0)
    pressao_pneus = models.PressaoPneus.objects.create(
        pressao=2.5,
        unidade_de_medida=unidade,
    )
    altura_corte = models.AlturadoCorte.objects.create(
        altura=5.0,
        unidade_de_medida=unidade,
    )
    pressao_corte = models.PressaodoCorte.objects.create(
        pressao=30.0,
        unidade_de_medida=unidade,
    )
    temp_umi = models.TempUmi_Ambiente.objects.create(
        temperatura=25.0,
        umidade=60.0,
    )
    temp_maquina = models.TemperaturaMaquina.objects.create(
        temperatura=85.0,
        maquina=modelo,
    )
    operario = models.Operario.objects.create(
        nome="Operario Permissao",
        tempo_de_servico=5,
        no_banco=True,
    )
    status_operacao = models.StatusdeOperacao.objects.create(
        em_operacao=True,
        tempo_de_operacao=8.0,
    )
    estado_movimento = models.EstadodeMovimento.objects.create(
        em_movimento=True,
        velocidade=6.5,
    )
    return models.Colheitadeira.objects.create(
        maquina_id=maquina_id,
        modelo=modelo,
        combustivel=combustivel,
        pressao_pneus=pressao_pneus,
        altura_do_corte=altura_corte,
        pressao_do_corte=pressao_corte,
        temp_umi_ambiente=temp_umi,
        temperatura_maquina=temp_maquina,
        operario=operario,
        status_de_operacao=status_operacao,
        estado_de_movimento=estado_movimento,
    )


@override_settings(DEMO_MODE=False)
class PermissaoCRUDTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.colheitadeira = _criar_colheitadeira()
        self.operario = models.Operario.objects.create(
            nome="Operario CRUD",
            tempo_de_servico=3,
            no_banco=True,
        )
        self.marca = models.Marca.objects.create(nome="Marca CRUD")

    def assert_write_blocked(self, response):
        self.assertIn(response.status_code, WRITE_BLOCKED_STATUS_CODES)

    def test_post_sem_auth_bloqueia_colheitadeira_operario_e_marca(self):
        casos = [
            (
                reverse("colheitadeira-list"),
                {"maquina_id": "COLH-SEM-AUTH"},
            ),
            (
                reverse("operario-list"),
                {"nome": "Anonimo", "tempo_de_servico": 1, "no_banco": True},
            ),
            (
                reverse("marca-list"),
                {"nome": "Marca Anonima"},
            ),
        ]

        for url, payload in casos:
            with self.subTest(url=url):
                response = self.client.post(url, payload, format="json")
                self.assert_write_blocked(response)

    def test_get_sem_auth_bloqueia_cruds_de_leitura(self):
        for url in [
            reverse("colheitadeira-list"),
            reverse("operario-list"),
            reverse("marca-list"),
        ]:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(response.status_code, WRITE_BLOCKED_STATUS_CODES)

    def test_delete_sem_auth_e_bloqueado(self):
        response = self.client.delete(reverse("marca-detail", args=[self.marca.id]))

        self.assert_write_blocked(response)
        self.assertTrue(models.Marca.objects.filter(id=self.marca.id).exists())

    def test_patch_sem_auth_e_bloqueado(self):
        response = self.client.patch(
            reverse("operario-detail", args=[self.operario.id]),
            {"nome": "Alterado sem auth"},
            format="json",
        )

        self.assert_write_blocked(response)
        self.operario.refresh_from_db()
        self.assertEqual(self.operario.nome, "Operario CRUD")

    def test_usuario_comum_nao_altera_catalogo_global(self):
        user = User.objects.create_user(username="user-crud", password="senha-forte-123")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("marca-list"),
            {"nome": "Marca Bloqueada"},
            format="json",
        )

        self.assert_write_blocked(response)
        self.assertFalse(models.Marca.objects.filter(nome="Marca Bloqueada").exists())

        response = self.client.patch(
            reverse("marca-detail", args=[self.marca.id]),
            {"nome": "Marca Alterada"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.marca.refresh_from_db()
        self.assertEqual(self.marca.nome, "Marca CRUD")

    def test_staff_pode_alterar_catalogo_global(self):
        user = User.objects.create_superuser(
            username="staff-crud", password="senha-forte-123", email="staff@example.com"
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("marca-list"), {"nome": "Marca Staff"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Marca.objects.filter(nome="Marca Staff").exists())

    def test_ingestao_browser_exige_maquina_da_organizacao_e_role_de_escrita(self):
        user = User.objects.create_user(username="member-ingest", password="senha-forte-123")
        org = models.Organization.objects.create(nome="Org de ingestao")
        machine = models.Machine.objects.create(
            external_code="COLH-INGEST-01", organization=org
        )
        models.Membership.objects.create(user=user, organization=org, role="member")
        self.client.force_authenticate(user=user)

        payload = {"maquina_id": machine.external_code}
        response = self.client.post(
            reverse("ingestao-telemetria"), payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        other_org = models.Organization.objects.create(nome="Outra org")
        other_machine = models.Machine.objects.create(
            external_code="COLH-INGEST-02", organization=other_org
        )
        response = self.client.post(
            reverse("ingestao-telemetria"),
            {"maquina_id": other_machine.external_code},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_ingestao_browser_viewer_nao_pode_escrever(self):
        user = User.objects.create_user(username="viewer-ingest", password="senha-forte-123")
        org = models.Organization.objects.create(nome="Org viewer")
        machine = models.Machine.objects.create(
            external_code="COLH-INGEST-03", organization=org
        )
        models.Membership.objects.create(user=user, organization=org, role="viewer")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("ingestao-telemetria"),
            {"maquina_id": machine.external_code},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_escrita_em_colheitadeira_respeita_role_da_organizacao(self):
        org = models.Organization.objects.create(nome="Org da frota")
        models.Machine.objects.create(
            external_code=self.colheitadeira.maquina_id,
            organization=org,
            colheitadeira=self.colheitadeira,
        )
        member = User.objects.create_user(username="fleet-member")
        viewer = User.objects.create_user(username="fleet-viewer")
        models.Membership.objects.create(user=member, organization=org, role="member")
        models.Membership.objects.create(user=viewer, organization=org, role="viewer")
        url = reverse("colheitadeira-detail", args=[self.colheitadeira.id])
        payload = {"status_de_operacao_id": self.colheitadeira.status_de_operacao_id}

        self.client.force_authenticate(user=member)
        allowed = self.client.patch(url, payload, format="json")
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=viewer)
        denied = self.client.patch(url, payload, format="json")
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)

    def test_credencial_basica_invalida_nao_libera_escrita(self):
        credentials = base64.b64encode(b"usuario-invalido:senha-invalida").decode("ascii")
        client = APIClient(HTTP_AUTHORIZATION=f"Basic {credentials}")

        response = client.post(
            reverse("marca-list"),
            {"nome": "Marca Credencial Invalida"},
            format="json",
        )

        self.assert_write_blocked(response)
        self.assertFalse(models.Marca.objects.filter(nome="Marca Credencial Invalida").exists())


@override_settings(DEMO_MODE=True)
class PermissaoEscritaEmDemoModeTest(TestCase):
    """Garante que DEMO_MODE=True não libera escrita para usuários anônimos."""

    def setUp(self):
        self.client = APIClient()
        self.marca = models.Marca.objects.create(nome="Marca Demo Existente")
        self.operario = models.Operario.objects.create(
            nome="Operario Demo",
            tempo_de_servico=2,
            no_banco=True,
        )

    def test_post_anonimo_bloqueado_em_demo_mode(self):
        for url, payload in [
            (reverse("marca-list"), {"nome": "Marca Indevida"}),
            (reverse("operario-list"), {"nome": "Op Indevido", "tempo_de_servico": 1, "no_banco": True}),
        ]:
            with self.subTest(url=url):
                response = self.client.post(url, payload, format="json")
                self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})

    def test_patch_anonimo_bloqueado_em_demo_mode(self):
        response = self.client.patch(
            reverse("operario-detail", args=[self.operario.id]),
            {"nome": "Alterado em demo"},
            format="json",
        )
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})
        self.operario.refresh_from_db()
        self.assertEqual(self.operario.nome, "Operario Demo")

    def test_delete_anonimo_bloqueado_em_demo_mode(self):
        response = self.client.delete(reverse("marca-detail", args=[self.marca.id]))
        self.assertIn(response.status_code, {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN})
        self.assertTrue(models.Marca.objects.filter(id=self.marca.id).exists())

    def test_usuario_comum_nao_pode_alterar_catalogo_em_demo_mode(self):
        user = User.objects.create_user(username="admin-demo", password="senha-forte-123")
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse("marca-list"),
            {"nome": "Marca Autenticada em Demo"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(models.Marca.objects.filter(nome="Marca Autenticada em Demo").exists())
