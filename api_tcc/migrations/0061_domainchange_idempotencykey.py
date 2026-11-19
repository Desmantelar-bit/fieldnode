import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0060_organizationtoken")]

    operations = [
        migrations.CreateModel(
            name="DomainChange",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("node_id", models.CharField(db_index=True, max_length=64)),
                ("hlc_l", models.BigIntegerField()),
                ("hlc_c", models.PositiveBigIntegerField()),
                ("entity", models.CharField(max_length=80)),
                ("entity_id", models.CharField(max_length=100)),
                ("op", models.CharField(max_length=20)),
                ("payload_hash", models.CharField(max_length=64)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={"ordering": ["hlc_l", "hlc_c", "node_id"]},
        ),
        migrations.AddConstraint(
            model_name="domainchange",
            constraint=models.UniqueConstraint(fields=("node_id", "hlc_l", "hlc_c"), name="domainchange_node_hlc_unique"),
        ),
        migrations.CreateModel(
            name="IdempotencyKey",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("key", models.CharField(max_length=128, unique=True)),
                ("request_hash", models.CharField(max_length=64)),
                ("response_status", models.PositiveSmallIntegerField(default=102)),
                ("response_payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("actor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
