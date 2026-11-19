"""API V1 reusing the currently implemented, tested route contract."""
from django.urls import include, path

urlpatterns = [path("", include("api_tcc.urls"))]
