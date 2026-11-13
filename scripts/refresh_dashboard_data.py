import os
import random
import sys
from datetime import timedelta
import django

# Setup Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from api_tcc.models import (
    Machine, Colheitadeira, LeituraTelemetria, MachineDataHealth,
    Prescricao, Event, Decision, Organization, Membership,
    StatusdeOperacao, EstadodeMovimento
)

now = timezone.now()
print(f"[INFO] Atualizando dados para horário atual: {now}...")

# 1. Certificar organização de demonstração
user = User.objects.filter(username='admin').first()
org, _ = Organization.objects.get_or_create(nome='Demo')
if user:
    Membership.objects.get_or_create(user=user, organization=org, defaults={'role': 'admin'})

# 2. Atualizar leituras e estados operacionais para COLH-01 .. COLH-10
for i in range(1, 11):
    code = f"COLH-{i:02d}"
    colh = Colheitadeira.objects.filter(maquina_id=code).first()
    machine = Machine.objects.filter(external_code=code).first()
    if not machine and colh:
        machine = Machine.objects.create(external_code=code, colheitadeira=colh, organization=org, ativo=True, is_demo=True)
    elif machine:
        machine.organization = org
        machine.is_demo = True
        machine.ativo = True
        if colh and machine.colheitadeira != colh:
            machine.colheitadeira = colh
        machine.save()

    # Atualizar status operacional
    if colh:
        em_op = (i not in [6, 9])  # 8 máquinas ativas em campo
        if colh.status_de_operacao:
            colh.status_de_operacao.em_operacao = em_op
            colh.status_de_operacao.tempo_de_operacao = round(random.uniform(250.0, 1800.0), 1)
            colh.status_de_operacao.save()

        em_mov = (i in [1, 2, 4, 5, 7, 8])
        if colh.estado_de_movimento:
            colh.estado_de_movimento.em_movimento = em_mov
            colh.estado_de_movimento.velocidade = round(random.uniform(5.5, 9.8), 1) if em_mov else 0.0
            colh.estado_de_movimento.save()

    # Atualizar timestamps de todas as 50 leituras de cada máquina
    readings = list(LeituraTelemetria.objects.filter(maquina_id=code).order_by('-id'))
    if not readings:
        print(f"  [AVISO] Nenhuma leitura encontrada para {code}")
        continue

    for idx, r in enumerate(readings[:50]):
        # Leitura 0 é 'agora', cada leitura anterior 3 minutos antes
        ts = now - timedelta(minutes=idx * 3)
        r.timestamp = ts
        r.recebido_em = ts
        r.machine = machine
        r.trust_score = round(random.uniform(0.82, 0.99), 2)
        r.save(update_fields=['timestamp', 'recebido_em', 'machine', 'trust_score'])

    # Atualizar MachineDataHealth com scores saudáveis e realistas
    if machine:
        MachineDataHealth.objects.update_or_create(
            machine=machine,
            defaults={
                'external_code': code,
                'status': 'ok',
                'trust_score_medio': round(random.uniform(0.88, 0.96), 4),
                'ultima_atualizacao': now,
                'leituras_analisadas': len(readings[:50]),
                'sinais_de_alerta': {
                    'score_baixo': False,
                    'gap_temporal': False,
                    'limite_fisico': False,
                    'salto_abrupto': False,
                    'primeira_leitura': False,
                    'valores_repetidos': False,
                    'timestamp_indisponivel': False,
                    'timestamp_fora_de_ordem': False,
                    'hora_dispositivo_nao_confiavel': False,
                    'contadores': {
                        'score_baixo': 0,
                        'gap_temporal': 0,
                        'limite_fisico': 0,
                        'salto_abrupto': 0,
                        'primeira_leitura': 0,
                        'valores_repetidos': 0,
                        'timestamp_indisponivel': 0,
                        'timestamp_fora_de_ordem': 0,
                        'hora_dispositivo_nao_confiavel': 0,
                    },
                    'ultimos_motivos': []
                }
            }
        )
    print(f"  [OK] {code}: 50 leituras e DataHealth atualizados.")

# 3. Prescrições realistas para a frota
prescricoes_data = [
    ("COLH-01", "Verificar Sistema de Arrefecimento", "Temperatura observada em patamar elevado sob alta demanda no talhão 4. Recomenda-se desobstrução e limpeza da colmeia do radiador.", "pendente"),
    ("COLH-01", "Manutenção Preventiva do Motor", "Próxima revisão em 50h: verificar filtros de combustível e óleo lubrificante.", "pendente"),
    ("COLH-02", "Calibração de Nivelamento da Plataforma", "Sensores de altura de corte com pequena oscilação. Executar calibração estática no início do próximo turno.", "pendente"),
    ("COLH-03", "Inspeção da Correia do Picador de Palha", "Vibração harmônica observada na rotação do picador. Verificar tensão da correia.", "concluida"),
    ("COLH-05", "Lubrificação dos Mancais do Rotor", "Atingido intervalo recomendado de horas trabalhadas para engraxamento dos mancais.", "pendente"),
    ("COLH-08", "Ajuste Fino das Peneiras de Limpeza", "Monitor acusou perda leve acima do nominal. Recomenda-se fechar abertura da peneira inferior em 2mm.", "pendente"),
]

for m_id, tit, desc, st in prescricoes_data:
    c = Colheitadeira.objects.filter(maquina_id=m_id).first()
    if c:
        p, created = Prescricao.objects.get_or_create(
            colheitadeira=c,
            titulo=tit,
            defaults={'descricao': desc, 'status': st}
        )
        if not created:
            p.status = st
            p.descricao = desc
            p.save()
print("[OK] Prescrições registradas com sucesso.")

# 4. Inserir Decisions e Events recentes para exibir no dashboard
c1 = Machine.objects.filter(external_code="COLH-01").first()
if c1:
    ev, _ = Event.objects.get_or_create(
        machine=c1,
        titulo="Temperatura de Óleo Próxima ao Limite de Trabalho",
        defaults={
            'severidade': 'ATENCAO',
            'detalhes': {'temperatura': 88.5, 'limite': 95.0, 'modulo': 'motor'},
            'criado_em': now - timedelta(minutes=15),
            'status': 'ABERTO'
        }
    )
    Decision.objects.get_or_create(
        machine=c1,
        texto="Recomenda-se monitorar fluxo de arrefecimento e agendar limpeza no final da jornada.",
        defaults={
            'acao_recomendada': "Inspecionar colmeia do radiador e manter rotação estável.",
            'severidade': 'ATENCAO',
            'status': 'PENDENTE',
            'criado_em': now - timedelta(minutes=10)
        }
    )

print("[SUCESSO] População completa do Dashboard concluída com dados recentes!")
