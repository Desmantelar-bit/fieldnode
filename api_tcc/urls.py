from django.urls import path, include
from rest_framework import routers
from api_tcc.api.views_auth import ExpiringAuthTokenView, RegisterView, LogoutView, MeView
from api_tcc.api import viewsets
from api_tcc.api.views_can_motor import MotorCANView
from api_tcc.api.views_ingestao import IngestaoTelemetriaView
from api_tcc.api.views_lote import IngestaoLoteView
from api_tcc.api.views_leituras import UltimaLeituraView, MachineDataHealthView
from api_tcc.api.views_metricas import MetricasView
from api_tcc.api.views_status import AnomaliaView, ManutencaoView, StatusMQTTView
from api_tcc.api.views_relatorio_operacional import RelatorioView
from api_tcc.api.views_prescricoes_legadas import LegacyDecisionView, LegacyDecisionListView, LegacyDecisionTestView
from api_tcc.api.views_decision_action import DecisionActionView
from api_tcc.api.views_health import HealthView, LiveHealthView, ReadyHealthView
from api_tcc.api.views_sync import DeliveryReportView
from api_tcc.api.views_dlq import DeadLetterEntryListView
from api_tcc.api.views_events import EventListView, EventDetailView, EventHeatmapView
from api_tcc.api.views_decisions import DecisionListView
from api_tcc.api.views_search import GlobalSearchView
from api_tcc.api.views_attention import AttentionSummaryView
from api_tcc.api.views_assistant import AssistantToolView
from api_tcc.api.views_prescricao import LegacyMachineDecisionView
from api_tcc.api.views_workorders import WorkOrderDetailView, WorkOrderExportView, WorkOrderListView, ThresholdOverrideView
from api_tcc.api.views_operation_graph import OperationGraphView, OperationGraphImportView
from api_tcc.api.views_consequence import ConsequenceAssessmentView
from api_tcc.api.views_incidents import IncidentListView
from api_tcc.api.views_capabilities import MachineCapabilitiesView
from api_tcc.api.views_relatorio import RelatorioExportarView
from api_tcc.api.views_passport import PassportExportView, OrganizationTokenView
from api_tcc import views_gps

router = routers.DefaultRouter()
router.register(r'unidadedemedida', viewsets.UnidadedeMedidaViewSet, basename='unidadedemedida')
router.register(r'marca', viewsets.MarcaViewSet, basename='marca')
router.register(r'modelo', viewsets.ModeloViewSet, basename='modelo')
router.register(r'combustivel', viewsets.CombustivelViewSet, basename='combustivel')
router.register(r'operario', viewsets.OperarioViewSet, basename='operario')
router.register(r'pressaopneus', viewsets.PressaoPneusViewSet, basename='pressaopneus')
router.register(r'alturadocorte', viewsets.AlturadoCorteViewSet, basename='alturadocorte')
router.register(r'pressaodocorte', viewsets.PressaodoCorteViewSet, basename='pressaodocorte')
router.register(r'tempumi_ambiente', viewsets.TempUmi_AmbienteViewSet, basename='tempumi_ambiente')
router.register(r'temperaturamaquina', viewsets.TemperaturaMaquinaViewSet, basename='temperaturamaquina')
router.register(r'statusdeoperacao', viewsets.StatusdeOperacaoViewSet, basename='statusdeoperacao')
router.register(r'estadodemovimento', viewsets.EstadodeMovimentoViewSet, basename='estadodemovimento')
router.register(r'transbordo', viewsets.TransbordoViewSet, basename='transbordo')
router.register(r'colheitadeira', viewsets.ColheitadeiraViewSet, basename='colheitadeira')

urlpatterns = [
    path("", include(router.urls)),
    path("auth/login/", ExpiringAuthTokenView.as_view(), name="auth-login"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("telemetria/", IngestaoTelemetriaView.as_view(), name="ingestao-telemetria"),
    path("can/motor/", MotorCANView.as_view(), name="can-motor"),
    path("telemetria/lote/", IngestaoLoteView.as_view(), name="ingestao-telemetria-lote"),
    path("anomalias/", AnomaliaView.as_view(), name="anomalias"),
    path("leituras/ultimas/", UltimaLeituraView.as_view(), name="ultimas-leituras"),
    path("manutencao/", ManutencaoView.as_view(), name="manutencao"),
    path("metricas/", MetricasView.as_view(), name="metricas"),
    path("machines/<str:machine_id>/health/", MachineDataHealthView.as_view(), name="machine-data-health"),
    path("machines/<str:machine_id>/capabilities/", MachineCapabilitiesView.as_view(), name="machine-capabilities"),
    path("health/", HealthView.as_view(), name="api-health"),
    path("health/live", LiveHealthView.as_view(), name="api-health-live"),
    path("health/ready", ReadyHealthView.as_view(), name="api-health-ready"),
    path("sync/report/", DeliveryReportView.as_view(), name="sync-delivery-report"),
    path("dlq/", DeadLetterEntryListView.as_view(), name="dlq-list"),
    path("status-mqtt/", StatusMQTTView.as_view(), name="status-mqtt"),
    path("events/", EventListView.as_view(), name="events-list"),
    path("events/heatmap/", EventHeatmapView.as_view(), name="events-heatmap"),
    path("attention/summary/", AttentionSummaryView.as_view(), name="attention-summary"),
    path("assistant/tools/", AssistantToolView.as_view(), name="assistant-tools"),
    path("events/<uuid:event_id>/", EventDetailView.as_view(), name="event-detail"),
    path("events/<uuid:event_id>/consequence/", ConsequenceAssessmentView.as_view(), name="event-consequence"),
    path("incidents/", IncidentListView.as_view(), name="incidents-list"),
    path("operation-graph/", OperationGraphView.as_view(), name="operation-graph"),
    path("operation-graph/import/", OperationGraphImportView.as_view(), name="operation-graph-import"),
    path("decisions/", DecisionListView.as_view(), name="decisions-list"),
    path("search/", GlobalSearchView.as_view(), name="global-search"),
    path("decisions/<uuid:decision_id>/", DecisionActionView.as_view(), name="decision-action"),
    path("decisions/<uuid:decision_id>/threshold-override/", ThresholdOverrideView.as_view(), name="threshold-override"),
    path("workorders/", WorkOrderListView.as_view(), name="workorders-list"),
    path("workorders/<uuid:work_order_id>/", WorkOrderDetailView.as_view(), name="workorder-detail"),
    path("workorders/<uuid:work_order_id>/export.<str:export_type>", WorkOrderExportView.as_view(), name="workorder-export"),
    path("prescricoes/", LegacyDecisionView.as_view(), name="prescricao"),
    path("prescricoes/teste/", LegacyDecisionTestView.as_view(), name="prescricao-teste"),
    path("prescricoes/lista/", LegacyDecisionListView.as_view(), name="prescricao-lista"),
    path("prescricoes/<str:maquina_id>/", LegacyMachineDecisionView.as_view(), name="prescricao-maquina"),
    path("relatorio/", RelatorioView.as_view(), name="relatorio"),
    path("relatorio/exportar/", RelatorioExportarView.as_view(), name="relatorio-exportar"),
    path("maquinas/posicao/", views_gps.get_maquinas_posicao, name="maquinas-posicao"),
    path("mapas/demo/", views_gps.gps_demo, name="mapas-demo"),
    path("passport/export/", PassportExportView.as_view(), name="passport-export"),
    path("auth/organization-tokens/", OrganizationTokenView.as_view(), name="organization-tokens"),
]
