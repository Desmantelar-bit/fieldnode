#!/usr/bin/env python
"""Adiciona telemetrias de teste para as 9 colheitadeiras."""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import LeituraTelemetria
from django.utils import timezone
from datetime import timedelta
import uuid
import random

print("📡 Adicionando telemetrias para as colheitadeiras...\n")

maquinas = [
    {"id": "COLH-01", "temp_base": 78, "vib_base": 0.42, "rpm_base": 1850},
    {"id": "COLH-02", "temp_base": 82, "vib_base": 0.55, "rpm_base": 1920},
    {"id": "COLH-03", "temp_base": 65, "vib_base": 0.20, "rpm_base": 800},
    {"id": "COLH-04", "temp_base": 75, "vib_base": 0.38, "rpm_base": 1780},
    {"id": "COLH-05", "temp_base": 88, "vib_base": 0.68, "rpm_base": 2100},
    {"id": "COLH-06", "temp_base": 70, "vib_base": 0.35, "rpm_base": 1650},
    {"id": "COLH-07", "temp_base": 62, "vib_base": 0.15, "rpm_base": 500},
    {"id": "COLH-08", "temp_base": 80, "vib_base": 0.45, "rpm_base": 1880},
    {"id": "COLH-09", "temp_base": 72, "vib_base": 0.40, "rpm_base": 1720},
]

total = 0
agora = timezone.now()

for maq in maquinas:
    print(f"  🔧 {maq['id']}...")
    
    # Adicionar 15 leituras com variação ao longo de 7 dias
    for i in range(15):
        timestamp = agora - timedelta(days=7) + timedelta(hours=i*11)
        
        # Adicionar variação aleatória
        temp = maq['temp_base'] + random.uniform(-5, 8)
        vib = max(0.1, maq['vib_base'] + random.uniform(-0.1, 0.15))
        rpm = int(maq['rpm_base'] + random.uniform(-100, 150))
        
        LeituraTelemetria.objects.create(
            id=uuid.uuid4(),
            maquina_id=maq['id'],
            temperatura=round(temp, 1),
            vibracao=round(vib, 2),
            rpm=rpm,
            latitude=-23.5505 - (i * 0.001),
            longitude=-46.6333 + (i * 0.001),
            timestamp=timestamp
        )
        total += 1
    
    print(f"    ✓ 15 leituras adicionadas")

print(f"\n✅ {total} leituras adicionadas no total!")
print("   Acesse: http://127.0.0.1:3000/colheitadeiras")
print("   Prescrições estarão disponíveis em: http://127.0.0.1:3000/detalhes?id=COLH-01")
