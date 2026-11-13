import hashlib

from rest_framework.throttling import SimpleRateThrottle


class IngestaoThrottle(SimpleRateThrottle):
    scope = 'ingestao'

    def get_cache_key(self, request, view):
        authenticated_device = getattr(request, 'authenticated_ingestion_device_id', None)
        if authenticated_device:
            identity = f'device:{hashlib.sha256(authenticated_device.encode()).hexdigest()}'
        elif getattr(request.user, 'is_authenticated', False):
            identity = f'user:{request.user.pk}'
        else:
            supplied_key = request.headers.get('X-API-Key', '')
            identity = (
                f'credential:{hashlib.sha256(supplied_key.encode()).hexdigest()}'
                if supplied_key else self.get_ident(request)
            )
        return self.cache_format % {'scope': self.scope, 'ident': identity}
