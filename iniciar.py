#!/usr/bin/env python
"""
Script de Inicialização - FieldNode
====================================

Inicia o sistema completo automaticamente:
- Verifica dependências
- Aplica migrations
- Popula dados (opcional)
- Inicia Django e frontend
- Abre o navegador

Uso:
    python iniciar.py
    python iniciar.py --sem-dados  # Pula a população de dados
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Cores para terminal (funciona no Windows 10+ e Unix)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

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

def run_command(cmd, check=True, shell=False):
    """Executa comando e retorna True se sucesso"""
    try:
        if shell:
            subprocess.run(cmd, check=check, shell=True, capture_output=True)
        else:
            subprocess.run(cmd, check=check, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error("Python 3.10+ é necessário")
        print_info(f"Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    return True

def check_venv():
    """Verifica se está em um virtualenv"""
    return hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

def check_mysql_connection():
    """Verifica conexão com MySQL"""
    try:
        from decouple import config
        import pymysql
        
        conn = pymysql.connect(
            host=config('DB_HOST'),
            user=config('DB_USER'),
            password=config('DB_PASSWORD'),
            database=config('DB_NAME')
        )
        conn.close()
        return True
    except Exception as e:
        print_error(f"Erro ao conectar no MySQL: {e}")
        return False

def main():
    print_header("🌾 FieldNode - Sistema de Telemetria Agrícola")
    
    # Verifica se está na pasta correta
    if not Path("manage.py").exists():
        print_error("Arquivo manage.py não encontrado!")
        print_info("Execute este script na pasta raiz do projeto.")
        sys.exit(1)
    
    # Verifica versão do Python
    print_info("Verificando versão do Python...")
    if not check_python_version():
        sys.exit(1)
    print_success("Python OK")
    
    # Verifica virtualenv
    if not check_venv():
        print_warning("Não está em um virtualenv!")
        print_info("Recomendado: ative o virtualenv antes de executar")
        print_info("  Windows: .venv\\Scripts\\activate")
        print_info("  Linux/Mac: source .venv/bin/activate")
        
        resposta = input("\nContinuar mesmo assim? [s/N]: ").strip().lower()
        if resposta != 's':
            sys.exit(0)
    
    # Verifica dependências
    print_info("Verificando dependências...")
    try:
        import django
        import rest_framework
        import drf_yasg
        print_success("Dependências OK")
    except ImportError:
        print_warning("Dependências não encontradas. Instalando...")
        if run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
            print_success("Dependências instaladas")
        else:
            print_error("Falha ao instalar dependências")
            sys.exit(1)
    
    # Verifica .env
    if not Path(".env").exists():
        print_warning("Arquivo .env não encontrado")
        if Path(".env.example").exists():
            print_info("Copiando .env.example para .env...")
            import shutil
            shutil.copy(".env.example", ".env")
            print_warning("Configure suas credenciais do MySQL no arquivo .env")
            input("Pressione Enter após configurar...")
        else:
            print_error("Arquivo .env.example não encontrado")
            sys.exit(1)
    
    # Verifica conexão MySQL
    print_info("Verificando conexão com MySQL...")
    if not check_mysql_connection():
        print_error("Não foi possível conectar ao MySQL")
        print_info("Verifique se:")
        print_info("  1. O MySQL está rodando")
        print_info("  2. As credenciais no .env estão corretas")
        print_info("  3. O banco 'fieldnode' foi criado")
        print_info("\nPara criar o banco, execute no MySQL:")
        print_info("  CREATE DATABASE fieldnode CHARACTER SET utf8mb4;")
        sys.exit(1)
    print_success("Conexão com MySQL OK")
    
    # Aplica migrations
    print_info("Aplicando migrations...")
    if run_command([sys.executable, "manage.py", "migrate", "--noinput"]):
        print_success("Migrations aplicadas")
    else:
        print_error("Falha ao aplicar migrations")
        sys.exit(1)
    
    # Pergunta se quer popular dados
    if "--sem-dados" not in sys.argv:
        print_header("População de Dados")
        print_info("Deseja popular o banco com dados de demonstração?")
        print_info("(Recomendado para primeira execução)")
        
        resposta = input("\nDigite S para popular ou N para pular [S/n]: ").strip().lower()
        
        if resposta in ['s', '']:
            print_info("Populando banco de dados...")
            if run_command([sys.executable, "simular_dados.py"]):
                print_success("Dados populados com sucesso!")
            else:
                print_warning("Erro ao popular dados. Continuando...")
    
    # Inicia servidores
    print_header("🚀 Iniciando Servidores")
    
    # Django
    print_info("Iniciando Django na porta 8000...")
    django_process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Aguarda Django iniciar
    
    if django_process.poll() is None:
        print_success("Django rodando")
    else:
        print_error("Falha ao iniciar Django")
        sys.exit(1)
    
    # Frontend
    print_info("Iniciando servidor do frontend na porta 5500...")
    
    # Verifica se a pasta frontend existe
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print_error("Pasta 'frontend' não encontrada!")
        django_process.terminate()
        sys.exit(1)
    
    # Verifica se index.html existe
    if not (frontend_path / "index.html").exists():
        print_error("Arquivo 'frontend/index.html' não encontrado!")
        django_process.terminate()
        sys.exit(1)
    
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "5500", "--bind", "127.0.0.1"],
        cwd=str(frontend_path),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Aguarda frontend iniciar
    
    if frontend_process.poll() is None:
        print_success("Frontend rodando")
        print_info(f"Servindo arquivos de: {frontend_path.absolute()}")
    else:
        print_error("Falha ao iniciar frontend")
        # Tenta descobrir o erro
        stderr = frontend_process.stderr.read().decode('utf-8', errors='ignore')
        if stderr:
            print_error(f"Erro: {stderr}")
        django_process.terminate()
        sys.exit(1)
    
    # Abre navegador
    print_info("Abrindo dashboard no navegador...")
    time.sleep(1)
    # Usa 127.0.0.1 em vez de localhost (mais rápido, sem resolução DNS)
    webbrowser.open("http://127.0.0.1:5500/index.html")
    
    # Resumo
    print_header("✅ Sistema Iniciado com Sucesso!")
    print(f"\n  📊 Dashboard:     {Colors.BLUE}http://127.0.0.1:5500/index.html{Colors.RESET}")
    print(f"  🔧 API Django:    {Colors.BLUE}http://127.0.0.1:8000{Colors.RESET}")
    print(f"  📚 Swagger:       {Colors.BLUE}http://127.0.0.1:8000/swagger/{Colors.RESET}")
    print(f"  👤 Admin:         {Colors.BLUE}http://127.0.0.1:8000/admin/{Colors.RESET}")
    
    print(f"\n  💡 Dica: Aguarde 3 segundos para o polling atualizar a tabela")
    print(f"\n  ⚠️  Para parar os servidores, pressione Ctrl+C")
    print(f"\n{'='*60}\n")
    
    # Mantém os processos rodando
    try:
        django_process.wait()
    except KeyboardInterrupt:
        print_info("\nEncerrando servidores...")
        django_process.terminate()
        frontend_process.terminate()
        print_success("Servidores encerrados")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\nOperação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        sys.exit(1)
