#!/usr/bin/env python
"""
Script de Validação Rápida - FieldNode
Verifica se todas as correções foram aplicadas corretamente
"""
import os
import sys

def check_file_exists(path, description):
    """Verifica se arquivo existe"""
    if os.path.exists(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - ARQUIVO NÃO ENCONTRADO")
        return False

def check_file_contains(path, text, description):
    """Verifica se arquivo contém texto específico"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - TEXTO NÃO ENCONTRADO")
                return False
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return False

def check_file_not_contains(path, text, description):
    """Verifica se arquivo NÃO contém texto específico"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if text not in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - TEXTO AINDA PRESENTE (deveria ter sido removido)")
                return False
    except Exception as e:
        print(f"❌ {description} - ERRO: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  VALIDAÇÃO DO SISTEMA FIELDNODE")
    print("="*60 + "\n")
    
    results = []
    
    # 1. Verificar correção do bug crítico
    print("📋 1. BUG CRÍTICO DE VALIDAÇÃO")
    results.append(check_file_not_contains(
        'api_tcc/services/telemetria.py',
        'if not Colheitadeira.objects.filter(modelo__nome=maquina_id).exists():',
        'Validação bloqueante removida'
    ))
    results.append(check_file_contains(
        'api_tcc/services/telemetria.py',
        'CORREÇÃO: Removida validação',
        'Comentário de correção presente'
    ))
    print()
    
    # 2. Verificar visual unificado
    print("📋 2. VISUAL UNIFICADO")
    results.append(check_file_contains(
        'frontend/detalhes.html',
        '<link rel="stylesheet" href="styles.css"/>',
        'detalhes.html usa styles.css'
    ))
    results.append(check_file_not_contains(
        'frontend/detalhes.html',
        'bootstrap@5.3.0',
        'Bootstrap removido de detalhes.html'
    ))
    print()
    
    # 3. Verificar sistema de busca
    print("📋 3. SISTEMA DE BUSCA")
    results.append(check_file_contains(
        'frontend/dashboard.html',
        'autocomplete-dropdown',
        'Dropdown de autocompletar presente'
    ))
    results.append(check_file_contains(
        'frontend/dashboard.html',
        'function selecionarMaquinaAutocomplete',
        'Função de seleção implementada'
    ))
    print()
    
    # 4. Verificar novas máquinas
    print("📋 4. NOVAS MÁQUINAS CADASTRADAS")
    results.append(check_file_contains(
        'scripts/simular_mqtt.py',
        'NH-CR8090-02',
        'New Holland CR8090-02 cadastrada'
    ))
    results.append(check_file_contains(
        'scripts/simular_mqtt.py',
        'VALTRA-BC8800-01',
        'Valtra BC8800-01 cadastrada'
    ))
    results.append(check_file_contains(
        'scripts/simular_mqtt.py',
        'VALTRA-BC6800-02',
        'Valtra BC6800-02 cadastrada'
    ))
    print()
    
    # 5. Verificar documentação
    print("📋 5. DOCUMENTAÇÃO")
    results.append(check_file_exists(
        'FLUXO-COMPLETO.md',
        'Guia de fluxo completo criado'
    ))
    results.append(check_file_exists(
        'docs/GUIA-SISTEMA-BUSCA.md',
        'Guia do sistema de busca criado'
    ))
    results.append(check_file_exists(
        'TESTE-RAPIDO-BUSCA.md',
        'Guia de teste rápido criado'
    ))
    print()
    
    # Resultado final
    print("="*60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\n📊 RESULTADO: {passed}/{total} verificações passaram")
    
    if failed == 0:
        print("\n🎉 SISTEMA VALIDADO COM SUCESSO!")
        print("\nPróximos passos:")
        print("  1. python manage.py runserver")
        print("  2. python scripts/mqtt_listen.py")
        print("  3. python scripts/simular_mqtt.py")
        print("  4. Acesse: http://127.0.0.1:8000/frontend/dashboard.html")
        return 0
    else:
        print(f"\n⚠️  {failed} verificação(ões) falharam")
        print("\nRevise os itens marcados com ❌ acima")
        return 1

if __name__ == '__main__':
    sys.exit(main())
