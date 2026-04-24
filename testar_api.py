#!/usr/bin/env python
"""
Teste de Conectividade da API - FieldNode
==========================================

Verifica se a API Django está respondendo corretamente.

Uso:
    python testar_api.py
"""

import sys
import time
import urllib.request
import urllib.error
import json

def test_api():
    print("🔍 Testando conectividade com a API Django...\n")
    
    endpoints = [
        ("Root", "http://127.0.0.1:8000/"),
        ("Colheitadeiras", "http://127.0.0.1:8000/Colheitadeira/"),
        ("Telemetria", "http://127.0.0.1:8000/api/telemetria/"),
        ("Swagger", "http://127.0.0.1:8000/swagger/"),
    ]
    
    for nome, url in endpoints:
        print(f"Testando {nome}... ", end="", flush=True)
        
        try:
            response = urllib.request.urlopen(url, timeout=5)
            status = response.status
            
            if status == 200:
                print(f"✅ OK (HTTP {status})")
                
                # Se for JSON, mostra preview
                if 'application/json' in response.headers.get('Content-Type', ''):
                    try:
                        data = json.loads(response.read().decode('utf-8'))
                        if isinstance(data, list):
                            print(f"   → Retornou {len(data)} registro(s)")
                        elif isinstance(data, dict):
                            print(f"   → Retornou objeto com {len(data)} campo(s)")
                    except:
                        pass
            else:
                print(f"⚠️  HTTP {status}")
                
        except urllib.error.HTTPError as e:
            print(f"❌ Erro HTTP {e.code}")
            if e.code == 404:
                print(f"   → Endpoint não encontrado")
            elif e.code == 500:
                print(f"   → Erro interno do servidor")
                
        except urllib.error.URLError as e:
            print(f"❌ Erro de conexão")
            print(f"   → {e.reason}")
            print(f"   → Verifique se o Django está rodando")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        time.sleep(0.5)
    
    print("\n" + "="*60)
    print("Teste concluído!")
    print("="*60)

if __name__ == "__main__":
    test_api()
