from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("api_tcc", "0037_security_audit_log")]

    operations = [
        migrations.AddField("auditlog", "object_type", models.CharField(blank=True, max_length=100)),
        migrations.AddField("auditlog", "object_id", models.CharField(blank=True, max_length=100)),
        migrations.AddField("auditlog", "ip", models.GenericIPAddressField(blank=True, null=True)),
        migrations.AddField("auditlog", "user_agent", models.CharField(blank=True, max_length=512)),
        migrations.AddField("auditlog", "correlation_id", models.CharField(blank=True, db_index=True, max_length=100)),
        migrations.AddField("auditlog", "before_hash", models.CharField(blank=True, max_length=64)),
        migrations.AddField("auditlog", "after_hash", models.CharField(blank=True, max_length=64)),
        migrations.AddField("auditlog", "criado_em", models.DateTimeField(auto_now_add=True, db_index=True)),
        migrations.AddField("devicecredential", "http_key_hash", models.CharField(blank=True, max_length=64)),
        migrations.AddField("devicecredential", "http_created_at", models.DateTimeField(blank=True, null=True)),
        migrations.AddField("devicecredential", "http_revoked_at", models.DateTimeField(blank=True, null=True)),
        migrations.AddField("devicecredential", "http_last_seen_at", models.DateTimeField(blank=True, null=True)),
        migrations.AddField("devicecredential", "http_previous_key_hash", models.CharField(blank=True, max_length=64)),
        migrations.AddField("devicecredential", "http_rotation_deadline", models.DateTimeField(blank=True, null=True)),
    ]
