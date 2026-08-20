#!/usr/bin/env python
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import *

print("🗑️  Limpando banco de dados...")

# Limpar na ordem correta (dependências)
try:
    Prescricao.objects.all().delete()
    print("  ✓ Prescrições removidas")
except Exception:
    print("  ⊘ Tabela Prescricao não existe (ok)")

try:
    LeituraTelemetria.objects.all().delete()
    TelemetriaInvalida.objects.all().delete()
    print("  ✓ Telemetrias removidas")
except Exception:
    print("  ⊘ Tabelas de telemetria não existem (ok)")

Colheitadeira.objects.all().delete()
print("  ✓ Colheitadeiras removidas")

StatusdeOperacao.objects.all().delete()
EstadodeMovimento.objects.all().delete()
TemperaturaMaquina.objects.all().delete()
TempUmi_Ambiente.objects.all().delete()
PressaodoCorte.objects.all().delete()
AlturadoCorte.objects.all().delete()
PressaoPneus.objects.all().delete()
Combustivel.objects.all().delete()
Transbordo.objects.all().delete()
print("  ✓ Dados operacionais removidos")

Operario.objects.all().delete()
print("  ✓ Operários removidos")

Modelo.objects.all().delete()
Marca.objects.all().delete()
UnidadedeMedida.objects.all().delete()
print("  ✓ Marcas, modelos e unidades removidas")

print("\n✅ Banco limpo com sucesso!")
