"""
Migration: cria tabela TelemetriaInvalida para dead-letter de payloads inválidos.

Decisão de design: ao invés de descartar silenciosamente dados fora do range
operacional, preservamos o payload bruto para:
  1. Detectar sensores com defeito (padrão de erros por maquina_id)
  2. Auditar tentativas de injeção de dados via MQTT
  3. Acompanhar drift de sensor ao longo do tempo em produção

Alternativa descartada: usar campo booleano "valido" em LeituraTelemetria.
Problema: dados inválidos frequentemente não têm todos os campos necessários
para a tabela principal (ex: temperatura ausente), o que tornaria a abordagem
mais complexa sem ganho real.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_tcc', '0006_alter_leituratelemetria_maquina_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelemetriaInvalida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('payload_raw', models.TextField(
                    verbose_name='Payload Bruto',
                    help_text='JSON original recebido, truncado em 2000 chars'
                )),
                ('motivo_rejeicao', models.CharField(
                    max_length=500,
                    verbose_name='Motivo da Rejeição'
                )),
                ('maquina_id', models.CharField(
                    max_length=50,
                    verbose_name='ID da Máquina',
                    default='desconhecida',
                    db_index=True,
                )),
                ('recebido_em', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='Recebido em',
                    db_index=True,
                )),
            ],
            options={
                'verbose_name': 'Telemetria Inválida',
                'verbose_name_plural': 'Telemetrias Inválidas',
                'ordering': ['-recebido_em'],
            },
        ),
    ]
