from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title='FieldNode API',
        default_version='v1',
        description=(
            'API de telemetria e inteligência operacional do FieldNode.\n\n'
            'O FieldNode é uma plataforma AgTech que transforma dados de sensores '
            'em máquinas agrícolas em inteligência operacional acionável — '
            'detecção de anomalias, prescrições, eventos e análises em tempo real.\n\n'
            '**Autenticação:** Token via header `Authorization: Token <token>` '
            'ou `X-API-Key` para ingestão de telemetria.\n\n'
            '**Health check:** `GET /api/health/`'
        ),
        contact=openapi.Contact(email='contato@fieldnode.app'),
        license=openapi.License(name='Proprietário'),
    ),
    public=True,
)

# Configuração do Django Admin
admin.site.site_header = 'FieldNode — Inteligência Operacional'
admin.site.site_title = 'FieldNode Admin'
admin.site.index_title = 'Painel Administrativo'

urlpatterns = [
    # Raiz: redireciona para Swagger (útil para desenvolvimento)
    path('', RedirectView.as_view(url='/swagger/', permanent=False), name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('api_tcc.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
