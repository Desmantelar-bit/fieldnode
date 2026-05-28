from rest_framework import serializers
from api_tcc import models

class UnidadedeMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UnidadedeMedida
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'nome': {'required': True}
        }

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Marca
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'nome': {'label': 'Nome da Marca', 'required': True}
        }
        
class ModeloSerializer(serializers.ModelSerializer):
    marca = MarcaSerializer(read_only=True)
    marca_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Marca.objects.all(), source='marca', write_only=True
    )

    class Meta:
        model = models.Modelo
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'nome': {'label': 'Nome do Modelo', 'required': True},
        }

class CombustivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Combustivel
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'tipo': {'label': 'Tipo de Combustível', 'required': True},
            'porcentagem': {'label': 'Porcentagem de Combustível', 'required': True}
        }

class OperarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Operario
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'nome': {'label': 'Nome do Operário', 'required': True},
            'tempo_de_servico': {'label': 'Tempo de Serviço', 'required': True},
            'no_banco': {'label': 'Operário no Banco', 'required': True}
        }

class PressaoPneusSerializer(serializers.ModelSerializer):
    unidade_de_medida = UnidadedeMedidaSerializer(read_only=True)
    unidade_de_medida_id = serializers.PrimaryKeyRelatedField(
        queryset=models.UnidadedeMedida.objects.all(), source='unidade_de_medida', write_only=True
    )

    class Meta:
        model = models.PressaoPneus
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'pressao': {'label': 'Pressão dos Pneus', 'required': True},
        }


class AlturadoCorteSerializer(serializers.ModelSerializer):
    unidade_de_medida = UnidadedeMedidaSerializer(read_only=True)
    unidade_de_medida_id = serializers.PrimaryKeyRelatedField(
        queryset=models.UnidadedeMedida.objects.all(), source='unidade_de_medida', write_only=True
    )

    class Meta:
        model = models.AlturadoCorte
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'altura': {'label': 'Altura de Corte', 'required': True},
        }

class PressaodoCorteSerializer(serializers.ModelSerializer):
    unidade_de_medida = UnidadedeMedidaSerializer(read_only=True)
    unidade_de_medida_id = serializers.PrimaryKeyRelatedField(
        queryset=models.UnidadedeMedida.objects.all(), source='unidade_de_medida', write_only=True
    )

    class Meta:
        model = models.PressaodoCorte
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'pressao': {'label': 'Pressão de Corte', 'required': True},
        }
        
class TempUmi_AmbienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TempUmi_Ambiente
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'temperatura': {'label': 'Temperatura do Ambiente', 'required': True},
            'umidade': {'label': 'Umidade do Ambiente', 'required': True}
        }


class TemperaturaMaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemperaturaMaquina
        fields = '__all__'   
        extra_kwargs = {
            'id': {'read_only': True},
            'temperatura': {'label': 'Temperatura da Máquina', 'required': True},
            'maquina': {'label': 'Máquina', 'required': True}
        }

class TransbordoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transbordo
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'modelo': {'label': 'Modelo da Colheitadeira', 'required': True},
            'capacidade': {'label': 'Capacidade de Transbordo', 'required': True}
        }

class StatusdeOperacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StatusdeOperacao
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'em_operacao': {'label': 'A máquina está em operação?', 'required': True},
            'tempo_de_operacao': {'label': 'Tempo de Operação (horas)', 'required': True}
        }

class EstadodeMovimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EstadodeMovimento
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'em_movimento': {'label': 'Em Movimento', 'required': True},
            'velocidade': {'label': 'Velocidade', 'required': True}
        }

class ColheitadeiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Colheitadeira
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'modelo': {'label': 'Modelo da Colheitadeira', 'required': True},
            'combustivel': {'label': 'Combustível', 'required': True},
            'pressao_pneus': {'label': 'Pressão dos Pneus', 'required': True},
            'altura_do_corte': {'label': 'Altura de Corte', 'required': True},
            'pressao_do_corte': {'label': 'Pressão de Corte', 'required': True},
            'temp_umi_ambiente': {'label': 'Temperatura e Umidade do Ambiente', 'required': True},
            'temperatura_maquina': {'label': 'Temperatura da Máquina', 'required': True},
            'operario': {'label': 'Operário', 'required': True},
            'status_de_operacao': {'label': 'Status de Operação', 'required': True},
            'estado_de_movimento': {'label': 'Estado de Movimento', 'required': True}
        }


from api_tcc.models import LeituraTelemetria

class LeituraTelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeituraTelemetria
        fields = '__all__'
        extra_kwargs = {
            'id':          {'read_only': True},
            'seq_id':      {'read_only': True},
            'recebido_em': {'read_only': True},
        }

    def validate_temperatura(self, value):
        if value > 200:
            raise serializers.ValidationError('Temperatura acima de 200°C é fisicamente inválida para operação normal.')
        return value

    def validate_vibracao(self, value):
        if value < 0:
            raise serializers.ValidationError('Vibração não pode ser negativa.')
        return value

    def validate_rpm(self, value):
        if value < 0 or value > 5000:
            raise serializers.ValidationError('RPM deve estar entre 0 e 5000.')
        return value

