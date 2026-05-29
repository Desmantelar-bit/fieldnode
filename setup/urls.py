"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api_tcc.api import viewsets
from api_tcc.api.views_ingestao import AnomaliaView, HealthView, IngestaoTelemetriaView, UltimaLeituraView, ManutencaoView, MetricasView, StatusMQTTView, PrescricaoView, RelatorioView
from api_tcc import views_gps
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='API de Telemetria - TCC',
        default_version='v1',
        description='Sistema para cadastro e controle por telemetria de frota de veículos agrícolas',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='contato@telemetria.com.br'),
        license=openapi.License(name='OpenSource'),
    ),
    public=True,
)

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

urlpatterns = [  # Rota para o admin e para as APIs geradas pelos viewsets
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "api/telemetria/", IngestaoTelemetriaView.as_view(), name="ingestao-telemetria"
    ),
]

urlpatterns += [ # Rotas para a documentação Swagger e Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += [  # Rota para detecção de anomalias
    path("api/anomalias/", AnomaliaView.as_view(), name="anomalias"),
    path("api/leituras/ultimas/", UltimaLeituraView.as_view(), name="ultimas-leituras"),
    path("api/manutencao/", ManutencaoView.as_view(), name="manutencao"),
    path("api/metricas/", MetricasView.as_view(), name="metricas"),
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/status-mqtt/", StatusMQTTView.as_view(), name="status-mqtt"),
    path("api/prescricoes/", PrescricaoView.as_view(), name="prescricao"),
    path("api/relatorio/", RelatorioView.as_view(), name="relatorio"),
    path("api/maquinas/posicao/", views_gps.get_maquinas_posicao, name="maquinas-posicao"),
]
