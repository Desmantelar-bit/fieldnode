from rest_framework.throttling import SimpleRateThrottle


class IngestaoThrottle(SimpleRateThrottle):
    scope = 'ingestao'

    def get_cache_key(self, request, view):
        maquina_id = (
            request.data.get('maquina_id')
            or view.kwargs.get('maquina_id')
            or 'desconhecida'
        )
        return self.cache_format % {'scope': self.scope, 'ident': maquina_id}
