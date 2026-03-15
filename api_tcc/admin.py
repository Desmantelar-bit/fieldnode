from django.contrib import admin
from api_tcc import models

# Register your models here.

admin.site.register(models.UnidadedeMedida)
admin.site.register(models.Marca)
admin.site.register(models.Modelo)
admin.site.register(models.Combustivel)
admin.site.register(models.Operario)
admin.site.register(models.PressaoPneus)
admin.site.register(models.AlturadoCorte)
admin.site.register(models.PressaodoCorte)
admin.site.register(models.TempUmi_Ambiente)
admin.site.register(models.TemperaturaMaquina)
admin.site.register(models.Transbordo)
admin.site.register(models.StatusdeOperacao)
admin.site.register(models.EstadodeMovimento)
admin.site.register(models.Colheitadeira)