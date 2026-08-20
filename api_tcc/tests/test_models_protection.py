from django.db.models.deletion import ProtectedError
from django.test import TestCase

from api_tcc.models import (
    AlturadoCorte,
    Colheitadeira,
    Combustivel,
    EstadodeMovimento,
    Marca,
    Modelo,
    Operario,
    PressaodoCorte,
    PressaoPneus,
    StatusdeOperacao,
    TemperaturaMaquina,
    TempUmi_Ambiente,
    UnidadedeMedida,
)


class ProtectedRelationsTestCase(TestCase):
    def setUp(self):
        unidade = UnidadedeMedida.objects.create(nome="Bar")
        marca = Marca.objects.create(nome="Marca de teste")
        self.modelo = Modelo.objects.create(nome="Modelo protegido", marca=marca)
        combustivel = Combustivel.objects.create(tipo="Diesel", porcentagem=100)

        self.colheitadeira = Colheitadeira.objects.create(
            modelo=self.modelo,
            maquina_id="COLH-PROTECT-01",
            combustivel=combustivel,
            pressao_pneus=PressaoPneus.objects.create(
                pressao=32, unidade_de_medida=unidade
            ),
            altura_do_corte=AlturadoCorte.objects.create(
                altura=15, unidade_de_medida=unidade
            ),
            pressao_do_corte=PressaodoCorte.objects.create(
                pressao=12, unidade_de_medida=unidade
            ),
            temp_umi_ambiente=TempUmi_Ambiente.objects.create(
                temperatura=26, umidade=60
            ),
            temperatura_maquina=TemperaturaMaquina.objects.create(
                temperatura=80, maquina=self.modelo
            ),
            operario=Operario.objects.create(
                nome="Operário de teste", tempo_de_servico=2
            ),
            status_de_operacao=StatusdeOperacao.objects.create(
                em_operacao=True, tempo_de_operacao=3
            ),
            estado_de_movimento=EstadodeMovimento.objects.create(
                em_movimento=True, velocidade=5
            ),
        )

    def test_deleting_modelo_in_use_raises_protected_error(self):
        with self.assertRaises(ProtectedError):
            self.modelo.delete()

        self.assertTrue(Modelo.objects.filter(pk=self.modelo.pk).exists())
        self.assertTrue(Colheitadeira.objects.filter(pk=self.colheitadeira.pk).exists())
