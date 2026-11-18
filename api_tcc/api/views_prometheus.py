from django.http import HttpResponse
from django.views.decorators.http import require_GET

from api_tcc.metrics import metrics_payload, metrics_token_is_valid


@require_GET
def prometheus_metrics(request):
    """Endpoint interno para scraping; exige FIELDNODE_METRICS_TOKEN."""
    request._metrics_token = request.headers.get("X-Metrics-Token", "")
    if not metrics_token_is_valid(request):
        return HttpResponse("forbidden\n", status=403, content_type="text/plain")
    return HttpResponse(metrics_payload(), content_type="text/plain; version=0.0.4; charset=utf-8")
