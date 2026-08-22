from django.urls import path, include
from rest_framework import routers
from api_tcc.api import viewsets
from api_tcc.api.views_ingestao import (
    AnomaliaView,
    IngestaoLoteView,
    IngestaoTelemetriaView,
    UltimaLeituraView,
    ManutencaoView,
    MetricasView,
    StatusMQTTView,
    PrescricaoView,
    PrescricaoListView,
    PrescricaoTesteView,
    RelatorioView,
)
from api_tcc.api.views_health import HealthView
from api_tcc.api.views_prescricao import PrescricaoView as PrescricaoMaquinaView
from api_tcc.api.views_relatorio import RelatorioExportarView
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
    path("telemetria/", IngestaoTelemetriaView.as_view(), name="ingestao-telemetria"),
    path("telemetria/lote/", IngestaoLoteView.as_view(), name="ingestao-telemetria-lote"),
    path("anomalias/", AnomaliaView.as_view(), name="anomalias"),
    path("leituras/ultimas/", UltimaLeituraView.as_view(), name="ultimas-leituras"),
    path("manutencao/", ManutencaoView.as_view(), name="manutencao"),
    path("metricas/", MetricasView.as_view(), name="metricas"),
    path("health/", HealthView.as_view(), name="api-health"),
    path("status-mqtt/", StatusMQTTView.as_view(), name="status-mqtt"),
    path("prescricoes/", PrescricaoView.as_view(), name="prescricao"),
    path("prescricoes/teste/", PrescricaoTesteView.as_view(), name="prescricao-teste"),
    path("prescricoes/lista/", PrescricaoListView.as_view(), name="prescricao-lista"),
    path("prescricoes/<str:maquina_id>/", PrescricaoMaquinaView.as_view(), name="prescricao-maquina"),
    path("relatorio/", RelatorioView.as_view(), name="relatorio"),
    path("relatorio/exportar/", RelatorioExportarView.as_view(), name="relatorio-exportar"),
    path("maquinas/posicao/", views_gps.get_maquinas_posicao, name="maquinas-posicao"),
    path("mapas/demo/", views_gps.gps_demo, name="mapas-demo"),
]
