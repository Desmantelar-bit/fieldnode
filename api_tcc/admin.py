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
    list_display = ('id', 'Modelo', 'Operario', 'StatusdeOperacao', 'EstadodeMovimento')


@admin.register(models.Operario)
class OperarioAdmin(admin.ModelAdmin):
    list_display  = ('Nome', 'TempodeServico', 'Nobanco')
    search_fields = ('Nome',)


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
