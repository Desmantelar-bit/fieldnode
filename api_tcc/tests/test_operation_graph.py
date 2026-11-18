from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from api_tcc.models import Front, Machine, MachineLink, Organization, Site
from api_tcc.services.operation_graph import (
    afetados_por,
    criar_machine_link,
    encerrar_machine_link,
)


class OperationGraphTests(TestCase):
    def setUp(self):
        self.now = timezone.now().replace(microsecond=0)
        self.org = Organization.objects.create(nome="Org A")
        self.other_org = Organization.objects.create(nome="Org B")
        self.site = Site.objects.create(organization=self.org, nome="Site A", codigo="SITE-A")
        self.front = Front.objects.create(
            organization=self.org, site=self.site, nome="Frente A", codigo="FR-A"
        )
        self.a = Machine.objects.create(
            external_code="A", organization=self.org, tipo="colhedora", site=self.site
        )
        self.b = Machine.objects.create(
            external_code="B", organization=self.org, tipo="transbordo", site=self.site
        )
        self.c = Machine.objects.create(
            external_code="C", organization=self.org, tipo="caminhao", site=self.site
        )

    def link(self, origem, destino, tipo=MachineLink.Tipo.ALIMENTA, **kwargs):
        return criar_machine_link(
            origem=origem,
            destino=destino,
            tipo=tipo,
            valido_de=kwargs.pop("valido_de", self.now),
            organization=self.org,
            **kwargs,
        )

    def test_site_and_front_keep_organization_consistency(self):
        other_site = Site.objects.create(organization=self.other_org, nome="Site B", codigo="SITE-B")
        with self.assertRaises(ValidationError):
            Front.objects.create(organization=self.org, site=other_site, nome="Inválida")

    def test_self_link_and_cross_organization_are_blocked(self):
        with self.assertRaises(ValidationError):
            self.link(self.a, self.a)
        foreign = Machine.objects.create(external_code="FOREIGN", organization=self.other_org)
        with self.assertRaises(ValidationError):
            self.link(self.a, foreign)

    def test_invalid_interval_and_overlap_are_blocked(self):
        with self.assertRaises(ValidationError):
            self.link(self.a, self.b, valido_ate=self.now - timedelta(seconds=1))
        self.link(self.a, self.b, valido_ate=self.now + timedelta(hours=1))
        with self.assertRaises(ValidationError):
            self.link(self.a, self.b, valido_de=self.now + timedelta(minutes=30))

    def test_close_then_create_later_period_preserves_history(self):
        link = self.link(self.a, self.b)
        ended = self.now + timedelta(hours=1)
        encerrar_machine_link(link, valido_ate=ended)
        later = self.link(self.a, self.b, valido_de=ended)
        self.assertEqual(MachineLink.objects.count(), 2)
        self.assertEqual(later.valido_de, ended)

    def test_bfs_respects_depth_and_returns_shortest_paths(self):
        self.link(self.a, self.b)
        self.link(self.b, self.c)
        result = afetados_por(self.a, em=self.now, max_hops=1, organization=self.org)
        self.assertEqual([item["machine"].external_code for item in result], ["B"])
        result = afetados_por(self.a, em=self.now, max_hops=2, organization=self.org)
        self.assertEqual({item["machine"].external_code for item in result}, {"B", "C"})
        self.assertEqual(next(item for item in result if item["machine"].external_code == "C")["distance"], 2)

    def test_dependency_propagates_from_dependency_to_dependent(self):
        self.link(self.b, self.a, tipo=MachineLink.Tipo.DEPENDE_DE)
        result = afetados_por(self.a, em=self.now, organization=self.org)
        self.assertEqual([item["machine"].external_code for item in result], ["B"])
        self.assertEqual(result[0]["path"][0].tipo, MachineLink.Tipo.DEPENDE_DE)

    def test_expired_and_future_links_are_ignored_consistently(self):
        self.link(
            self.a,
            self.b,
            valido_de=self.now - timedelta(hours=2),
            valido_ate=self.now - timedelta(seconds=1),
        )
        self.link(self.a, self.c, valido_de=self.now + timedelta(hours=1))
        self.assertEqual(afetados_por(self.a, em=self.now, organization=self.org), [])

    def test_cycle_does_not_repeat_or_include_origin(self):
        self.link(self.a, self.b)
        self.link(self.b, self.c)
        self.link(self.c, self.a)
        result = afetados_por(self.a, em=self.now, max_hops=5, organization=self.org)
        codes = [item["machine"].external_code for item in result]
        self.assertEqual(codes, ["B", "C"])

    def test_zero_and_negative_depth(self):
        self.assertEqual(afetados_por(self.a, em=self.now, max_hops=0, organization=self.org), [])
        with self.assertRaises(ValueError):
            afetados_por(self.a, em=self.now, max_hops=-1, organization=self.org)

    def test_unscoped_machine_cannot_be_used_for_graph(self):
        unscoped = Machine.objects.create(external_code="UNSCOPED")
        with self.assertRaises(ValidationError):
            afetados_por(unscoped)
