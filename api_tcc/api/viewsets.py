from rest_framework import status, viewsets
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from api_tcc import models
from api_tcc.api import serializers


def _make_viewset(model, serializer, descriptions, queryset=None, soft_delete_field=None):
    """Gera um ModelViewSet com @swagger_auto_schema em cada action."""

    @swagger_auto_schema(operation_description=descriptions.get('list', ''), responses={200: serializer(many=True)})
    def list(self, request, *args, **kwargs):
        return super(self.__class__, self).list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description=descriptions.get('create', ''), responses={201: serializer()})
    def create(self, request, *args, **kwargs):
        return super(self.__class__, self).create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description=descriptions.get('retrieve', ''), responses={200: serializer()})
    def retrieve(self, request, *args, **kwargs):
        return super(self.__class__, self).retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description=descriptions.get('update', ''), responses={200: serializer()})
    def update(self, request, *args, **kwargs):
        return super(self.__class__, self).update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description=descriptions.get('destroy', ''), responses={204: 'No content'})
    def destroy(self, request, *args, **kwargs):
        if soft_delete_field:
            instance = self.get_object()
            setattr(instance, soft_delete_field, False)
            instance.save(update_fields=[soft_delete_field])
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super(self.__class__, self).destroy(request, *args, **kwargs)

    return type(
        model.__name__ + 'ViewSet',
        (viewsets.ModelViewSet,),
        {
            'queryset': queryset if queryset is not None else model.objects.all(),
            'serializer_class': serializer,
            'list': list,
            'create': create,
            'retrieve': retrieve,
            'update': update,
            'destroy': destroy,
        }
    )


def _desc(nome):
    return {
        'list':     f'Retorna todos os registros de {nome}.',
        'create':   f'Cria um novo registro de {nome}.',
        'retrieve': f'Retorna o registro de {nome} pelo ID.',
        'update':   f'Atualiza o registro de {nome} pelo ID.',
        'destroy':  f'Remove o registro de {nome} pelo ID.',
    }


UnidadedeMedidaViewSet  = _make_viewset(models.UnidadedeMedida,  serializers.UnidadedeMedidaSerializer,  _desc('unidade de medida'))
MarcaViewSet            = _make_viewset(models.Marca,            serializers.MarcaSerializer,            _desc('marca'))
ModeloViewSet           = _make_viewset(models.Modelo,           serializers.ModeloSerializer,           _desc('modelo'), queryset=models.Modelo.objects.select_related('marca'))
CombustivelViewSet      = _make_viewset(models.Combustivel,      serializers.CombustivelSerializer,      _desc('combustível'))
OperarioViewSet         = _make_viewset(models.Operario,         serializers.OperarioSerializer,         _desc('operário'))
PressaoPneusViewSet     = _make_viewset(models.PressaoPneus,     serializers.PressaoPneusSerializer,     _desc('pressão dos pneus'), queryset=models.PressaoPneus.objects.select_related('unidade_de_medida'))
AlturadoCorteViewSet    = _make_viewset(models.AlturadoCorte,    serializers.AlturadoCorteSerializer,    _desc('altura de corte'), queryset=models.AlturadoCorte.objects.select_related('unidade_de_medida'))
PressaodoCorteViewSet   = _make_viewset(models.PressaodoCorte,   serializers.PressaodoCorteSerializer,   _desc('pressão de corte'), queryset=models.PressaodoCorte.objects.select_related('unidade_de_medida'))
TempUmi_AmbienteViewSet = _make_viewset(models.TempUmi_Ambiente, serializers.TempUmi_AmbienteSerializer, _desc('temperatura e umidade do ambiente'))
TemperaturaMaquinaViewSet = _make_viewset(models.TemperaturaMaquina, serializers.TemperaturaMaquinaSerializer, _desc('temperatura da máquina'))
StatusdeOperacaoViewSet = _make_viewset(models.StatusdeOperacao, serializers.StatusdeOperacaoSerializer, _desc('status de operação'))
EstadodeMovimentoViewSet = _make_viewset(models.EstadodeMovimento, serializers.EstadodeMovimentoSerializer, _desc('estado de movimento'))
TransbordoViewSet       = _make_viewset(models.Transbordo,       serializers.TransbordoSerializer,       _desc('transbordo'))
ColheitadeiraViewSet    = _make_viewset(
    models.Colheitadeira,
    serializers.ColheitadeiraSerializer,
    _desc('colheitadeira'),
    queryset=models.Colheitadeira.objects.filter(ativo=True),
    soft_delete_field='ativo',
)
