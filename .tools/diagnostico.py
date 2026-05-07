#!/usr/bin/env python
"""
Script de Diagnóstico - FieldNode
==================================

Identifica problemas comuns de rede e servidor.

Uso:
    python diagnostico.py
"""

import os
import sys
import socket
import subprocess
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.RESET} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.RESET}  {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.RESET}  {text}")

def check_port(port, host='127.0.0.1'):
    """Verifica se uma porta está disponível"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0  # True se porta está em uso
    except:
        return False

def check_file_exists(path):
    """Verifica se um arquivo existe"""
    return Path(path).exists()

def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Não detectado"

def main():
    print_header("🔍 Diagnóstico do Sistema FieldNode")
    
    # 1. Verificar estrutura de arquivos
    print_info("Verificando estrutura de arquivos...")
    
    arquivos_criticos = [
        "manage.py",
        "frontend/index.html",
        "frontend/config.js",
        "frontend/styles.css",
        "frontend/js/api.js",
        "frontend/js/colors.js",
        "frontend/js/status.js",
    ]
    
    arquivos_ok = True
    for arquivo in arquivos_criticos:
        if check_file_exists(arquivo):
            print_success(f"{arquivo}")
        else:
            print_error(f"{arquivo} NÃO ENCONTRADO")
            arquivos_ok = False
    
    if not arquivos_ok:
        print_error("\nArquivos críticos faltando! Verifique a estrutura do projeto.")
        return
    
    print_success("\nTodos os arquivos críticos encontrados")
    
    # 2. Verificar portas
    print_header("🔌 Verificando Portas")
    
    porta_8000 = check_port(8000)
    porta_5500 = check_port(5500)
    
    if porta_8000:
        print_warning("Porta 8000 (Django) está EM USO")
        print_info("  Isso é NORMAL se o Django já está rodando")
        print_info("  Se não deveria estar rodando, execute: taskkill /F /IM python.exe")
    else:
        print_success("Porta 8000 (Django) está LIVRE")
    
    if porta_5500:
        print_warning("Porta 5500 (Frontend) está EM USO")
        print_info("  Isso é NORMAL se o frontend já está rodando")
        print_info("  Se não deveria estar rodando, execute: taskkill /F /IM python.exe")
    else:
        print_success("Porta 5500 (Frontend) está LIVRE")
    
    # 3. Verificar conectividade
    print_header("🌐 Verificando Conectividade")
    
    ip_local = get_local_ip()
    print_info(f"IP Local: {ip_local}")
    
    # Testa localhost
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect(("127.0.0.1", 80))
        sock.close()
        print_success("Localhost (127.0.0.1) acessível")
    except:
        print_warning("Localhost pode ter problemas de conectividade")
    
    # 4. Verificar Python e dependências
    print_header("🐍 Verificando Python")
    
    print_info(f"Versão do Python: {sys.version.split()[0]}")
    print_info(f"Executável: {sys.executable}")
    
    # Verifica virtualenv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Virtualenv ATIVO")
    else:
        print_warning("Virtualenv NÃO ATIVO")
        print_info("  Recomendado: .venv\\Scripts\\activate")
    
    # Verifica dependências
    print_info("\nVerificando dependências críticas...")
    dependencias = ['django', 'rest_framework', 'requests']
    
    for dep in dependencias:
        try:
            __import__(dep)
            print_success(f"{dep}")
        except ImportError:
            print_error(f"{dep} NÃO INSTALADO")
    
    # 5. Teste de servidor HTTP
    print_header("🧪 Teste de Servidor HTTP")
    
    print_info("Iniciando servidor de teste na porta 8888...")
    
    try:
        # Tenta iniciar servidor de teste
        test_server = subprocess.Popen(
            [sys.executable, "-m", "http.server", "8888", "--bind", "127.0.0.1"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        import time
        time.sleep(2)
        
        if test_server.poll() is None:
            print_success("Servidor de teste INICIADO com sucesso")
            
            # Testa acesso
            try:
                import urllib.request
                response = urllib.request.urlopen("http://127.0.0.1:8888/index.html", timeout=3)
                if response.status == 200:
                    print_success("index.html ACESSÍVEL em http://127.0.0.1:8888/index.html")
                else:
                    print_error(f"index.html retornou status {response.status}")
            except Exception as e:
                print_error(f"Erro ao acessar index.html: {e}")
            
            # Encerra servidor de teste
            test_server.terminate()
            print_info("Servidor de teste encerrado")
        else:
            print_error("Falha ao iniciar servidor de teste")
            stderr = test_server.stderr.read().decode('utf-8', errors='ignore')
            if stderr:
                print_error(f"Erro: {stderr}")
    
    except Exception as e:
        print_error(f"Erro no teste: {e}")
    
    # 6. Recomendações
    print_header("💡 Recomendações")
    
    if not porta_8000 and not porta_5500:
        print_success("Sistema pronto para iniciar!")
        print_info("\nExecute: python iniciar.py")
    elif porta_8000 and porta_5500:
        print_success("Sistema já está rodando!")
        print_info("\nAcesse: http://127.0.0.1:5500/index.html")
    else:
        print_warning("Portas parcialmente ocupadas")
        print_info("\nPara liberar portas:")
        print_info("  Windows: taskkill /F /IM python.exe")
        print_info("  Linux/Mac: pkill -f python")
    
    # 7. URLs de teste
    print_header("🔗 URLs para Testar")
    
    urls = [
        ("Dashboard", "http://127.0.0.1:5500/index.html"),
        ("API Django", "http://127.0.0.1:8000"),
        ("Swagger", "http://127.0.0.1:8000/swagger/"),
        ("Admin", "http://127.0.0.1:8000/admin/"),
    ]
    
    for nome, url in urls:
        print_info(f"{nome:15} → {url}")
    
    print("\n" + "="*60)
    print("  Diagnóstico concluído!")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\nDiagnóstico cancelado")
    except Exception as e:
        print_error(f"Erro: {e}")
