from django.contrib.auth.models import User
from django.db import models
import uuid as uuid_lib


class UnidadedeMedida(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')

    class Meta:
        verbose_name = 'Unidade de Medida'
        verbose_name_plural = 'Unidades de Medida'

    def __str__(self):
        return self.nome


class Marca(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.nome


class Modelo(models.Model):
    nome  = models.CharField(max_length=100, verbose_name='Nome')
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, verbose_name='Marca')

    class Meta:
        verbose_name = 'Modelo'
        verbose_name_plural = 'Modelos'

    def __str__(self):
        return f'{self.nome} - {self.marca.nome}'


class Combustivel(models.Model):
    tipo        = models.CharField(max_length=100, verbose_name='Tipo')
    porcentagem = models.FloatField(verbose_name='Porcentagem (%)')

    class Meta:
        verbose_name = 'Combustível'
        verbose_name_plural = 'Combustíveis'

    def __str__(self):
        return f'{self.tipo} - {self.porcentagem}%'


class Operario(models.Model):
    nome           = models.CharField(max_length=100, verbose_name='Nome')
    tempo_de_servico = models.IntegerField(verbose_name='Tempo de Serviço (anos)')
    no_banco        = models.BooleanField(default=True, verbose_name='No Banco')

    class Meta:
        verbose_name = 'Operário'
        verbose_name_plural = 'Operários'

    def __str__(self):
        return f'{self.nome} - {self.tempo_de_servico} anos - {"No banco" if self.no_banco else "Fora do banco"}'


class PressaoPneus(models.Model):
    pressao          = models.FloatField(verbose_name='Pressão')
    unidade_de_medida  = models.ForeignKey(UnidadedeMedida, on_delete=models.PROTECT, verbose_name='Unidade de Medida')

    class Meta:
        verbose_name = 'Pressão dos Pneus'
        verbose_name_plural = 'Pressões dos Pneus'

    def __str__(self):
        return f'Pressão: {self.pressao} - Unidade: {self.unidade_de_medida}'


class AlturadoCorte(models.Model):
    altura          = models.FloatField(verbose_name='Altura')
    unidade_de_medida = models.ForeignKey(UnidadedeMedida, on_delete=models.PROTECT, verbose_name='Unidade de Medida')

    class Meta:
        verbose_name = 'Altura de Corte'
        verbose_name_plural = 'Alturas de Corte'

    def __str__(self):
        return f'Altura: {self.altura} - Unidade: {self.unidade_de_medida}'


class PressaodoCorte(models.Model):
    pressao         = models.FloatField(verbose_name='Pressão')
    unidade_de_medida = models.ForeignKey(UnidadedeMedida, on_delete=models.PROTECT, verbose_name='Unidade de Medida')

    class Meta:
        verbose_name = 'Pressão de Corte'
        verbose_name_plural = 'Pressões de Corte'

    def __str__(self):
        return f'Pressão: {self.pressao} - Unidade: {self.unidade_de_medida}'


class TempUmi_Ambiente(models.Model):
    temperatura = models.FloatField(verbose_name='Temperatura (°C)')
    umidade     = models.FloatField(verbose_name='Umidade (%)')

    class Meta:
        verbose_name = 'Temperatura e Umidade do Ambiente'
        verbose_name_plural = 'Temperaturas e Umidades do Ambiente'

    def __str__(self):
        return f'Temperatura: {self.temperatura} - Umidade: {self.umidade}'


class Transbordo(models.Model):
    modelo = models.ForeignKey(Modelo, on_delete=models.PROTECT, verbose_name="Modelo")
    capacidade = models.FloatField(verbose_name='Capacidade')

    class Meta:
        verbose_name = 'Transbordo'
        verbose_name_plural = 'Transbordos'

    def __str__(self):
        return f'Modelo: {self.modelo.nome} - Capacidade: {self.capacidade}'


class StatusdeOperacao(models.Model):
    em_operacao       = models.BooleanField(default=False, verbose_name='Em Operação')
    tempo_de_operacao = models.FloatField(verbose_name='Tempo de Operação (h)')

    class Meta:
        verbose_name = 'Status de Operação'
        verbose_name_plural = 'Status de Operação'

    def __str__(self):
        return f'Em Operação: {"Sim" if self.em_operacao else "Não"} - Tempo de Operação: {self.tempo_de_operacao} horas'


class EstadodeMovimento(models.Model):
    em_movimento = models.BooleanField(default=False, verbose_name='Em Movimento')
    velocidade   = models.FloatField(verbose_name='Velocidade (km/h)')

    class Meta:
        verbose_name = 'Estado de Movimento'
        verbose_name_plural = 'Estados de Movimento'

    def __str__(self):
        return f'Em Movimento: {"Sim" if self.em_movimento else "Não"} - Velocidade: {self.velocidade} km/h'


class TemperaturaMaquina(models.Model):
    temperatura = models.FloatField(verbose_name='Temperatura (°C)')
    maquina     = models.ForeignKey(Modelo, on_delete=models.PROTECT, verbose_name='Modelo da Máquina')

    class Meta:
        verbose_name = 'Temperatura da Máquina'
        verbose_name_plural = 'Temperaturas das Máquinas'

    def __str__(self):
        return f'Temperatura: {self.temperatura}'


class Colheitadeira(models.Model):
    # Relações de catálogo/configuração: não podem remover uma máquina nem seu
    # histórico operacional quando um cadastro de referência for excluído.
    modelo             = models.ForeignKey(Modelo,            on_delete=models.PROTECT, verbose_name='Modelo')
    maquina_id         = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name='ID da Máquina (Telemetria)')
    ativo              = models.BooleanField(default=True, db_index=True, verbose_name='Ativa')
    combustivel        = models.ForeignKey(Combustivel,       on_delete=models.PROTECT, verbose_name='Combustível')
    pressao_pneus      = models.ForeignKey(PressaoPneus,      on_delete=models.PROTECT, verbose_name='Pressão dos Pneus')
    altura_do_corte    = models.ForeignKey(AlturadoCorte,     on_delete=models.PROTECT, verbose_name='Altura de Corte')
    pressao_do_corte   = models.ForeignKey(PressaodoCorte,    on_delete=models.PROTECT, verbose_name='Pressão de Corte')
    temp_umi_ambiente  = models.ForeignKey(TempUmi_Ambiente,  on_delete=models.PROTECT, verbose_name='Temp./Umidade Ambiente')
    temperatura_maquina = models.ForeignKey(TemperaturaMaquina,on_delete=models.PROTECT, verbose_name='Temperatura da Máquina')
    operario           = models.ForeignKey(Operario,          on_delete=models.PROTECT, verbose_name='Operário')
    # Embora representem estado operacional, estes registros são referenciados
    # pela máquina; PROTECT evita apagar a máquina por exclusão do snapshot.
    status_de_operacao  = models.ForeignKey(StatusdeOperacao,  on_delete=models.PROTECT, verbose_name='Status de Operação')
    estado_de_movimento = models.ForeignKey(EstadodeMovimento, on_delete=models.PROTECT, verbose_name='Estado de Movimento')

    class Meta:
        verbose_name = 'Colheitadeira'
        verbose_name_plural = 'Colheitadeiras'

    def __str__(self):
        return f'Máquina: {self.modelo.nome} - Operário: {self.operario.nome} - Em Operação: {"Sim" if self.status_de_operacao.em_operacao else "Não"} - Em Movimento: {"Sim" if self.estado_de_movimento.em_movimento else "Não"}'


class LeituraTelemetria(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    maquina_id  = models.CharField(max_length=50, verbose_name='ID da Máquina')
    temperatura = models.FloatField(verbose_name='Temperatura (°C)')
    vibracao    = models.FloatField(verbose_name='Vibração')
    rpm         = models.IntegerField(verbose_name='RPM')
    latitude = models.FloatField(verbose_name="Latitude", null=True, blank=True)
    longitude = models.FloatField(verbose_name="Longitude", null=True, blank=True)
    timestamp   = models.DateTimeField(verbose_name='Timestamp do Sensor', db_index=True)
    recebido_em = models.DateTimeField(auto_now_add=True, verbose_name='Recebido em', db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['maquina_id', '-timestamp']),
        ]
        verbose_name = 'Leitura de Telemetria'
        verbose_name_plural = 'Leituras de Telemetria'

    def __str__(self):
        return f'#{self.id} — {self.maquina_id} — {self.temperatura}°C — {self.timestamp}'

class RegistroAnalise(models.Model):
    """Snapshot auditável de uma decisão do pipeline de IA."""

    id = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    maquina_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    motivos = models.JSONField(default=list)
    metricas = models.JSONField(default=dict)
    recomendacao = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        indexes = [models.Index(fields=['maquina_id', 'criado_em'])]


class TelemetriaInvalida(models.Model):
    """
    Dead-letter para payloads rejeitados na ingestão.

    Payload é preservado para auditoria e diagnóstico de sensor.
    Não usamos tabela compartilhada com LeituraTelemetria porque
    dados inválidos frequentemente chegam sem os campos obrigatórios.
    """

    payload_raw = models.TextField(
        verbose_name="Payload Bruto", help_text="JSON original, truncado em 2000 chars"
    )
    motivo_rejeicao = models.CharField(
        max_length=500, verbose_name="Motivo da Rejeição"
    )
    maquina_id = models.CharField(
        max_length=50,
        verbose_name="ID da Máquina",
        default="desconhecida",
        db_index=True,
    )
    recebido_em = models.DateTimeField(
        auto_now_add=True, verbose_name="Recebido em", db_index=True
    )

    class Meta:
        ordering = ['-recebido_em']
        verbose_name = 'Telemetria Inválida'
        verbose_name_plural = 'Telemetrias Inválidas'

    def __str__(self):
        return f'{self.maquina_id} — {self.motivo_rejeicao[:60]} — {self.recebido_em}'


class Prescricao(models.Model):
    STATUS_CHOICES = (
        ("pendente", "Pendente"),
        ("concluida", "Concluída"),
        ("cancelada", "Cancelada"),
    )
    colheitadeira = models.ForeignKey(
        Colheitadeira, on_delete=models.PROTECT, verbose_name="Colheitadeira"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(verbose_name="Descrição")
    data_geracao = models.DateTimeField(
        auto_now_add=True, verbose_name="Data de Geração"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pendente", verbose_name="Status"
    )

    class Meta:
        verbose_name = "Prescrição"
        verbose_name_plural = "Prescrições"

    def __str__(self):
        return f"{self.titulo} - {self.colheitadeira.modelo.nome}"


# ---------------------------------------------------------------------------
# S1-T1 — Fundação Multi-tenant + Machine Canônica
# ---------------------------------------------------------------------------

class Organization(models.Model):
    """Tenant raiz: agrupa usuários e máquinas de uma mesma operação agrícola."""

    id        = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    nome      = models.CharField(max_length=255, verbose_name="Nome")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"

    def __str__(self):
        return self.nome


class Membership(models.Model):
    """Associação de um usuário Django a uma Organization com papel (role)."""

    ROLE_CHOICES = [
        ("admin",  "Administrador"),
        ("member", "Membro"),
        ("viewer", "Visualizador"),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    organization = models.ForeignKey(
        "Organization", on_delete=models.CASCADE, verbose_name="Organização"
    )
    role      = models.CharField(
        max_length=50, choices=ROLE_CHOICES, default="member", verbose_name="Papel"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Membership"
        verbose_name_plural = "Memberships"
        unique_together = [("user", "organization")]

    def __str__(self):
        return f"{self.user} → {self.organization} [{self.role}]"


class Machine(models.Model):
    """
    Entidade canônica que representa um hardware físico (ex.: ESP32/colheitadeira).

    external_code: ID do dispositivo normalizado (.strip().upper()), único no sistema.
    Serve de âncora para LeituraTelemetria (FK adicionada em S1-T2) e de ponte
    opcional para Colheitadeira (especialização agrícola) e Organization (multi-tenant).
    """

    id            = models.UUIDField(primary_key=True, default=uuid_lib.uuid4, editable=False)
    external_code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Código externo",
        help_text="ID do hardware/ESP32 normalizado (.strip().upper())",
    )

    # FKs opcionais — nullable para permitir backfill incremental
    organization  = models.ForeignKey(
        "Organization",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Organização",
    )
    modelo        = models.ForeignKey(
        "Modelo",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Modelo",
    )
    colheitadeira = models.ForeignKey(
        "Colheitadeira",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Colheitadeira vinculada",
    )

    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    ativo     = models.BooleanField(default=True, db_index=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Machine"
        verbose_name_plural = "Machines"
        ordering = ["external_code"]

    def __str__(self):
        return self.external_code
