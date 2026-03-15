from django.db import models

# Create your models here.


class UnidadedeMedida(models.Model):
    Nome = models.CharField(max_length=100)

    def __str__(self):
        return self.Nome

class Marca(models.Model):
    Nome = models.CharField(max_length=100)

    def __str__(self):
        return self.Nome

class Modelo(models.Model):
    Nome = models.CharField(max_length=100)
    Marca = models.ForeignKey(Marca, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.Nome} - {self.Marca.Nome}'

class Combustivel(models.Model):
    Tipo = models.CharField(max_length=100)
    Porcentagem = models.FloatField()

    def __str__(self):
        return f'{self.Tipo} - {self.Porcentagem}%'

class Operario(models.Model):
    Nome = models.CharField(max_length=100)
    TempodeServico = models.IntegerField()
    Nobanco = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.Nome} - {self.TempodeServico} anos - {"No banco" if self.Nobanco else "Fora do banco"}'

class PressaoPneus(models.Model):

    Pressao = models.FloatField()
    UnidadedeMedida = models.ForeignKey(UnidadedeMedida, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'Pressão: {self.Pressao} - Unidade: {self.UnidadedeMedida}'
    
class AlturadoCorte(models.Model):
    Altura = models.FloatField()
    UnidadedeMedida = models.ForeignKey(UnidadedeMedida, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'Altura: {self.Altura} - Unidade: {self.UnidadedeMedida}'

class PressaodoCorte(models.Model):
    Pressao = models.FloatField()
    UnidadedeMedida = models.ForeignKey(UnidadedeMedida, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'Pressão: {self.Pressao} - Unidade: {self.UnidadedeMedida}'
    
class TempUmi_Ambiente (models.Model):
    Temperatura = models.FloatField()
    Umidade = models.FloatField()
    
    def __str__(self):
        return f'Temperatura: {self.Temperatura} - Umidade: {self.Umidade}'
    
class Transbordo(models.Model):
    Modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    Capacidade = models.FloatField()
    
    def __str__(self):
        return f'Modelo: {self.Modelo.Nome} - Capacidade: {self.Capacidade}'

class StatusdeOperacao(models.Model):
    Em_Operacao = models.BooleanField(default=False)
    Tempo_de_Operacao = models.FloatField()

    def __str__(self):
        return f'Em Operação: {"Sim" if self.Em_Operacao else "Não"} - Tempo de Operação: {self.Tempo_de_Operacao} horas'
        
class EstadodeMovimento(models.Model):
    Em_Movimento = models.BooleanField(default=False)
    Velocidade = models.FloatField()

    def __str__(self):
        return f'Em Movimento: {"Sim" if self.Em_Movimento else "Não"} - Velocidade: {self.Velocidade} km/h'

class TemperaturaMaquina(models.Model):
    Temperatura = models.FloatField()
    Maquina = models.ForeignKey(Modelo, on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return f'Temperatura: {self.Temperatura}'
    
class Colheitadeira(models.Model):
    
    Modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE)
    Combustivel = models.ForeignKey(Combustivel, on_delete=models.CASCADE)
    PressaoPneus = models.ForeignKey(PressaoPneus, on_delete=models.CASCADE)
    AlturadoCorte = models.ForeignKey(AlturadoCorte, on_delete=models.CASCADE)
    PressaodoCorte = models.ForeignKey(PressaodoCorte, on_delete=models.CASCADE)
    TempUmi_Ambiente = models.ForeignKey(TempUmi_Ambiente, on_delete=models.CASCADE)
    TemperaturaMaquina = models.ForeignKey(TemperaturaMaquina, on_delete=models.CASCADE)
    Operario = models.ForeignKey(Operario, on_delete=models.CASCADE)
    StatusdeOperacao = models.ForeignKey(StatusdeOperacao, on_delete=models.CASCADE)
    EstadodeMovimento = models.ForeignKey(EstadodeMovimento, on_delete=models.CASCADE)
    def __str__(self):
        return f'Máquina: {self.Modelo.Nome} - Operário: {self.Operario.Nome} - Em Operação: {"Sim" if self.StatusdeOperacao.Em_Operacao else "Não"} - Em Movimento: {"Sim" if self.EstadodeMovimento.Em_Movimento else "Não"}'

