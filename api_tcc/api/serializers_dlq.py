from rest_framework import serializers

from api_tcc.models import DeadLetterEntry


class DeadLetterEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadLetterEntry
        fields = [
            "id",
            "contexto",
            "payload_referencia",
            "motivo",
            "tentativas",
            "criado_em",
            "resolvido",
        ]
        read_only_fields = fields
