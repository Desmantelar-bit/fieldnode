import csv
import io
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from api_tcc.models import LeituraTelemetria, Prescricao, Colheitadeira
from api_tcc.ia.anomalias import detectar_anomalias
from api_tcc.ia.manutencao import prever_manutencao
from api_tcc.ia.prescricoes import gerar_prescricao

def preparar_dados_relatorio(maquina_id, data_inicio=None, data_fim=None):
    """
    Extrai e processa os dados necessários para qualquer formato de relatório.
    """
    if not data_fim:
        data_fim = timezone.now()
    if not data_inicio:
        data_inicio = data_fim - timedelta(days=7)

    queryset = LeituraTelemetria.objects.filter(
        maquina_id=maquina_id,
        timestamp__gte=data_inicio,
        timestamp__lte=data_fim
    ).order_by('timestamp')

    if not queryset.exists():
        return None, data_inicio, data_fim

    leituras = list(queryset)
    temperaturas = [l.temperatura for l in leituras]
    vibracoes = [l.vibracao for l in leituras]
    rpms = [l.rpm for l in leituras]

    stats = {
        'total_leituras': len(leituras),
        'temp_media': sum(temperaturas) / len(temperaturas) if temperaturas else 0,
        'temp_max': max(temperaturas) if temperaturas else 0,
        'temp_min': min(temperaturas) if temperaturas else 0,
        'vib_media': sum(vibracoes) / len(vibracoes) if vibracoes else 0,
        'vib_max': max(vibracoes) if vibracoes else 0,
        'vib_min': min(vibracoes) if vibracoes else 0,
        'rpm_media': sum(rpms) / len(rpms) if rpms else 0,
        'rpm_max': max(rpms) if rpms else 0,
        'rpm_min': min(rpms) if rpms else 0,
    }

    colheitadeira = Colheitadeira.objects.filter(modelo__nome=maquina_id).first()
    prescricoes = []
    if colheitadeira:
        prescricoes = list(Prescricao.objects.filter(
            colheitadeira=colheitadeira,
            data_geracao__gte=data_inicio,
            data_geracao__lte=data_fim
        ).order_by('-data_geracao'))

    return {
        'stats': stats,
        'leituras': leituras,
        'prescricoes': prescricoes,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    }, data_inicio, data_fim


def gerar_relatorio_completo(maquina_id, data_inicio=None, data_fim=None, formato='csv'):
    """
    Gera um relatório completo com dados de telemetria, anomalias, manutenção e prescrições.

    Args:
        maquina_id: ID da máquina
        data_inicio: Data de início (opcional)
        data_fim: Data de fim (opcional)
        formato: Formato de saída ('csv' ou 'txt')

    Returns:
        HttpResponse com o relatório no formato solicitado
    """
    dados, data_inicio, data_fim = preparar_dados_relatorio(maquina_id, data_inicio, data_fim)

    if not dados:
        # Retornar resposta vaziosa se não houver dados
        if formato == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="relatorio_vazio_{maquina_id}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Mensagem'])
            writer.writerow(['Nenhum dado de telemetria encontrado para o período especificado.'])
            return response
        else:  # formato texto
            buf = io.StringIO()
            buf.write(f"RELATÓRIO DE TELEMETRIA - MÁQUINA {maquina_id}\n")
            buf.write("=" * 50 + "\n")
            buf.write(f"Período: {data_inicio.strftime('%d/%m/%Y %H:%M')} a {data_fim.strftime('%d/%m/%Y %H:%M')}\n")
            buf.write("\nSTATUS: Nenhum dado encontrado\n")
            buf.write("Não há leituras de telemetria para este período.\n")
            response = HttpResponse(buf.getvalue(), content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="relatorio_{maquina_id}.txt"'
            return response

    # Gerar relatório no formato solicitado
    if formato == 'csv':
        return _gerar_relatorio_csv(
            maquina_id, data_inicio, data_fim,
            dados['stats'], dados['leituras'], dados['prescricoes']
        )
    else:  # formato texto padrão
        return _gerar_relatorio_txt(
            maquina_id, data_inicio, data_fim,
            dados['stats'], dados['leituras'], dados['prescricoes']
        )


def _gerar_relatorio_csv(maquina_id, data_inicio, data_fim, stats, leituras, prescricoes):
    """Gera relatório em formato CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="relatorio_completo_{maquina_id}_{data_inicio.strftime("%Y%m%d")}_{data_fim.strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response, lineterminator='\n')

    # Cabeçalho do relatório
    writer.writerow(['Relatório Completo de Telemetria - FieldNode'])
    writer.writerow([f'Máquina: {maquina_id}'])
    writer.writerow([f'Período: {data_inicio.strftime("%d/%m/%Y %H:%M")} a {data_fim.strftime("%d/%m/%Y %H:%M")}'])
    writer.writerow([f'Gerado em: {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}'])
    writer.writerow([])  # Linha vazia

    # Seção de estatísticas de telemetria
    writer.writerow(['ESTATÍSTICAS DE TELEMETRIA'])
    writer.writerow(['Métrica', 'Valor'])
    writer.writerow(['Total de Leituras', stats['total_leituras']])
    writer.writerow(['Temperatura Média (°C)', f"{stats['temp_media']:.2f}"])
    writer.writerow(['Temperatura Máxima (°C)', f"{stats['temp_max']:.2f}"])
    writer.writerow(['Temperatura Mínima (°C)', f"{stats['temp_min']:.2f}"])
    writer.writerow(['Vibração Média (g)', f"{stats['vib_media']:.3f}"])
    writer.writerow(['Vibração Máxima (g)', f"{stats['vib_max']:.3f}"])
    writer.writerow(['Vibração Mínima (g)', f"{stats['vib_min']:.3f}"])
    writer.writerow(['RPM Médio', f"{stats['rpm_media']:.0f}"])
    writer.writerow(['RPM Máximo', f"{stats['rpm_max']:.0f}"])
    writer.writerow(['RPM Mínimo', f"{stats['rpm_min']:.0f}"])
    writer.writerow([])  # Linha vazia

    # Seção de prescrições (se houver)
    if prescricoes:
        writer.writerow(['PRESCRIÇÕES DE MANUTENÇÃO'])
        writer.writerow(['ID', 'Título', 'Descrição', 'Status', 'Data de Geração'])
        for p in prescricoes:
            writer.writerow([
                p.id,
                p.titulo,
                p.descricao,
                p.status,
                p.data_geracao.strftime('%d/%m/%Y %H:%M') if p.data_geracao else ''
            ])
        writer.writerow([])  # Linha vazia
    else:
        writer.writerow(['PRESCRIÇÕES DE MANUTENÇÃO'])
        writer.writerow(['Nenhuma prescrição encontrada para o período.'])
        writer.writerow([])  # Linha vazia

    # Seção de dados detalhados de telemetria (opcional, pode ser grande)
    # Comentado por padrão para evitar arquivos muito grandes
    # writer.writerow(['DADOS DETALHADOS DE TELEMETRIA'])
    # writer.writerow(['Timestamp', 'Temperatura (°C)', 'Vibração (g)', 'RPM'])
    # for leitura in leituras:
    #     writer.writerow([
    #         leitura.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
    #         f"{leitura.temperatura:.2f}",
    #         f"{leitura.vibracao:.3f}",
    #         leitura.rpm
    #     ])

    return response


def _gerar_relatorio_txt(maquina_id, data_inicio, data_fim, stats, leituras, prescricoes):
    """Gera relatório em formato texto legível."""
    buf = io.StringIO()

    # Cabeçalho
    buf.write(f"RELATÓRIO COMPLETO DE TELEMETRIA - FIELDNODE\n")
    buf.write("=" * 60 + "\n")
    buf.write(f"Máquina: {maquina_id}\n")
    buf.write(f"Período: {data_inicio.strftime('%d/%m/%Y %H:%M')} a {data_fim.strftime('%d/%m/%Y %H:%M')}\n")
    buf.write(f"Gerado em: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    buf.write("\n")

    # Estatísticas de telemetria
    buf.write("ESTATÍSTICAS DE TELEMETRIA\n")
    buf.write("-" * 30 + "\n")
    buf.write(f"Total de Leituras: {stats['total_leituras']}\n")
    buf.write(f"Temperatura Média: {stats['temp_media']:.2f} °C\n")
    buf.write(f"Temperatura Máxima: {stats['temp_max']:.2f} °C\n")
    buf.write(f"Temperatura Mínima: {stats['temp_min']:.2f} °C\n")
    buf.write(f"Vibração Média: {stats['vib_media']:.3f} g\n")
    buf.write(f"Vibração Máxima: {stats['vib_max']:.3f} g\n")
    buf.write(f"Vibração Mínima: {stats['vib_min']:.3f} g\n")
    buf.write(f"RPM Médio: {stats['rpm_media']:.0f}\n")
    buf.write(f"RPM Máximo: {stats['rpm_max']:.0f}\n")
    buf.write(f"RPM Mínimo: {stats['rpm_min']:.0f}\n")
    buf.write("\n")

    # Prescrições
    buf.write("PRESCRIÇÕES DE MANUTENÇÃO\n")
    buf.write("-" * 30 + "\n")
    if prescricoes:
        for i, p in enumerate(prescricoes, 1):
            buf.write(f"{i}. {p.titulo}\n")
            buf.write(f"   Status: {p.status}\n")
            buf.write(f"   Data: {p.data_geracao.strftime('%d/%m/%Y %H:%M') if p.data_geracao else 'N/A'}\n")
            buf.write(f"   Descrição: {p.descricao}\n")
            buf.write("\n")
    else:
        buf.write("Nenhuma prescrição encontrada para o período.\n")
        buf.write("\n")

    # Observação sobre dados detalhados
    buf.write("OBSERVAÇÃO: Para dados detalhados de telemetria (leituras individuais),\n")
    buf.write("utilize o formato CSV que inclui todas as medições no período.\n")

    response = HttpResponse(buf.getvalue(), content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="relatorio_completo_{maquina_id}_{data_inicio.strftime("%Y%m%d")}_{data_fim.strftime("%Y%m%d")}.txt"'
    return response


def gerar_relatorio_csv(maquina_id):
    """
    Função mantida para compatibilidade com views existentes.
    Gera um relatório CSV básico de telemetria.
    """
    queryset = LeituraTelemetria.objects.filter(maquina_id=maquina_id)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{maquina_id}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Temperatura', 'Vibração', 'RPM'])

    for leitura in queryset:
        writer.writerow([leitura.timestamp, leitura.temperatura, leitura.vibracao, leitura.rpm])

    return response