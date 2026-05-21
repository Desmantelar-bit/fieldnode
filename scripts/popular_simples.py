#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
import uuid

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import LeituraTelemetria

def popular_dados():
    print("Populando banco com dados de teste...")
    
    maquinas = ["CASE-TC5000-01", "JOHN-DEERE-02", "NEW-HOLLAND-03"]
    
    # Gerar 50 leituras para cada máquina
    for maquina_id in maquinas:
        for i in range(50):
            timestamp = datetime.now() - timedelta(minutes=i*5)
            
            # Simular dados variados
            if i < 10:  # Últimas 10 leituras normais
                temp = 65 + (i % 5) * 2
                vib = 0.2 + (i % 3) * 0.1
                rpm = 1800 + (i % 4) * 50
            elif i < 20:  # Algumas com temperatura alta
                temp = 80 + (i % 3) * 3
                vib = 0.4 + (i % 2) * 0.1
                rpm = 1900 + (i % 3) * 30
            else:  # Dados normais históricos
                temp = 70 + (i % 6) * 2
                vib = 0.3 + (i % 4) * 0.05
                rpm = 1850 + (i % 5) * 25
            
            LeituraTelemetria.objects.create(
                id=uuid.uuid4(),
                maquina_id=maquina_id,
                temperatura=temp,
                vibracao=vib,
                rpm=rpm,
                timestamp=timestamp
            )
    
    total = LeituraTelemetria.objects.count()
    print(f"Criadas {total} leituras de telemetria")
    
    # Mostrar uma amostra
    for maquina in maquinas:
        ultima = LeituraTelemetria.objects.filter(maquina_id=maquina).order_by('-timestamp').first()
        if ultima:
            print(f"{maquina}: Temp={ultima.temperatura}°C, Vib={ultima.vibracao}, RPM={ultima.rpm}")

if __name__ == "__main__":
    popular_dados()