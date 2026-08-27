#!/usr/bin/env python
"""
Popula o banco do FieldNode com dados de exemplo para apresentação/demo.
"""
import os
import sys
import django
from datetime import datetime, timedelta, timezone as tz
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

from api_tcc.models import (
    UnidadedeMedida,
    Marca,
    Modelo,
    Combustivel,
    PressaoPneus,
    AlturadoCorte,
    PressaodoCorte,
    TempUmi_Ambiente,
    TemperaturaMaquina,
    Operario,
    StatusdeOperacao,
    EstadodeMovimento,
    Colheitadeira,
    LeituraTelemetria,
    RegistroAnalise,
    Prescricao,
)


def limpar():
    Prescricao.objects.all().delete()
    RegistroAnalise.objects.all().delete()
    LeituraTelemetria.objects.all().delete()
    Colheitadeira.objects.all().delete()
    StatusdeOperacao.objects.all().delete()
    EstadodeMovimento.objects.all().delete()
    TemperaturaMaquina.objects.all().delete()
    TempUmi_Ambiente.objects.all().delete()
    PressaodoCorte.objects.all().delete()
    AlturadoCorte.objects.all().delete()
    PressaoPneus.objects.all().delete()
    Combustivel.objects.all().delete()
    Operario.objects.all().delete()
    Modelo.objects.all().delete()
    Marca.objects.all().delete()
    UnidadedeMedida.objects.all().delete()


def criar():
    limpar()

    unidade_bar = UnidadedeMedida.objects.create(nome="bar")
    unidade_cm = UnidadedeMedida.objects.create(nome="cm")
    unidade_kmh = UnidadedeMedida.objects.create(nome="km/h")
    unidade_c = UnidadedeMedida.objects.create(nome="°C")
    unidade_pct = UnidadedeMedida.objects.create(nome="%")
    unidade_h = UnidadedeMedida.objects.create(nome="h")
    unidade_l = UnidadedeMedida.objects.create(nome="L")

    marca_case = Marca.objects.create(nome="Case IH")
    marca_new = Marca.objects.create(nome="New Holland")
    marca_john = Marca.objects.create(nome="John Deere")
    marca_claas = Marca.objects.create(nome="CLAAS")
    marca_fendt = Marca.objects.create(nome="Fendt")
    marca_massey = Marca.objects.create(nome="Massey Ferguson")
    marca_valtra = Marca.objects.create(nome="Valtra")
    marca_agco = Marca.objects.create(nome="AGCO")

    modelos = [
        Modelo.objects.create(nome="Axial-Flow 9240", marca=marca_case),
        Modelo.objects.create(nome="CR 8.90", marca=marca_new),
        Modelo.objects.create(nome="S750", marca=marca_john),
        Modelo.objects.create(nome="Lexion 8900", marca=marca_claas),
        Modelo.objects.create(nome="Ideal 8", marca=marca_fendt),
        Modelo.objects.create(nome="Mid-Range 7700", marca=marca_massey),
        Modelo.objects.create(nome="T Series", marca=marca_valtra),
        Modelo.objects.create(nome="RT 120", marca=marca_agco),
    ]

    combustiveis = [
        Combustivel.objects.create(tipo="Diesel S10", porcentagem=85.0),
        Combustivel.objects.create(tipo="Biodiesel B10", porcentagem=72.0),
        Combustivel.objects.create(tipo="Diesel S500", porcentagem=90.0),
        Combustivel.objects.create(tipo="Biodiesel B20", porcentagem=65.0),
    ]

    pressoes_pneus = [
        PressaoPneus.objects.create(pressao=28.5, unidade_de_medida=unidade_bar),
        PressaoPneus.objects.create(pressao=26.0, unidade_de_medida=unidade_bar),
        PressaoPneus.objects.create(pressao=24.5, unidade_de_medida=unidade_bar),
        PressaoPneus.objects.create(pressao=27.0, unidade_de_medida=unidade_bar),
        PressaoPneus.objects.create(pressao=25.5, unidade_de_medida=unidade_bar),
        PressaoPneus.objects.create(pressao=23.0, unidade_de_medida=unidade_bar),
        PressaoPneus.objects.create(pressao=29.0, unidade_de_medida=unidade_bar),
        PressaoPneus.objects.create(pressao=26.5, unidade_de_medida=unidade_bar),
    ]

    alturas_corte = [
        AlturadoCorte.objects.create(altura=15.0, unidade_de_medida=unidade_cm),
        AlturadoCorte.objects.create(altura=12.0, unidade_de_medida=unidade_cm),
        AlturadoCorte.objects.create(altura=9.0, unidade_de_medida=unidade_cm),
        AlturadoCorte.objects.create(altura=18.0, unidade_de_medida=unidade_cm),
        AlturadoCorte.objects.create(altura=11.0, unidade_de_medida=unidade_cm),
        AlturadoCorte.objects.create(altura=14.0, unidade_de_medida=unidade_cm),
        AlturadoCorte.objects.create(altura=10.0, unidade_de_medida=unidade_cm),
        AlturadoCorte.objects.create(altura=16.0, unidade_de_medida=unidade_cm),
    ]

    pressoes_corte = [
        PressaodoCorte.objects.create(pressao=1.8, unidade_de_medida=unidade_bar),
        PressaodoCorte.objects.create(pressao=1.5, unidade_de_medida=unidade_bar),
        PressaodoCorte.objects.create(pressao=1.2, unidade_de_medida=unidade_bar),
        PressaodoCorte.objects.create(pressao=1.6, unidade_de_medida=unidade_bar),
        PressaodoCorte.objects.create(pressao=1.4, unidade_de_medida=unidade_bar),
        PressaodoCorte.objects.create(pressao=1.1, unidade_de_medida=unidade_bar),
        PressaodoCorte.objects.create(pressao=1.9, unidade_de_medida=unidade_bar),
        PressaodoCorte.objects.create(pressao=1.3, unidade_de_medida=unidade_bar),
    ]

    temps_amb = [
        TempUmi_Ambiente.objects.create(temperatura=32.0, umidade=55.0),
        TempUmi_Ambiente.objects.create(temperatura=29.5, umidade=62.0),
        TempUmi_Ambiente.objects.create(temperatura=31.0, umidade=58.0),
        TempUmi_Ambiente.objects.create(temperatura=28.0, umidade=70.0),
        TempUmi_Ambiente.objects.create(temperatura=33.5, umidade=48.0),
        TempUmi_Ambiente.objects.create(temperatura=30.0, umidade=65.0),
        TempUmi_Ambiente.objects.create(temperatura=27.5, umidade=75.0),
        TempUmi_Ambiente.objects.create(temperatura=34.0, umidade=45.0),
    ]

    temps_maquina = [
        TemperaturaMaquina.objects.create(temperatura=92.0, maquina=modelos[0]),
        TemperaturaMaquina.objects.create(temperatura=88.5, maquina=modelos[1]),
        TemperaturaMaquina.objects.create(temperatura=95.0, maquina=modelos[2]),
        TemperaturaMaquina.objects.create(temperatura=90.0, maquina=modelos[3]),
        TemperaturaMaquina.objects.create(temperatura=87.0, maquina=modelos[4]),
        TemperaturaMaquina.objects.create(temperatura=93.5, maquina=modelos[5]),
        TemperaturaMaquina.objects.create(temperatura=89.0, maquina=modelos[6]),
        TemperaturaMaquina.objects.create(temperatura=96.0, maquina=modelos[7]),
    ]

    operarios = [
        Operario.objects.create(nome="João Silva", tempo_de_servico=8, no_banco=True),
        Operario.objects.create(nome="Maria Oliveira", tempo_de_servico=5, no_banco=True),
        Operario.objects.create(nome="Carlos Souza", tempo_de_servico=12, no_banco=True),
        Operario.objects.create(nome="Ana Pereira", tempo_de_servico=3, no_banco=True),
        Operario.objects.create(nome="Pedro Costa", tempo_de_servico=15, no_banco=True),
        Operario.objects.create(nome="Lucia Ferreira", tempo_de_servico=7, no_banco=True),
        Operario.objects.create(nome="Roberto Lima", tempo_de_servico=20, no_banco=True),
        Operario.objects.create(nome="Fernanda Alves", tempo_de_servico=4, no_banco=True),
    ]

    status_op = [
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=8.5),
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=6.2),
        StatusdeOperacao.objects.create(em_operacao=False, tempo_de_operacao=3.1),
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=10.0),
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=5.5),
        StatusdeOperacao.objects.create(em_operacao=False, tempo_de_operacao=2.0),
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=7.8),
        StatusdeOperacao.objects.create(em_operacao=True, tempo_de_operacao=9.2),
    ]

    estados_mov = [
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=12.0),
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=9.5),
        EstadodeMovimento.objects.create(em_movimento=False, velocidade=0.0),
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=15.0),
        EstadodeMovimento.objects.create(em_movimento=False, velocidade=0.0),
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=11.0),
        EstadodeMovimento.objects.create(em_movimento=True, velocidade=8.0),
        EstadodeMovimento.objects.create(em_movimento=False, velocidade=0.0),
    ]

    maquinas_ids = [
        "CASE-TC5000-01",
        "NEW-CR890-02",
        "JOHN-S750-03",
        "CLAAS-LEX-04",
        "FENDT-IDEAL-05",
        "MASSEY-7700-06",
        "VALTRA-T210-07",
        "AGCO-RT120-08",
    ]

    base_lat = -15.793889
    base_lng = -47.882778
    spread = 0.015

    colheitadeiras = []
    for i in range(8):
        row = i % 4
        col = i // 4
        lat = base_lat + (row - 1.5) * spread + (i % 3) * 0.003
        lng = base_lng + (col - 0.5) * spread + (i % 2) * 0.004

        c = Colheitadeira.objects.create(
            modelo=modelos[i],
            maquina_id=maquinas_ids[i],
            ativo=True,
            combustivel=combustiveis[i % len(combustiveis)],
            pressao_pneus=pressoes_pneus[i],
            altura_do_corte=alturas_corte[i],
            pressao_do_corte=pressoes_corte[i],
            temp_umi_ambiente=temps_amb[i],
            temperatura_maquina=temps_maquina[i],
            operario=operarios[i],
            status_de_operacao=status_op[i],
            estado_de_movimento=estados_mov[i],
        )
        colheitadeiras.append((c, lat, lng))

    leituras = []
    now = datetime.now(tz.utc)
    for i in range(8):
        maquina, lat, lng = colheitadeiras[i]
        for j in range(12):
            ts = now - timedelta(minutes=j * 10)
            temperatura = 75 + (i * 3 + j) % 8 * 2.5
            vibracao = 0.25 + (i + j) % 5 * 0.1
            rpm = 1500 + (i * 70 + j * 40) % 600
            leitura_lat = lat + (j % 3) * 0.0008
            leitura_lng = lng + (j % 2) * 0.001

            leituras.append(
                LeituraTelemetria(
                    maquina_id=maquina.maquina_id,
                    temperatura=round(temperatura, 1),
                    vibracao=round(vibracao, 2),
                    rpm=rpm,
                    latitude=round(leitura_lat, 6),
                    longitude=round(leitura_lng, 6),
                    timestamp=ts,
                )
            )

    LeituraTelemetria.objects.bulk_create(leituras)

    status_list = ["normal", "normal", "atencao", "normal", "atencao", "normal", "normal", "atencao"]
    motivos_map = {
        "normal": ["Temperatura estável", "Vibração dentro do limite", "Operação estável"],
        "atencao": ["Temperatura elevada", "RPM acima da média", "Vibração acima do limite"],
    }
    recomendacoes = {
        "normal": "Manutenção preventiva em 120h.",
        "atencao": "Verificar sistema de arrefecimento.",
    }

    for i in range(8):
        maquina, _, _ = colheitadeiras[i]
        status = status_list[i]
        RegistroAnalise.objects.create(
            maquina_id=maquina.maquina_id,
            status=status,
            motivos=motivos_map[status],
            metricas={
                "temperatura": float(temps_maquina[i].temperatura),
                "vibracao": round(0.25 + (i % 5) * 0.1, 2),
                "rpm": 1500 + (i * 70) % 600,
            },
            recomendacao=recomendacoes[status],
        )

    prescricoes = [
        ("Troca de filtro de óleo", "Realizar troca do filtro de óleo e verificação do nível.", "pendente"),
        ("Ajuste de correia", "Ajustar tensionamento da correia do ventilador.", "pendente"),
        ("Calibração de sensor", "Calibrar sensor de temperatura e vibração.", "concluida"),
        ("Verificação hidráulica", "Inspecionar sistema hidráulico e pressões.", "pendente"),
        ("Troca de filtro de ar", "Substituir filtro de ar e limpar admissão.", "pendente"),
        ("Ajuste de esteira", "Verificar tensão e desgaste da esteira.", "concluida"),
        ("Lubrificação geral", "Executar lubrificação dos pontos críticos.", "pendente"),
        ("Verificação elétrica", "Checar chicotes e sensores elétricos.", "pendente"),
    ]

    for i in range(8):
        maquina, _, _ = colheitadeiras[i]
        titulo, descricao, status_presc = prescricoes[i]
        Prescricao.objects.create(
            colheitadeira=maquina,
            titulo=titulo,
            descricao=descricao,
            status=status_presc,
        )

    print(" Banco populado com sucesso!")
    print(f" Colheitadeiras: {Colheitadeira.objects.count()}")
    print(f" Leituras: {LeituraTelemetria.objects.count()}")
    print(f" Análises: {RegistroAnalise.objects.count()}")
    print(f" Prescrições: {Prescricao.objects.count()}")


if __name__ == "__main__":
    criar()
