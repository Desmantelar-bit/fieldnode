"""Regressions and route inventory for organization data boundaries."""

from collections import Counter
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from rest_framework.test import APIClient

from api_tcc.models import Decision, Event, Machine, Membership, Operario, Organization


# Every route name in api_tcc.urls is explicitly classified. Router list/detail
# operations are listed separately; method coverage comes from the registered
# DRF action map and is compared below so a newly enabled method also fails.
ROUTES = {
    "api-root": "public_discovery",
    **{f"{name}-list": "global_catalog" for name in (
        "unidadedemedida", "marca", "modelo", "combustivel", "operario",
        "pressaopneus", "alturadocorte", "pressaodocorte", "tempumi_ambiente",
        "temperaturamaquina", "statusdeoperacao", "estadodemovimento", "transbordo",
        "colheitadeira",
    )},
    **{f"{name}-detail": "global_catalog" for name in (
        "unidadedemedida", "marca", "modelo", "combustivel", "operario",
        "pressaopneus", "alturadocorte", "pressaodocorte", "tempumi_ambiente",
        "temperaturamaquina", "statusdeoperacao", "estadodemovimento", "transbordo",
        "colheitadeira",
    )},
    "auth-login": "authentication", "auth-login-no-slash": "authentication",
    "auth-register": "authentication", "auth-register-no-slash": "authentication",
    "auth-logout": "authentication", "auth-logout-no-slash": "authentication",
    "auth-me": "authentication", "ingestao-telemetria": "machine_scoped_write",
    "can-motor": "machine_scoped_read", "ingestao-telemetria-lote": "machine_scoped_write",
    "anomalias": "machine_scoped_read", "ultimas-leituras": "machine_scoped_read",
    "manutencao": "machine_scoped_read", "metricas": "machine_scoped_read",
    "machine-data-health": "machine_scoped_read", "api-health": "public_health",
    "dlq-list": "administrative", "status-mqtt": "operational_status",
    "events-list": "machine_scoped_collection", "event-detail": "machine_scoped_detail",
    "decisions-list": "machine_scoped_collection", "decision-action": "machine_scoped_action",
    "prescricao": "machine_scoped_read_write", "prescricao-teste": "machine_scoped_read",
    "prescricao-lista": "machine_scoped_collection", "prescricao-maquina": "machine_scoped_read",
    "relatorio": "machine_scoped_report", "relatorio-exportar": "machine_scoped_export",
    "maquinas-posicao": "machine_scoped_collection", "mapas-demo": "demo_only",
}
ROUTES["operario-list"] = "tenant_scoped_collection"
ROUTES["operario-detail"] = "tenant_scoped_detail"
ROTAS = ROUTES

_ROUTER_BASES = (
    "unidadedemedida", "marca", "modelo", "combustivel", "operario",
    "pressaopneus", "alturadocorte", "pressaodocorte", "tempumi_ambiente",
    "temperaturamaquina", "statusdeoperacao", "estadodemovimento", "transbordo",
    "colheitadeira",
)
_ROUTER_METHODS = {
    **{f"{name}-list": {"GET", "POST"} for name in _ROUTER_BASES},
    **{f"{name}-detail": {"GET", "PUT", "PATCH", "DELETE"} for name in _ROUTER_BASES},
}
_CUSTOM_METHODS = {
    "api-root": {"GET"}, "auth-login": {"POST"}, "auth-login-no-slash": {"POST"},
    "auth-register": {"POST"}, "auth-register-no-slash": {"POST"},
    "auth-logout": {"POST"}, "auth-logout-no-slash": {"POST"}, "auth-me": {"GET"},
    "ingestao-telemetria": {"GET", "POST"}, "can-motor": {"GET"},
    "ingestao-telemetria-lote": {"POST"}, "anomalias": {"GET"},
    "ultimas-leituras": {"GET"}, "manutencao": {"GET"}, "metricas": {"GET"},
    "machine-data-health": {"GET"}, "api-health": {"GET"}, "dlq-list": {"GET"},
    "status-mqtt": {"GET"}, "events-list": {"GET"}, "event-detail": {"GET"},
    "decisions-list": {"GET"}, "decision-action": {"GET", "PATCH"},
    "prescricao": {"GET", "POST"}, "prescricao-teste": {"GET"},
    "prescricao-lista": {"GET"}, "prescricao-maquina": {"GET", "POST"},
    "relatorio": {"GET"}, "relatorio-exportar": {"GET"},
    "maquinas-posicao": {"GET"}, "mapas-demo": {"GET"},
}
OPERAÇÕES = {**_ROUTER_METHODS, **_CUSTOM_METHODS}
ROUTE_PATTERN_COUNTS = {
    **{name: 2 for name in _ROUTER_METHODS},
    "api-root": 2,
    **{name: 1 for name in _CUSTOM_METHODS if name != "api-root"},
}
ROTAS_PUBLICAS = {
    "api-root": "DRF route discovery only; returns links, no tenant records.",
    "api-health": "Health status only; no tenant records.",
    "auth-login": "Credential exchange endpoint.",
    "auth-login-no-slash": "Slashless alias of credential exchange.",
    "auth-register": "Public registration endpoint; server feature flag controls creation.",
    "auth-register-no-slash": "Slashless alias of public registration.",
    "can-motor": "Safe reads may expose only explicit demo machines while anonymous in DEMO_MODE.",
    "anomalias": "Safe reads may expose only explicit demo machines while anonymous in DEMO_MODE.",
    "ultimas-leituras": "Anonymous data is filtered to readings of explicit demo machines.",
    "manutencao": "Safe reads may expose only explicit demo machines while anonymous in DEMO_MODE.",
    "metricas": "Anonymous aggregates are derived from explicit demo machine readings.",
    "status-mqtt": "Safe reads are limited by the view's demo-machine checks in DEMO_MODE.",
    "events-list": "Anonymous event reads are scoped to explicit demo machines.",
    "event-detail": "Anonymous event detail is available only through an explicit demo machine.",
    "decisions-list": "Anonymous decision reads are scoped to explicit demo machines.",
    "decision-action": "GET only may expose explicit demo-machine decisions; PATCH requires authentication.",
    "prescricao": "GET is demo-machine scoped; POST requires authentication.",
    "prescricao-teste": "Static deprecation response (410); returns no tenant data.",
    "prescricao-lista": "Anonymous list requires a demo machine and is scoped to it.",
    "prescricao-maquina": "GET is demo-machine scoped; POST requires authentication.",
    "relatorio": "Anonymous report reads are scoped to explicit demo machine telemetry.",
    "relatorio-exportar": "Anonymous export requires an explicit demo machine.",
    "maquinas-posicao": "Anonymous positions are limited to explicit demo machines.",
    "mapas-demo": "Demo map endpoint; demo-only records.",
    "colheitadeira-list": "Anonymous list filters to explicit demo machines in DEMO_MODE.",
    "colheitadeira-detail": "Anonymous detail queryset filters to explicit demo machines in DEMO_MODE.",
}


def _api_operations(patterns, namespace=""):
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            yield from _api_operations(
                pattern.url_patterns,
                namespace + (f"{pattern.namespace}:" if pattern.namespace else ""),
            )
            continue
        if not isinstance(pattern, URLPattern):
            continue
        callback = pattern.callback
        actions = getattr(callback, "actions", None)
        view_class = getattr(callback, "cls", None)
        methods = set(actions.keys()) if actions else {
            method for method in ("get", "post", "put", "patch", "delete")
            if view_class and callable(getattr(view_class, method, None))
        }
        for method in methods & {"get", "post", "put", "patch", "delete"}:
            yield (namespace + (pattern.name or "<unnamed>"), method.upper(), pattern)


def _declared_operations():
    return {(name, method) for name, methods in OPERAÇÕES.items() for method in methods}


def _unclassified_operations(operations):
    return {(name, method) for name, method, _pattern in operations} - _declared_operations()


class TenantRouteInventoryTest(TestCase):
    def test_operation_added_without_matrix_entry_is_detected(self):
        synthetic_route = [("new-unclassified-route", "GET", None)]
        self.assertEqual(
            _unclassified_operations(synthetic_route),
            {("new-unclassified-route", "GET")},
        )

    def test_every_api_operation_has_an_explicit_matrix_classification(self):
        resolver = get_resolver("api_tcc.urls")
        operations = list(_api_operations(resolver.url_patterns))
        observed_names = {name for name, _method, _pattern in operations}
        self.assertEqual(
            observed_names - set(ROUTES), set(),
            "Rota API sem classificação na matriz ROTAS.",
        )
        self.assertEqual(
            set(ROUTES) - observed_names, set(),
            "Classificação sem rota registrada ou rota que deixou de ser coberta.",
        )
        observed_operations = {(name, method) for name, method, _pattern in operations}
        observed_pattern_counts = Counter(name for name, _method, _pattern in operations)
        expected_pattern_counts = {
            name: len(methods) * ROUTE_PATTERN_COUNTS[name]
            for name, methods in OPERAÇÕES.items()
        }
        self.assertEqual(
            observed_pattern_counts, Counter(expected_pattern_counts),
            "Quantidade de padrões/formatos registrada mudou; revise e classifique a matriz.",
        )
        self.assertEqual(
            _unclassified_operations(operations), set(),
            "Operação HTTP nova sem cobertura explícita na matriz OPERAÇÕES.",
        )
        self.assertEqual(
            _declared_operations() - observed_operations, set(),
            "Operação declarada que não existe mais ou deixou de ser descoberta.",
        )
        self.assertTrue(set(ROTAS_PUBLICAS).issubset(set(ROTAS)))
        self.assertTrue(operations)


@override_settings(DEMO_MODE=False)
class TenantCrossAccessRegressionTest(TestCase):
    def setUp(self):
        self.org_a = Organization.objects.create(nome="Organização A")
        self.org_b = Organization.objects.create(nome="Organização B")
        self.user_a = User.objects.create_user(username="tenant-a", password="secret")
        self.user_b = User.objects.create_user(username="tenant-b", password="secret")
        Membership.objects.create(user=self.user_a, organization=self.org_a, role="admin")
        Membership.objects.create(user=self.user_b, organization=self.org_b, role="admin")
        self.machine_a = Machine.objects.create(external_code="TENANT-A-01", organization=self.org_a)
        self.machine_b = Machine.objects.create(external_code="TENANT-B-01", organization=self.org_b)
        self.event_a = Event.objects.create(
            machine=self.machine_a, tipo=Event.Tipo.TEMP_ALTA,
            severidade=Event.Severidade.CRITICO, dados_contexto={"marker": "private-a"},
        )
        self.event_b = Event.objects.create(
            machine=self.machine_b, tipo=Event.Tipo.VIBRACAO_ALTA,
            severidade=Event.Severidade.ATENCAO, dados_contexto={"marker": "private-b"},
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user_b)

    def test_event_list_only_contains_the_authenticated_organizations_data(self):
        response = self.client.get(reverse("events-list"))
        self.assertEqual(response.status_code, 200)
        body = str(response.data)
        self.assertIn(str(self.event_b.id), body)
        self.assertNotIn(str(self.event_a.id), body)
        self.assertNotIn("private-a", body)

    def test_operator_collection_does_not_expose_unlinked_other_organization_data(self):
        operator = Operario.objects.create(
            nome="Operador privado A", tempo_de_servico=8, no_banco=True,
        )
        response = self.client.get(reverse("operario-list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(operator.nome, str(response.data))

    def test_event_detail_hides_another_organizations_resource(self):
        response = self.client.get(reverse("event-detail", args=[self.event_a.id]))
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("private-a", response.content.decode())

    def test_decision_detail_hides_another_organizations_resource(self):
        decision = Decision.objects.create(
            machine=self.machine_a, event=self.event_a, texto="private decision",
            acao_recomendada="private action", severidade=Event.Severidade.CRITICO,
            confianca=0.9,
        )
        response = self.client.get(reverse("decision-action", args=[decision.id]))
        self.assertEqual(response.status_code, 404)
        self.assertNotIn("private decision", response.content.decode())

    def test_decision_write_hides_cross_organization_resource_without_mutation(self):
        decision = Decision.objects.create(
            machine=self.machine_a, event=self.event_a, texto="private decision",
            acao_recomendada="private action", severidade=Event.Severidade.CRITICO,
            confianca=0.9,
        )
        response = self.client.patch(
            reverse("decision-action", args=[decision.id]),
            {"status": Decision.Status.REJEITADA}, format="json",
        )
        self.assertEqual(response.status_code, 404)
        decision.refresh_from_db()
        self.assertEqual(decision.status, Decision.Status.PENDENTE)


@override_settings(DEMO_MODE=True)
class TenantDemoBoundaryTest(TestCase):
    def test_demo_mode_does_not_expose_global_catalog_without_demo_marker(self):
        from api_tcc.models import Marca, Operario

        marca = Marca.objects.create(nome="Catalogo privado")
        Operario.objects.create(nome="Operador confidencial", tempo_de_servico=4, no_banco=True)
        client = APIClient()
        for url, marker in (
            (reverse("marca-list"), "Catalogo privado"),
            (reverse("operario-list"), "Operador confidencial"),
            (reverse("marca-detail", args=[marca.id]), "Catalogo privado"),
        ):
            with self.subTest(url=url):
                response = client.get(url)
                self.assertIn(response.status_code, {401, 403})
                self.assertNotIn(marker.encode(), response.content)
