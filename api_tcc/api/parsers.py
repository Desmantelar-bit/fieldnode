"""Request parsers with explicit bounds for telemetry JSON bodies."""

import io

from django.conf import settings
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser


class BoundedTelemetryJSONParser(JSONParser):
    """Limit bytes read before JSON decoding to the configured Django body cap."""

    def parse(self, stream, media_type=None, parser_context=None):
        limit = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
        body = stream.read(limit + 1)
        if len(body) > limit:
            raise ParseError(f"corpo da requisição excede o limite de {limit} bytes")
        return super().parse(io.BytesIO(body), media_type=media_type, parser_context=parser_context)
