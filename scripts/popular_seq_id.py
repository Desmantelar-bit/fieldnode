#!/usr/bin/env python
"""
Script para popular o campo seq_id em registros existentes.
Executa uma única vez após adicionar o campo.

Uso:
    python scripts/popular_seq_id.py
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from api_tcc.models import LeituraTelemetria

def popular_seq_id():
    """Popula seq_id em todos os registros que não possuem."""
    leituras_sem_seq = LeituraTelemetria.objects.filter(seq_id__isnull=True).order_by('recebido_em')
    total = leituras_sem_seq.count()
    
    if total == 0:
        print("[OK] Todos os registros ja possuem seq_id")
        return
    
    print(f"[INFO] Encontrados {total} registros sem seq_id")
    print("[INFO] Populando...")
    
    seq_atual = 1
    ultimo_com_seq = LeituraTelemetria.objects.filter(seq_id__isnull=False).order_by('-seq_id').first()
    if ultimo_com_seq:
        seq_atual = ultimo_com_seq.seq_id + 1
    
    for idx, leitura in enumerate(leituras_sem_seq, start=1):
        leitura.seq_id = seq_atual
        leitura.save(update_fields=['seq_id'])
        seq_atual += 1
        
        if idx % 100 == 0:
            print(f"  Processados {idx}/{total}...")
    
    print(f"[OK] Concluido! {total} registros atualizados")

if __name__ == '__main__':
    popular_seq_id()
