#!/usr/bin/env python
"""
seed_data.py — Ponto de entrada único para população de dados do FieldNode.

Uso:
    python scripts/seed_data.py --scenario simples
    python scripts/seed_data.py --scenario completo
    python scripts/seed_data.py --scenario stress

Cenários:
    simples   — 8 colheitadeiras, 96 leituras, dados fixos/determinísticos.
                Limpa o banco antes de popular. Equivale ao comportamento
                histórico de scripts/popular_banco.py.

    completo  — 10 colheitadeiras (COLH-01..10), 500 leituras com GPS real
                em área agrícola (Goiás/DF), dados aleatórios. Usa
                get_or_create (idempotente, não limpa o banco). Equivale ao
                comportamento de manage.py popular_tudo.

    stress    — 20 colheitadeiras, 200 leituras cada (4 000 leituras total),
                inseridas via bulk_create para validar performance de escrita
                em massa. Limpa os dados de stress anteriores antes de popular.
"""

import argparse
import os
import sys
import uuid
import django
from datetime import datetime, timedelta, timezone as tz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")
django.setup()

import random  # noqa: E402 — importado após django.setup() para garantir settings
from django.db import transaction  # noqa: E402
from django.utils.timezone import make_aware  # noqa: E402

from api_tcc.models import (  # noqa: E402
    AlturadoCorte,
    Colheitadeira,
    Combustivel,
    EstadodeMovimento,
    LeituraTelemetria,
    Marca,
    Modelo,
    Operario,
    PressaodoCorte,
    PressaoPneus,
    Prescricao,
    RegistroAnalise,
    StatusdeOperacao,
    TempUmi_Ambiente,
    TemperaturaMaquina,
    Transbordo,
    UnidadedeMedida,
)


# ---------------------------------------------------------------------------
# Cenário: simples
# Reproduz o comportamento de scripts/popular_banco.py (aposentado).
# 8 colheitadeiras, 12 leituras cada = 96 leituras totais. Dados fixos.
# Limpa todas as tabelas antes de popular.
# ---------------------------------------------------------------------------

def _limpar_completo():
    """Remove todos os dados na ordem correta de dependências."""
    Transbordo.objects.all().delete()
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


def scenario_simples():
    """
    8 colheitadeiras com dados fixos, 96 leituras, 8 análises, 8 prescrições.
    Limpa o banco antes de popular.
    """
    _limpar_completo()

    unidade_bar = UnidadedeMedida.objects.create(nome="bar")
    unidade_cm  = UnidadedeMedida.objects.create(nome="cm")
    UnidadedeMedida.objects.create(nome="km/h")
    UnidadedeMedida.objects.create(nome="°C")
    UnidadedeMedida.objects.create(nome="%")
    UnidadedeMedida.objects.create(nome="h")
    UnidadedeMedida.objects.create(nome="L")

    marca_case   = Marca.objects.create(nome="Case IH")
    marca_new    = Marca.objects.create(nome="New Holland")
    marca_john   = Marca.objects.create(nome="John Deere")
    marca_claas  = Marca.objects.create(nome="CLAAS")
    marca_fendt  = Marca.objects.create(nome="Fendt")
    marca_massey = Marca.objects.create(nome="Massey Ferguson")
    marca_valtra = Marca.objects.create(nome="Valtra")
    marca_agco   = Marca.objects.create(nome="AGCO")

    modelos = [
        Modelo.objects.create(nome="Axial-Flow 9240", marca=marca_case),
        Modelo.objects.create(nome="CR 8.90",         marca=marca_new),
        Modelo.objects.create(nome="S750",             marca=marca_john),
        Modelo.objects.create(nome="Lexion 8900",      marca=marca_claas),
        Modelo.objects.create(nome="Ideal 8",          marca=marca_fendt),
        Modelo.objects.create(nome="Mid-Range 7700",   marca=marca_massey),
        Modelo.objects.create(nome="T Series",         marca=marca_valtra),
        Modelo.objects.create(nome="RT 120",           marca=marca_agco),
    ]

    combustiveis = [
        Combustivel.objects.create(tipo="Diesel S10",    porcentagem=85.0),
        Combustivel.objects.create(tipo="Biodiesel B10", porcentagem=72.0),
        Combustivel.objects.create(tipo="Diesel S500",   porcentagem=90.0),
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
        AlturadoCorte.objects.create(altura= 9.0, unidade_de_medida=unidade_cm),
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
        Operario.objects.create(nome="João Silva",      tempo_de_servico= 8, no_banco=True),
        Operario.objects.create(nome="Maria Oliveira",  tempo_de_servico= 5, no_banco=True),
        Operario.objects.create(nome="Carlos Souza",    tempo_de_servico=12, no_banco=True),
        Operario.objects.create(nome="Ana Pereira",     tempo_de_servico= 3, no_banco=True),
        Operario.objects.create(nome="Pedro Costa",     tempo_de_servico=15, no_banco=True),
        Operario.objects.create(nome="Lucia Ferreira",  tempo_de_servico= 7, no_banco=True),
        Operario.objects.create(nome="Roberto Lima",    tempo_de_servico=20, no_banco=True),
        Operario.objects.create(nome="Fernanda Alves",  tempo_de_servico= 4, no_banco=True),
    ]

    status_op = [
        StatusdeOperacao.objects.create(em_operacao=True,  tempo_de_operacao= 8.5),
        StatusdeOperacao.objects.create(em_operacao=True,  tempo_de_operacao= 6.2),
        StatusdeOperacao.objects.create(em_operacao=False, tempo_de_operacao= 3.1),
        StatusdeOperacao.objects.create(em_operacao=True,  tempo_de_operacao=10.0),
        StatusdeOperacao.objects.create(em_operacao=True,  tempo_de_operacao= 5.5),
        StatusdeOperacao.objects.create(em_operacao=False, tempo_de_operacao= 2.0),
        StatusdeOperacao.objects.create(em_operacao=True,  tempo_de_operacao= 7.8),
        StatusdeOperacao.objects.create(em_operacao=True,  tempo_de_operacao= 9.2),
    ]

    estados_mov = [
        EstadodeMovimento.objects.create(em_movimento=True,  velocidade=12.0),
        EstadodeMovimento.objects.create(em_movimento=True,  velocidade= 9.5),
        EstadodeMovimento.objects.create(em_movimento=False, velocidade= 0.0),
        EstadodeMovimento.objects.create(em_movimento=True,  velocidade=15.0),
        EstadodeMovimento.objects.create(em_movimento=False, velocidade= 0.0),
        EstadodeMovimento.objects.create(em_movimento=True,  velocidade=11.0),
        EstadodeMovimento.objects.create(em_movimento=True,  velocidade= 8.0),
        EstadodeMovimento.objects.create(em_movimento=False, velocidade= 0.0),
    ]

    maquinas_ids = [
        "CASE-TC5000-01", "NEW-CR890-02",    "JOHN-S750-03",   "CLAAS-LEX-04",
        "FENDT-IDEAL-05", "MASSEY-7700-06",  "VALTRA-T210-07", "AGCO-RT120-08",
    ]

    base_lat = -15.793889
    base_lng = -47.882778
    spread   = 0.015

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
            ts          = now - timedelta(minutes=j * 10)
            temperatura = 75 + (i * 3 + j) % 8 * 2.5
            vibracao    = 0.25 + (i + j) % 5 * 0.1
            rpm         = 1500 + (i * 70 + j * 40) % 600
            leitura_lat = lat + (j % 3) * 0.0008
            leitura_lng = lng + (j % 2) * 0.001
            mid = str(uuid.uuid4())

            leituras.append(LeituraTelemetria(
                maquina_id=maquina.maquina_id,
                device_id=maquina.maquina_id,
                message_id=mid,
                temperatura=round(temperatura, 1),
                vibracao=round(vibracao, 2),
                rpm=rpm,
                latitude=round(leitura_lat, 6),
                longitude=round(leitura_lng, 6),
                timestamp=ts,
            ))

    LeituraTelemetria.objects.bulk_create(leituras)

    status_list  = ["normal", "normal", "atencao", "normal", "atencao", "normal", "normal", "atencao"]
    motivos_map  = {
        "normal":  ["Temperatura estável", "Vibração dentro do limite", "Operação estável"],
        "atencao": ["Temperatura elevada",  "RPM acima da média",        "Vibração acima do limite"],
    }
    recomendacoes = {
        "normal":  "Manutenção preventiva em 120h.",
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
                "vibracao":    round(0.25 + (i % 5) * 0.1, 2),
                "rpm":         1500 + (i * 70) % 600,
            },
            recomendacao=recomendacoes[status],
        )

    prescricoes = [
        ("Troca de filtro de óleo",  "Realizar troca do filtro de óleo e verificação do nível.",  "pendente"),
        ("Ajuste de correia",        "Ajustar tensionamento da correia do ventilador.",             "pendente"),
        ("Calibração de sensor",     "Calibrar sensor de temperatura e vibração.",                 "concluida"),
        ("Verificação hidráulica",   "Inspecionar sistema hidráulico e pressões.",                  "pendente"),
        ("Troca de filtro de ar",    "Substituir filtro de ar e limpar admissão.",                  "pendente"),
        ("Ajuste de esteira",        "Verificar tensão e desgaste da esteira.",                     "concluida"),
        ("Lubrificação geral",       "Executar lubrificação dos pontos críticos.",                  "pendente"),
        ("Verificação elétrica",     "Checar chicotes e sensores elétricos.",                       "pendente"),
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

    print("Banco populado com sucesso! (cenário: simples)")
    print(f"  Colheitadeiras : {Colheitadeira.objects.count()}")
    print(f"  Leituras       : {LeituraTelemetria.objects.count()}")
    print(f"  Análises       : {RegistroAnalise.objects.count()}")
    print(f"  Prescrições    : {Prescricao.objects.count()}")


# ---------------------------------------------------------------------------
# Cenário: completo
# Reproduz o comportamento de manage.py popular_tudo (aposentado como ponto
# de entrada standalone; o comando Django permanece disponível).
# 10 colheitadeiras COLH-01..10, 500 leituras com GPS real. Idempotente.
# ---------------------------------------------------------------------------

# Coordenadas GPS reais em área agrícola (Goiás/DF) — herdadas de popular_tudo
_GPS_BASE = [
    (-15.7939, -47.8828), (-15.7955, -47.8850), (-15.7980, -47.8885),
    (-15.8010, -47.8920), (-15.8035, -47.8895), (-15.8020, -47.8850),
    (-15.7990, -47.8815), (-15.7960, -47.8790), (-15.7940, -47.8810),
    (-15.7925, -47.8840),
]

_NUM_MAQUINAS_COMPLETO   = 10
_LEITURAS_POR_MAQUINA_COMPLETO = 50


def _resolver_dependencia_unica(model, lookup, fk_name, label):
    """Consolida duplicatas exatas e preserva referências existentes."""
    with transaction.atomic():
        registros = list(model.objects.filter(**lookup).order_by("pk"))
        if not registros:
            return model.objects.create(**lookup)

        canonico = registros[0]
        duplicatas = registros[1:]
        if duplicatas:
            ids_duplicados = [registro.pk for registro in duplicatas]
            atualizados = Colheitadeira.objects.filter(
                **{f"{fk_name}__in": ids_duplicados}
            ).update(**{fk_name: canonico.pk})
            model.objects.filter(pk__in=ids_duplicados).delete()
            print(
                f"  [corrigido] {label}: mantido pk={canonico.pk}; "
                f"removidas {len(duplicatas)} duplicata(s); "
                f"referências reatribuídas: {atualizados}"
            )
        return canonico


def scenario_completo():
    """
    10 colheitadeiras (COLH-01..10), 500 leituras com GPS real em área
    agrícola (Goiás/DF), dados aleatórios. Usa get_or_create — idempotente,
    não limpa o banco.
    """
    unidade, _ = UnidadedeMedida.objects.get_or_create(nome="bar")
    unidade = UnidadedeMedida.objects.filter(nome="bar").first()
    if not unidade:
        unidade = UnidadedeMedida.objects.create(nome="bar")

    marca_case,    _ = Marca.objects.get_or_create(nome="CASE")
    modelo_tc5000, _ = Modelo.objects.get_or_create(nome="TC5000",  defaults={"marca": marca_case})
    marca_nh,      _ = Marca.objects.get_or_create(nome="New Holland")
    modelo_cr9090, _ = Modelo.objects.get_or_create(nome="CR 9090", defaults={"marca": marca_nh})
    marca_jd,      _ = Marca.objects.get_or_create(nome="John Deere")
    modelo_s780,   _ = Modelo.objects.get_or_create(nome="S780",    defaults={"marca": marca_jd})
    combustivel = _resolver_dependencia_unica(
        Combustivel,
        {"tipo": "Diesel S10", "porcentagem": 75.0},
        "combustivel_id",
        "Combustível Diesel S10 75%",
    )
    marca_case = Marca.objects.filter(nome="CASE").first()
    if not marca_case:
        marca_case = Marca.objects.create(nome="CASE")
        
    modelo_tc5000 = Modelo.objects.filter(nome="TC5000").first()
    if not modelo_tc5000:
        modelo_tc5000 = Modelo.objects.create(nome="TC5000", marca=marca_case)
        
    marca_nh = Marca.objects.filter(nome="New Holland").first()
    if not marca_nh:
        marca_nh = Marca.objects.create(nome="New Holland")
        
    modelo_cr9090 = Modelo.objects.filter(nome="CR 9090").first()
    if not modelo_cr9090:
        modelo_cr9090 = Modelo.objects.create(nome="CR 9090", marca=marca_nh)
        
    marca_jd = Marca.objects.filter(nome="John Deere").first()
    if not marca_jd:
        marca_jd = Marca.objects.create(nome="John Deere")
        
    modelo_s780 = Modelo.objects.filter(nome="S780").first()
    if not modelo_s780:
        modelo_s780 = Modelo.objects.create(nome="S780", marca=marca_jd)
        
    combustivel = _resolver_dependencia_unica(
        Combustivel,
        {"tipo": "Diesel S10", "porcentagem": 75.0},
        "combustivel_id",
        "Combustível Diesel S10 75%",
    )

    pressao_pneus, _ = PressaoPneus.objects.get_or_create(
        pressao=28.5, defaults={"unidade_de_medida": unidade}
    )
    altura_corte, _ = AlturadoCorte.objects.get_or_create(
        altura=6.5, defaults={"unidade_de_medida": unidade}
    )
    pressao_corte, _ = PressaodoCorte.objects.get_or_create(
        pressao=120.0, defaults={"unidade_de_medida": unidade}
    )
    temp_ambiente, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=32.0, umidade=65.0)
    temp_maquina = _resolver_dependencia_unica(
        TemperaturaMaquina,
        {"temperatura": 82.0, "maquina": modelo_tc5000},
        "temperatura_maquina_id",
        "Temperatura de máquina 82.0/TC5000",
    )
    pressao_pneus = PressaoPneus.objects.filter(pressao=28.5).first()
    if not pressao_pneus:
        pressao_pneus = PressaoPneus.objects.create(pressao=28.5, unidade_de_medida=unidade)
        
    altura_corte = AlturadoCorte.objects.filter(altura=6.5).first()
    if not altura_corte:
        altura_corte = AlturadoCorte.objects.create(altura=6.5, unidade_de_medida=unidade)
        
    pressao_corte = PressaodoCorte.objects.filter(pressao=120.0).first()
    if not pressao_corte:
        pressao_corte = PressaodoCorte.objects.create(pressao=120.0, unidade_de_medida=unidade)
        
    temp_ambiente = TempUmi_Ambiente.objects.filter(temperatura=32.0, umidade=65.0).first()
    if not temp_ambiente:
        temp_ambiente = TempUmi_Ambiente.objects.create(temperatura=32.0, umidade=65.0)
        
    temp_maquina = TemperaturaMaquina.objects.filter(temperatura=82.0, maquina=modelo_tc5000).first()
    if not temp_maquina:
        temp_maquina = TemperaturaMaquina.objects.create(temperatura=82.0, maquina=modelo_tc5000)

    modelos_disp = [modelo_tc5000, modelo_cr9090, modelo_s780]

    nomes_operarios = [
        "Carlos Silva", "Ana Santos",     "Bruno Costa",     "Mariana Oliveira",
        "João Pereira", "Patricia Lima",  "Ricardo Souza",   "Fernanda Alves",
    ]
    operarios = []
    for nome in nomes_operarios:
        op, _ = Operario.objects.get_or_create(
            nome=nome,
            defaults={"tempo_de_servico": random.randint(1, 15), "no_banco": True},
        )
        op = Operario.objects.filter(nome=nome).first()
        if not op:
            op = Operario.objects.create(
                nome=nome,
                tempo_de_servico=random.randint(1, 15), 
                no_banco=True
            )
        operarios.append(op)

    for i in range(_NUM_MAQUINAS_COMPLETO):
        ativo = i < 7
        status, _ = StatusdeOperacao.objects.get_or_create(
            em_operacao=ativo,
            tempo_de_operacao=round(random.uniform(120, 1800) if ativo else random.uniform(0, 120), 1),
        )
        tempo_op = round(random.uniform(120, 1800) if ativo else random.uniform(0, 120), 1)
        status = StatusdeOperacao.objects.filter(em_operacao=ativo, tempo_de_operacao=tempo_op).first()
        if not status:
            status = StatusdeOperacao.objects.create(em_operacao=ativo, tempo_de_operacao=tempo_op)
        
        mov_flag = i < 5
        vel = round(random.uniform(4.5, 8.2), 1) if mov_flag else 0.0
        movimento = _resolver_dependencia_unica(
            EstadodeMovimento,
            {"em_movimento": mov_flag, "velocidade": vel},
            "estado_de_movimento_id",
            f"Estado de movimento {mov_flag}/{vel}",
        )
        maquina_id = f"COLH-{i+1:02d}"
        modelo = modelos_disp[i % len(modelos_disp)]
        operario = operarios[i % len(operarios)]
        colheitadeira, created = Colheitadeira.objects.get_or_create(
            maquina_id=maquina_id,
            defaults={
                "modelo":             modelo,
                "combustivel":        combustivel,
                "pressao_pneus":      pressao_pneus,
                "altura_do_corte":    altura_corte,
                "pressao_do_corte":   pressao_corte,
                "temp_umi_ambiente":  temp_ambiente,
                "temperatura_maquina": temp_maquina,
                "operario":           operario,
                "status_de_operacao": status,
                "estado_de_movimento": movimento,
            },
        )
        if created:
            print(f"  [criado] Colheitadeira {maquina_id}")

    base = make_aware(datetime.now())
    leituras_criadas = 0
    for i in range(_NUM_MAQUINAS_COMPLETO):
        maquina_id = f"COLH-{i+1:02d}"
        lat_base, lng_base = _GPS_BASE[i]
        for j in range(_LEITURAS_POR_MAQUINA_COMPLETO):
            ts  = base - timedelta(minutes=j * 5)
            lat = round(lat_base + (random.random() - 0.5) * 0.002, 6)
            lng = round(lng_base + (random.random() - 0.5) * 0.002, 6)
            mid = f"{maquina_id}-{j:04d}"
            _, created = LeituraTelemetria.objects.get_or_create(
                device_id=maquina_id,
                message_id=mid,
                defaults={
                    "maquina_id":  maquina_id,
                    "temperatura": round(random.uniform(65, 98), 1),
                    "vibracao":    round(random.uniform(0.15, 0.95), 2),
                    "rpm":         random.randint(1300, 2300),
                    "latitude":    lat,
                    "longitude":   lng,
                    "timestamp":   ts,
                },
            )
            if created:
                leituras_criadas += 1

    print("Banco populado com sucesso! (cenário: completo)")
    print(f"  Colheitadeiras : {Colheitadeira.objects.count()}")
    print(f"  Leituras criadas nesta execução : {leituras_criadas}")
    print(f"  Leituras totais                 : {LeituraTelemetria.objects.count()}")


# ---------------------------------------------------------------------------
# Cenário: stress
# 20 colheitadeiras, 200 leituras cada = 4 000 leituras via bulk_create.
# Remove apenas os dados criados por este cenário antes de popular (prefixo
# STRESS-). Não afeta dados de outros cenários.
# ---------------------------------------------------------------------------

_NUM_MAQUINAS_STRESS  = 20
_LEITURAS_POR_MAQUINA_STRESS = 200
_STRESS_PREFIX = "STRESS-"


def scenario_stress():
    """
    20 colheitadeiras (STRESS-01..20), 200 leituras cada = 4 000 leituras
    inseridas via bulk_create. Valida performance de escrita em massa.
    Remove dados de execuções anteriores deste cenário antes de popular.
    """
    # Limpar apenas dados do cenário stress (prefixo STRESS-)
    LeituraTelemetria.objects.filter(maquina_id__startswith=_STRESS_PREFIX).delete()
    Colheitadeira.objects.filter(maquina_id__startswith=_STRESS_PREFIX).delete()

    # Dependências compartilhadas (get_or_create para não colidir com outros cenários)
    unidade, _ = UnidadedeMedida.objects.get_or_create(nome="bar")
    marca, _   = Marca.objects.get_or_create(nome="STRESS-Brand")
    modelo, _  = Modelo.objects.get_or_create(
        nome="STRESS-Model", defaults={"marca": marca}
    )
    combustivel = _resolver_dependencia_unica(
        Combustivel,
        {"tipo": "Diesel S10", "porcentagem": 75.0},
        "combustivel_id",
        "Combustível Diesel S10 75%",
    )
    pressao_pneus, _ = PressaoPneus.objects.get_or_create(
        pressao=28.5, defaults={"unidade_de_medida": unidade}
    )
    altura_corte, _ = AlturadoCorte.objects.get_or_create(
        altura=6.5, defaults={"unidade_de_medida": unidade}
    )
    pressao_corte, _ = PressaodoCorte.objects.get_or_create(
        pressao=120.0, defaults={"unidade_de_medida": unidade}
    )
    temp_ambiente, _ = TempUmi_Ambiente.objects.get_or_create(temperatura=32.0, umidade=65.0)
    temp_maquina = _resolver_dependencia_unica(
        TemperaturaMaquina,
        {"temperatura": 82.0, "maquina": modelo},
        "temperatura_maquina_id",
        "Temperatura de máquina 82.0/STRESS-Model",
    )
    operario, _ = Operario.objects.get_or_create(
        nome="Operário Stress", defaults={"tempo_de_servico": 10, "no_banco": True}
    )
    status_op = _resolver_dependencia_unica(
        StatusdeOperacao,
        {"em_operacao": True, "tempo_de_operacao": 8.0},
        "status_de_operacao_id",
        "Status de operação True/8.0",
    )
    estado_mov = _resolver_dependencia_unica(
        EstadodeMovimento,
        {"em_movimento": True, "velocidade": 6.0},
        "estado_de_movimento_id",
        "Estado de movimento True/6.0",
    )
    # Dependências compartilhadas
    unidade = UnidadedeMedida.objects.filter(nome="bar").first()
    if not unidade:
        unidade = UnidadedeMedida.objects.create(nome="bar")
        
    marca = Marca.objects.filter(nome="STRESS-Brand").first()
    if not marca:
        marca = Marca.objects.create(nome="STRESS-Brand")
        
    modelo = Modelo.objects.filter(nome="STRESS-Model").first()
    if not modelo:
        modelo = Modelo.objects.create(nome="STRESS-Model", marca=marca)

    combustivel = _resolver_dependencia_unica(
        Combustivel,
        {"tipo": "Diesel S10", "porcentagem": 75.0},
        "combustivel_id",
        "Combustível Diesel S10 75%",
    )

    pressao_pneus = PressaoPneus.objects.filter(pressao=28.5).first()
    if not pressao_pneus:
        pressao_pneus = PressaoPneus.objects.create(pressao=28.5, unidade_de_medida=unidade)

    altura_corte = AlturadoCorte.objects.filter(altura=6.5).first()
    if not altura_corte:
        altura_corte = AlturadoCorte.objects.create(altura=6.5, unidade_de_medida=unidade)

    pressao_corte = PressaodoCorte.objects.filter(pressao=120.0).first()
    if not pressao_corte:
        pressao_corte = PressaodoCorte.objects.create(pressao=120.0, unidade_de_medida=unidade)

    temp_ambiente = TempUmi_Ambiente.objects.filter(temperatura=32.0, umidade=65.0).first()
    if not temp_ambiente:
        temp_ambiente = TempUmi_Ambiente.objects.create(temperatura=32.0, umidade=65.0)

    temp_maquina = _resolver_dependencia_unica(
        TemperaturaMaquina,
        {"temperatura": 82.0, "maquina": modelo},
        "temperatura_maquina_id",
        "Temperatura de máquina 82.0/STRESS-Model",
    )

    operario = Operario.objects.filter(nome="Operário Stress").first()
    if not operario:
        operario = Operario.objects.create(nome="Operário Stress", tempo_de_servico=10, no_banco=True)

    status_op = _resolver_dependencia_unica(
        StatusdeOperacao,
        {"em_operacao": True, "tempo_de_operacao": 8.0},
        "status_de_operacao_id",
        "Status de operação True/8.0",
    )

    estado_mov = _resolver_dependencia_unica(
        EstadodeMovimento,
        {"em_movimento": True, "velocidade": 6.0},
        "estado_de_movimento_id",
        "Estado de movimento True/6.0",
    )

    colheitadeiras = []
    for i in range(_NUM_MAQUINAS_STRESS):
        maquina_id = f"{_STRESS_PREFIX}{i+1:02d}"
        c = Colheitadeira.objects.create(
            maquina_id=maquina_id,
            modelo=modelo,
            combustivel=combustivel,
            pressao_pneus=pressao_pneus,
            altura_do_corte=altura_corte,
            pressao_do_corte=pressao_corte,
            temp_umi_ambiente=temp_ambiente,
            temperatura_maquina=temp_maquina,
            operario=operario,
            status_de_operacao=status_op,
            estado_de_movimento=estado_mov,
        )
        colheitadeiras.append(c)

    base = datetime.now(tz.utc)
    leituras = []
    for i, colheitadeira in enumerate(colheitadeiras):
        for j in range(_LEITURAS_POR_MAQUINA_STRESS):
            ts = base - timedelta(minutes=j * 2)
            leituras.append(LeituraTelemetria(
                maquina_id=colheitadeira.maquina_id,
                device_id=colheitadeira.maquina_id,
                message_id=str(uuid.uuid4()),
                temperatura=round(65 + (i + j) % 35, 1),
                vibracao=round(0.15 + (i + j) % 10 * 0.08, 2),
                rpm=1300 + (i * 50 + j * 10) % 1000,
                latitude=round(-15.79 + i * 0.001, 6),
                longitude=round(-47.88 + j * 0.0005, 6),
                timestamp=ts,
            ))

    LeituraTelemetria.objects.bulk_create(leituras)

    print("Banco populado com sucesso! (cenário: stress)")
    print(f"  Colheitadeiras criadas : {len(colheitadeiras)}")
    print(f"  Leituras inseridas     : {len(leituras)}")
    print(f"  Leituras totais        : {LeituraTelemetria.objects.count()}")


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

SCENARIOS = {
    "simples":  scenario_simples,
    "completo": scenario_completo,
    "stress":   scenario_stress,
}


def main():
    parser = argparse.ArgumentParser(
        description="Popula o banco do FieldNode com dados de exemplo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS.keys()),
        required=True,
        metavar="SCENARIO",
        help="Cenário de população: simples | completo | stress",
    )
    args = parser.parse_args()
    SCENARIOS[args.scenario]()


if __name__ == "__main__":
    main()
