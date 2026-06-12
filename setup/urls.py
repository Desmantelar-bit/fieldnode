from django.contrib import admin
from django.urls import path, include
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_tcc.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
