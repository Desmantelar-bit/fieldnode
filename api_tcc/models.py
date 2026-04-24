from django.db import models
import uuid as uuid_lib


class UnidadedeMedida(models.Model):
    Nome = models.CharField(max_length=100, verbose_name='Nome')

    class Meta:
        verbose_name = 'Unidade de Medida'
        verbose_name_plural = 'Unidades de Medida'

    def __str__(self):
        return self.Nome


class Marca(models.Model):
    Nome = models.CharField(max_length=100, verbose_name='Nome')

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.Nome


class Modelo(models.Model):
    Nome  = models.CharField(max_length=100, verbose_name='Nome')
    Marca = models.ForeignKey(Marca, on_delete=models.PROTECT, verbose_name='Marca')

    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'

    def __str__(self):
        return f'{self.Nome} - {self.Marca.Nome}'


class Combustivel(models.Model):
    Tipo        = models.CharField(max_length=100, verbose_name='Tipo')
    Porcentagem = models.FloatField(verbose_name='Porcentagem (%)')

    class Meta:
        verbose_name = 'Combustível'
        verbose_name_plural = 'Combustíveis'

    def __str__(self):
        return f'{self.Tipo} - {self.Porcentagem}%'


class Operario(models.Model):
    Nome           = models.CharField(max_length=100, verbose_name='Nome')
    TempodeServico = models.IntegerField(verbose_name='Tempo de Serviço (anos)')
    Nobanco        = models.BooleanField(default=True, verbose_name='No Banco')

    class Meta:
        verbose_name = 'Operário'
        verbose_name_plural = 'Operários'

    def __str__(self):
        return f'{self.Nome} - {self.TempodeServico} anos - {"No banco" if self.Nobanco else "Fora do banco"}'


class PressaoPneus(models.Model):
    Pressao          = models.FloatField(verbose_name='Pressão')
    UnidadedeMedida  = models.ForeignKey(UnidadedeMedida, on_delete=models.PROTECT, verbose_name='Unidade de Medida')

    class Meta:
        verbose_name = 'Pressão dos Pneus'
        verbose_name_plural = 'Pressões dos Pneus'

    def __str__(self):
        return f'Pressão: {self.Pressao} - Unidade: {self.UnidadedeMedida}'


class AlturadoCorte(models.Model):
    Altura          = models.FloatField(verbose_name='Altura')
    UnidadedeMedida = models.ForeignKey(UnidadedeMedida, on_delete=models.PROTECT, verbose_name='Unidade de Medida')

    class Meta:
        verbose_name = 'Altura de Corte'
        verbose_name_plural = 'Alturas de Corte'

    def __str__(self):
        return f'Altura: {self.Altura} - Unidade: {self.UnidadedeMedida}'


class PressaodoCorte(models.Model):
    Pressao         = models.FloatField(verbose_name='Pressão')
    UnidadedeMedida = models.ForeignKey(UnidadedeMedida, on_delete=models.PROTECT, verbose_name='Unidade de Medida')

    class Meta:
        verbose_name = 'Pressão de Corte'
        verbose_name_plural = 'Pressões de Corte'

    def __str__(self):
        return f'Pressão: {self.Pressao} - Unidade: {self.UnidadedeMedida}'


class TempUmi_Ambiente(models.Model):
    Temperatura = models.FloatField(verbose_name='Temperatura (°C)')
    Umidade     = models.FloatField(verbose_name='Umidade (%)')

    class Meta:
        verbose_name = 'Temperatura e Umidade do Ambiente'
        verbose_name_plural = 'Temperaturas e Umidades do Ambiente'

    def __str__(self):
        return f'Temperatura: {self.Temperatura} - Umidade: {self.Umidade}'


class Transbordo(models.Model):
    Modelo     = models.ForeignKey(Modelo, on_delete=models.CASCADE, verbose_name='Modelo')
    Capacidade = models.FloatField(verbose_name='Capacidade')

    class Meta:
        verbose_name = 'Transbordo'
        verbose_name_plural = 'Transbordos'

    def __str__(self):
        return f'Modelo: {self.Modelo.Nome} - Capacidade: {self.Capacidade}'


class StatusdeOperacao(models.Model):
    Em_Operacao       = models.BooleanField(default=False, verbose_name='Em Operação')
    Tempo_de_Operacao = models.FloatField(verbose_name='Tempo de Operação (h)')

    class Meta:
        verbose_name = 'Status de Operação'
        verbose_name_plural = 'Status de Operação'

    def __str__(self):
        return f'Em Operação: {"Sim" if self.Em_Operacao else "Não"} - Tempo de Operação: {self.Tempo_de_Operacao} horas'


class EstadodeMovimento(models.Model):
    Em_Movimento = models.BooleanField(default=False, verbose_name='Em Movimento')
    Velocidade   = models.FloatField(verbose_name='Velocidade (km/h)')

    class Meta:
        verbose_name = 'Estado de Movimento'
        verbose_name_plural = 'Estados de Movimento'

    def __str__(self):
        return f'Em Movimento: {"Sim" if self.Em_Movimento else "Não"} - Velocidade: {self.Velocidade} km/h'


class TemperaturaMaquina(models.Model):
    Temperatura = models.FloatField(verbose_name='Temperatura (°C)')
    Maquina     = models.ForeignKey(Modelo, on_delete=models.PROTECT, verbose_name='Modelo da Máquina')

    class Meta:
        verbose_name = 'Temperatura da Máquina'
        verbose_name_plural = 'Temperaturas das Máquinas'

    def __str__(self):
        return f'Temperatura: {self.Temperatura}'


class Colheitadeira(models.Model):
    Modelo             = models.ForeignKey(Modelo,            on_delete=models.PROTECT, verbose_name='Modelo')
    Combustivel        = models.ForeignKey(Combustivel,       on_delete=models.PROTECT, verbose_name='Combustível')
    PressaoPneus       = models.ForeignKey(PressaoPneus,      on_delete=models.PROTECT, verbose_name='Pressão dos Pneus')
    AlturadoCorte      = models.ForeignKey(AlturadoCorte,     on_delete=models.PROTECT, verbose_name='Altura de Corte')
    PressaodoCorte     = models.ForeignKey(PressaodoCorte,    on_delete=models.PROTECT, verbose_name='Pressão de Corte')
    TempUmi_Ambiente   = models.ForeignKey(TempUmi_Ambiente,  on_delete=models.PROTECT, verbose_name='Temp./Umidade Ambiente')
    TemperaturaMaquina = models.ForeignKey(TemperaturaMaquina,on_delete=models.PROTECT, verbose_name='Temperatura da Máquina')
    Operario           = models.ForeignKey(Operario,          on_delete=models.PROTECT, verbose_name='Operário')
    StatusdeOperacao   = models.ForeignKey(StatusdeOperacao,  on_delete=models.PROTECT, verbose_name='Status de Operação')
    EstadodeMovimento  = models.ForeignKey(EstadodeMovimento, on_delete=models.PROTECT, verbose_name='Estado de Movimento')

    class Meta:
        verbose_name = 'Colheitadeira'
        verbose_name_plural = 'Colheitadeiras'

    def __str__(self):
        return f'Máquina: {self.Modelo.Nome} - Operário: {self.Operario.Nome} - Em Operação: {"Sim" if self.StatusdeOperacao.Em_Operacao else "Não"} - Em Movimento: {"Sim" if self.EstadodeMovimento.Em_Movimento else "Não"}'


class LeituraTelemetria(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    maquina_id  = models.CharField(max_length=50, verbose_name='ID da Máquina')
    temperatura = models.FloatField(verbose_name='Temperatura (°C)')
    vibracao    = models.FloatField(verbose_name='Vibração')
    rpm         = models.IntegerField(verbose_name='RPM')
    timestamp   = models.DateTimeField(verbose_name='Timestamp do Sensor')
    recebido_em = models.DateTimeField(auto_now_add=True, verbose_name='Recebido em')

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Leitura de Telemetria'
        verbose_name_plural = 'Leituras de Telemetria'

    def __str__(self):
        return f'{self.maquina_id} — {self.temperatura}°C — {self.timestamp}'

class TelemetriaInvalida(models.Model):
    """
    Dead-letter para payloads rejeitados na ingestão.
 
    Payload é preservado para auditoria e diagnóstico de sensor.
    Não usamos tabela compartilhada com LeituraTelemetria porque
    dados inválidos frequentemente chegam sem os campos obrigatórios.
    """
    payload_raw      = models.TextField(verbose_name='Payload Bruto',
                                        help_text='JSON original, truncado em 2000 chars')
    motivo_rejeicao  = models.CharField(max_length=500, verbose_name='Motivo da Rejeição')
    maquina_id       = models.CharField(max_length=50, verbose_name='ID da Máquina',
                                        default='desconhecida', db_index=True)
    recebido_em      = models.DateTimeField(auto_now_add=True, verbose_name='Recebido em',
                                            db_index=True)
 
    class Meta:
        ordering = ['-recebido_em']
        verbose_name = 'Telemetria Inválida'
        verbose_name_plural = 'Telemetrias Inválidas'
 
    def __str__(self):
        return f'{self.maquina_id} — {self.motivo_rejeicao[:60]} — {self.recebido_em}'