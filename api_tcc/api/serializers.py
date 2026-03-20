from rest_framework import serializers
from api_tcc import models

class UnidadedeMedidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UnidadedeMedida
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Nome': {'required': True}
        }

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Marca
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Nome': {'label': 'Nome da Marca', 'required': True}
        }
            
class ModeloSerializer(serializers.ModelSerializer):
    Marca = MarcaSerializer(read_only=True)
    Marca_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Marca.objects.all(), source='Marca', write_only=True
    )

    class Meta:
        model = models.Modelo
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Nome': {'label': 'Nome do Modelo', 'required': True},
        }

class CombustivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Combustivel
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Tipo': {'label': 'Tipo de Combustível', 'required': True},
            'Porcentagem': {'label': 'Porcentagem de Combustível', 'required': True}
        }

class OperarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Operario
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Nome': {'label': 'Nome do Operário', 'required': True},
            'TempodeServico': {'label': 'Tempo de Serviço', 'required': True},
            'Nobanco': {'label': 'Operário no Banco', 'required': True}
        }

class PressaoPneusSerializer(serializers.ModelSerializer):
    UnidadedeMedida = UnidadedeMedidaSerializer(read_only=True)
    UnidadedeMedida_id = serializers.PrimaryKeyRelatedField(
        queryset=models.UnidadedeMedida.objects.all(), source='UnidadedeMedida', write_only=True
    )

    class Meta:
        model = models.PressaoPneus
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Pressao': {'label': 'Pressão dos Pneus', 'required': True},
        }


class AlturadoCorteSerializer(serializers.ModelSerializer):
    UnidadedeMedida = UnidadedeMedidaSerializer(read_only=True)
    UnidadedeMedida_id = serializers.PrimaryKeyRelatedField(
        queryset=models.UnidadedeMedida.objects.all(), source='UnidadedeMedida', write_only=True
    )

    class Meta:
        model = models.AlturadoCorte
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Altura': {'label': 'Altura de Corte', 'required': True},
        }

class PressaodoCorteSerializer(serializers.ModelSerializer):
    UnidadedeMedida = UnidadedeMedidaSerializer(read_only=True)
    UnidadedeMedida_id = serializers.PrimaryKeyRelatedField(
        queryset=models.UnidadedeMedida.objects.all(), source='UnidadedeMedida', write_only=True
    )

    class Meta:
        model = models.PressaodoCorte
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Pressao': {'label': 'Pressão de Corte', 'required': True},
        }
        
class TempUmi_AmbienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TempUmi_Ambiente
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Temperatura': {'label': 'Temperatura do Ambiente', 'required': True},
            'Umidade': {'label': 'Umidade do Ambiente', 'required': True}
        }


class TemperaturaMaquinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TemperaturaMaquina
        fields = '__all__'   
        extra_kwargs = {
            'id': {'read_only': True},
            'Temperatura': {'label': 'Temperatura da Máquina', 'required': True},
            'Maquina': {'label': 'Máquina', 'required': True}
        }

class TransbordoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transbordo
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Modelo': {'label': 'Modelo da Colheitadeira', 'required': True},
            'Capacidade': {'label': 'Capacidade de Transbordo', 'required': True}
        }

class StatusdeOperacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StatusdeOperacao
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Em_Operacao': {'label': 'A máquina está em operação?', 'required': True},
            'Tempo_de_Operacao': {'label': 'Tempo de Operação (horas)', 'required': True}
        }

class EstadodeMovimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EstadodeMovimento
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Em_Movimento': {'label': 'Em Movimento', 'required': True},
            'Velocidade': {'label': 'Velocidade', 'required': True}
        }

class ColheitadeiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Colheitadeira
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'Modelo': {'label': 'Modelo da Colheitadeira', 'required': True},
            'Combustivel': {'label': 'Combustível', 'required': True},
            'PressaoPneus': {'label': 'Pressão dos Pneus', 'required': True},
            'AlturadoCorte': {'label': 'Altura de Corte', 'required': True},
            'PressaodoCorte': {'label': 'Pressão de Corte', 'required': True},
            'TempUmi_Ambiente': {'label': 'Temperatura e Umidade do Ambiente', 'required': True},
            'TemperaturaMaquina': {'label': 'Temperatura da Máquina', 'required': True},
            'Operario': {'label': 'Operário', 'required': True},
            'StatusdeOperacao': {'label': 'Status de Operação', 'required': True},
            'EstadodeMovimento': {'label': 'Estado de Movimento', 'required': True}
        }


from api_tcc.models import LeituraTelemetria

class LeituraTelemetriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeituraTelemetria
        fields = '__all__'
        extra_kwargs = {
            'id':          {'read_only': True},
            'recebido_em': {'read_only': True},
        }

