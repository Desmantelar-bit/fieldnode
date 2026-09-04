"""
Testes unitários — S1-T1: Modelo Machine canônico + backfill
=============================================================

Cobertura:
- TestMachineUniqueness   : external_code é único (IntegrityError em duplicata)
- TestBackfillMachines    : command é idempotente e normaliza strings sujas
- TestMachineStr          : __str__ retorna external_code
- TestOrganization        : criação básica de Organization
- TestMembership          : criação de Membership com papel correto
"""

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from io import StringIO

from api_tcc.models import LeituraTelemetria, Machine, Organization, Membership


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _criar_leitura(maquina_id: str) -> LeituraTelemetria:
    """Cria uma LeituraTelemetria mínima com o maquina_id fornecido."""
    return LeituraTelemetria.objects.create(
        maquina_id=maquina_id,
        temperatura=75.0,
        vibracao=0.30,
        rpm=1800,
        timestamp=timezone.now(),
    )


# ---------------------------------------------------------------------------
# Testes de Machine
# ---------------------------------------------------------------------------

class TestMachineUniqueness(TestCase):
    """
    Critério de aceite: external_code é UNIQUE — tentar criar dois registros
    com o mesmo código deve levantar IntegrityError do banco de dados.
    """

    def test_external_code_unico(self):
        Machine.objects.create(external_code="ESP-001")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Machine.objects.create(external_code="ESP-001")

    def test_codigos_distintos_nao_conflitam(self):
        Machine.objects.create(external_code="ESP-001")
        Machine.objects.create(external_code="ESP-002")
        self.assertEqual(Machine.objects.count(), 2)

    def test_str_retorna_external_code(self):
        m = Machine.objects.create(external_code="COLH-99")
        self.assertEqual(str(m), "COLH-99")

    def test_ativo_default_true(self):
        m = Machine.objects.create(external_code="COLH-ATIVO")
        self.assertTrue(m.ativo)


# ---------------------------------------------------------------------------
# Testes do Command backfill_machines
# ---------------------------------------------------------------------------

class TestBackfillMachines(TestCase):
    """
    Critérios de aceite:
    1. Dados sujos (espaços, capitalização mista) convergem para o mesmo Machine.
    2. Rodar o command duas vezes não duplica registros (idempotência).
    3. Entradas vazias/nulas são ignoradas silenciosamente.
    """

    def _run_backfill(self) -> str:
        """Executa o command e retorna o stdout capturado."""
        out = StringIO()
        call_command("backfill_machines", stdout=out)
        return out.getvalue()

    # --- Normalização e unicidade ---

    def test_ids_sujos_geram_um_unico_machine(self):
        """
        ' maq-01', 'MAQ-01  ' e 'maq-01' todos normalizam para 'MAQ-01'.
        Deve existir exatamente 1 Machine com external_code='MAQ-01'.
        """
        _criar_leitura(" maq-01")
        _criar_leitura("MAQ-01  ")
        _criar_leitura("maq-01")

        self._run_backfill()

        self.assertEqual(Machine.objects.filter(external_code="MAQ-01").count(), 1)
        self.assertEqual(Machine.objects.count(), 1)

    def test_ids_distintos_geram_machines_separadas(self):
        _criar_leitura("ESP-A")
        _criar_leitura("ESP-B")
        _criar_leitura("ESP-C")

        self._run_backfill()

        self.assertEqual(Machine.objects.count(), 3)

    # --- Idempotência ---

    def test_segunda_execucao_nao_duplica(self):
        """
        Rodar backfill duas vezes com os mesmos dados de entrada não deve
        criar registros adicionais.
        """
        _criar_leitura("COLH-01")
        _criar_leitura("COLH-02")

        self._run_backfill()
        contagem_apos_primeira = Machine.objects.count()

        self._run_backfill()
        contagem_apos_segunda = Machine.objects.count()

        self.assertEqual(contagem_apos_primeira, contagem_apos_segunda)
        self.assertEqual(contagem_apos_segunda, 2)

    def test_terceira_execucao_nao_duplica(self):
        """Garantia extra: N execuções são seguras."""
        _criar_leitura("FROTA-X")

        for _ in range(3):
            self._run_backfill()

        self.assertEqual(Machine.objects.count(), 1)

    # --- Entradas vazias ---

    def test_maquina_id_vazio_e_ignorado(self):
        """IDs nulos ou compostos de espaços não geram Machine."""
        _criar_leitura("   ")   # espaços apenas — deve ser ignorado
        _criar_leitura("COLH-VALIDA")

        self._run_backfill()

        # Apenas o ID válido deve ter gerado um Machine
        self.assertFalse(Machine.objects.filter(external_code="").exists())
        self.assertTrue(Machine.objects.filter(external_code="COLH-VALIDA").exists())
        self.assertEqual(Machine.objects.count(), 1)

    # --- Saída do command ---

    def test_output_contem_resumo(self):
        """O stdout do command deve conter as linhas de sumário esperadas."""
        _criar_leitura("COLH-TEST")
        output = self._run_backfill()

        self.assertIn("Total de IDs lidos", output)
        self.assertIn("Machines criadas", output)
        self.assertIn("Já existentes", output)
        self.assertIn("Ignorados (vazios)", output)

    def test_output_segunda_execucao_indica_existente(self):
        """Na segunda execução, o Machine já existe e não é criado novamente."""
        _criar_leitura("REPLAY-01")
        self._run_backfill()

        out = self._run_backfill()

        self.assertIn("Já existentes       : 1", out)
        self.assertIn("Machines criadas    : 0", out)


# ---------------------------------------------------------------------------
# Testes de Organization e Membership
# ---------------------------------------------------------------------------

class TestOrganization(TestCase):
    def test_criacao_basica(self):
        org = Organization.objects.create(nome="Fazenda Santa Clara")
        self.assertEqual(str(org), "Fazenda Santa Clara")
        self.assertIsNotNone(org.id)
        self.assertIsNotNone(org.criado_em)

    def test_id_e_uuid(self):
        org = Organization.objects.create(nome="Teste UUID")
        # UUID tem 36 chars no formato padrão
        self.assertEqual(len(str(org.id)), 36)


class TestMembership(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="farmworker", password="senha123"
        )
        self.org = Organization.objects.create(nome="Agro Corp")

    def test_criacao_com_role_padrao(self):
        mb = Membership.objects.create(user=self.user, organization=self.org)
        self.assertEqual(mb.role, "member")
        self.assertIn("farmworker", str(mb))
        self.assertIn("Agro Corp", str(mb))

    def test_criacao_com_role_admin(self):
        mb = Membership.objects.create(
            user=self.user, organization=self.org, role="admin"
        )
        self.assertEqual(mb.role, "admin")

    def test_unique_together_user_organization(self):
        Membership.objects.create(user=self.user, organization=self.org)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Membership.objects.create(user=self.user, organization=self.org)


# ---------------------------------------------------------------------------
# Testes de integração básica Machine ↔ Organization / Colheitadeira
# ---------------------------------------------------------------------------

class TestMachineFKsNullable(TestCase):
    """
    Machine pode ser criada sem FKs opcionais, pois todas são null=True.
    """

    def test_machine_sem_organization(self):
        m = Machine.objects.create(external_code="STANDALONE-01")
        self.assertIsNone(m.organization)
        self.assertIsNone(m.modelo)
        self.assertIsNone(m.colheitadeira)

    def test_machine_com_organization(self):
        org = Organization.objects.create(nome="Fazenda Modelo")
        m = Machine.objects.create(external_code="ORG-LINKED-01", organization=org)
        self.assertEqual(m.organization, org)

    def test_machine_count_bate_com_ids_distintos(self):
        """
        Critério de aceite: Machine.objects.count() == nº de maquina_id distintos
        após normalização.
        """
        ids_originais = ["COLH-A", " colh-b ", "COLH-C", "colh-a"]
        for raw_id in ids_originais:
            _criar_leitura(raw_id)

        call_command("backfill_machines", stdout=StringIO())

        # "COLH-A" e " colh-a " normalizam para "COLH-A" → 3 distintos reais
        ids_normalizados = {raw.strip().upper() for raw in ids_originais if raw.strip()}
        self.assertEqual(Machine.objects.count(), len(ids_normalizados))
