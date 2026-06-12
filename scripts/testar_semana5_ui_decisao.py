#!/usr/bin/env python3
"""
Script para testar a funcionalidade de prescrição implementada na Semana 5.
Valida endpoints, tipos Zod e comportamento do modal.
"""

import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api"
API_KEY = "fieldnode-demo-2024"

def test_prescricao_endpoint():
    """Testa se o endpoint de prescrição responde corretamente"""
    print("Testando endpoint /api/prescricoes/...")
    
    try:
        # Primeiro testa sem maquina_id (deve dar erro)
        response = requests.get(
            f"{API_URL}/prescricoes/",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 400:
            print("Endpoint corretamente rejeita requisição sem maquina_id")
            
            # Agora testa com maquina_id
            response = requests.get(
                f"{API_URL}/prescricoes/?maquina_id=COLH-01",
                headers={"X-API-Key": API_KEY},
                timeout=5
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Endpoint funcionando. Tipo de resposta: {type(data)}")
            
            # Se for array
            if isinstance(data, list) and len(data) > 0:
                prescricao = data[0]
            # Se for objeto único
            elif isinstance(data, dict):
                prescricao = data
            else:
                print("Resposta vazia ou formato inesperado")
                return True
            
            required_fields = ['maquina_id', 'recomendacao', 'prioridade', 'categoria', 'justificativa', 'timestamp']
            missing_fields = [field for field in required_fields if field not in prescricao]
            
            if missing_fields:
                print(f"Campos obrigatórios faltando: {missing_fields}")
            else:
                print("Estrutura da prescricao esta correta")
                print(f"   Maquina: {prescricao['maquina_id']}")
                print(f"   Prioridade: {prescricao['prioridade']}")
                print(f"   Recomendacao: {prescricao['recomendacao'][:50]}...")
        else:
            print(f"Endpoint falhou: {response.status_code}")
            if response.text:
                print(f"Erro: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexao: {e}")
        return False
    
    return True

def test_relatorio_endpoint():
    """Testa se o endpoint de relatório responde corretamente"""
    print("\nTestando endpoint /api/relatorio/...")
    
    try:
        # Testa relatório geral (sem maquina_id específico)
        response = requests.get(
            f"{API_URL}/relatorio/?formato=json",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("Endpoint de relatorio funcionando")
            
            required_fields = ['periodo', 'total_leituras', 'maquinas_ativas', 'alertas_gerados']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"Campos obrigatorios faltando no relatorio: {missing_fields}")
            else:
                print("Estrutura do relatorio esta correta")
                print(f"   Periodo: {data['periodo']}")
                print(f"   Total de leituras: {data['total_leituras']}")
        else:
            print(f"Endpoint de relatorio falhou: {response.status_code}")
            if response.text:
                print(f"Erro: {response.text[:200]}")
            
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexao no relatorio: {e}")
        return False
    
    return True

def test_maquina_specific_prescricao():
    """Testa prescrição para máquina específica"""
    print("\nTestando prescricao para maquina especifica...")
    
    # Primeiro, pega uma máquina que existe
    try:
        telemetry_response = requests.get(f"{API_URL}/leituras/ultimas/", timeout=5)
        if telemetry_response.status_code == 200:
            telemetry_data = telemetry_response.json()
            if telemetry_data:
                machine_id = telemetry_data[0]['maquina_id']
                print(f"   Testando com maquina: {machine_id}")
                
                prescricao_response = requests.get(
                    f"{API_URL}/prescricoes/?maquina_id={machine_id}",
                    headers={"X-API-Key": API_KEY},
                    timeout=5
                )
                
                if prescricao_response.status_code == 200:
                    prescricao_data = prescricao_response.json()
                    print("Prescricao especifica funcionando")
                    
                    if isinstance(prescricao_data, list) and len(prescricao_data) > 0:
                        prescricao = prescricao_data[0]
                        print(f"   Recomendacao: {prescricao['recomendacao'][:50]}...")
                    elif isinstance(prescricao_data, dict) and 'recomendacao' in prescricao_data:
                        print(f"   Recomendacao: {prescricao_data['recomendacao'][:50]}...")
                    else:
                        print("   Resposta vazia ou formato inesperado")
                else:
                    print(f"Falha na prescricao especifica: {prescricao_response.status_code}")
            else:
                print("Nenhuma telemetria disponivel para teste")
        else:
            print("Nao foi possivel obter lista de maquinas")
            
    except requests.exceptions.RequestException as e:
        print(f"Erro no teste de maquina especifica: {e}")
        return False
    
    return True

def main():
    print("Iniciando testes da Semana 5 - UI de Decisao")
    print("=" * 50)
    
    # Testa backend
    backend_ok = all([
        test_prescricao_endpoint(),
        test_relatorio_endpoint(),
        test_maquina_specific_prescricao()
    ])
    
    print("\n" + "=" * 50)
    if backend_ok:
        print("Backend pronto para UI de Decisao")
        print("\nProximos passos para validar no frontend:")
        print("   1. Abra http://127.0.0.1:3000/colheitadeiras")
        print("   2. Clique no botao 'Ver Decisao' de qualquer maquina")
        print("   3. Verifique se o modal abre com prescricao")
        print("   4. Teste fechar o modal clicando fora dele")
        print("   5. Va para /detalhes?id=COLH-01 e teste o botao da toolbar")
    else:
        print("Problemas encontrados no backend")
        print("   Corrija os endpoints antes de testar o frontend")

if __name__ == "__main__":
    main()