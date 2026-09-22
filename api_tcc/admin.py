from django.contrib import admin
from api_tcc import models


@admin.register(models.LeituraTelemetria)
class LeituraTelemetriaAdmin(admin.ModelAdmin):
    list_display   = ('maquina_id', 'temperatura', 'vibracao', 'rpm', 'timestamp', 'recebido_em')
    list_filter    = ('maquina_id',)
    search_fields  = ('maquina_id',)
    readonly_fields = ('id', 'recebido_em')


@admin.register(models.TelemetriaInvalida)
class TelemetriaInvalidaAdmin(admin.ModelAdmin):
    """
    Payloads rejeitados ficam aqui para auditoria.
    Útil para diagnosticar sensores com defeito ou tentativas de injeção.
    """
    list_display   = ('maquina_id', 'motivo_rejeicao', 'recebido_em')
    list_filter    = ('maquina_id',)
    search_fields  = ('maquina_id', 'motivo_rejeicao')
    readonly_fields = ('recebido_em',)


@admin.register(models.Colheitadeira)
class ColheitadeiraAdmin(admin.ModelAdmin):
    list_display = ('id', 'modelo', 'operario', 'status_de_operacao', 'estado_de_movimento')


@admin.register(models.Operario)
class OperarioAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'tempo_de_servico', 'no_banco')
    search_fields = ('nome',)


@admin.register(models.Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "external_code",
        "organization",
        "modelo",
        "colheitadeira",
        "criado_em",
        "ativo",
        "is_demo",
    )
    search_fields = ("external_code",)
    list_filter = ("ativo", "is_demo")


@admin.register(models.MachineDataHealth)
class MachineDataHealthAdmin(admin.ModelAdmin):
    list_display = (
        "machine",
        "trust_score_medio",
        "leituras_analisadas",
        "ultima_atualizacao",
    )
    search_fields = ("machine__external_code",)
    readonly_fields = (
        "machine",
        "trust_score_medio",
        "ultima_atualizacao",
        "leituras_analisadas",
        "sinais_de_alerta",
    )


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "machine",
        "tipo",
        "severidade",
        "status",
        "trust_score_herdado",
        "criado_em",
    )
    list_filter = ("tipo", "severidade", "status")
    search_fields = ("machine__external_code",)
    readonly_fields = (
        "id",
        "machine",
        "leitura_origem",
        "tipo",
        "severidade",
        "trust_score_herdado",
        "criado_em",
        "dados_contexto",
    )


@admin.register(models.Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "machine",
        "event",
        "severidade",
        "confianca",
        "status",
        "criado_em",
        "decidido_por",
        "decidido_em",
    )
    list_filter = ("severidade", "status", "criado_em")
    search_fields = ("machine__external_code", "texto", "acao_recomendada")
    ordering = ("-criado_em",)
    readonly_fields = (
        "id",
        "machine",
        "event",
        "texto",
        "acao_recomendada",
        "severidade",
        "confianca",
        "criado_em",
    )


admin.site.register(models.UnidadedeMedida)
admin.site.register(models.Marca)
admin.site.register(models.Modelo)
admin.site.register(models.Combustivel)
admin.site.register(models.PressaoPneus)
admin.site.register(models.AlturadoCorte)
admin.site.register(models.PressaodoCorte)
admin.site.register(models.TempUmi_Ambiente)
admin.site.register(models.TemperaturaMaquina)
admin.site.register(models.Transbordo)
admin.site.register(models.StatusdeOperacao)
admin.site.register(models.EstadodeMovimento)
