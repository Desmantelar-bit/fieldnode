"""
Script para resetar o banco de dados MySQL
Execute: python scripts/resetar_banco.py
"""
import os
import sys
import MySQLdb
from decouple import config

def resetar_banco():
    print("🔄 Resetando banco de dados MySQL...")
    print("-" * 60)
    
    # Ler configurações do .env
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='3306', cast=int)
    db_user = config('DB_USER')
    db_password = config('DB_PASSWORD')
    db_name = config('DB_NAME')
    
    print(f"📊 Banco: {db_name}")
    print(f"🖥️  Host: {db_host}:{db_port}")
    print(f"👤 Usuário: {db_user}")
    print()
    
    try:
        # Conectar ao MySQL (sem especificar o banco)
        print("🔌 Conectando ao MySQL...")
        conn = MySQLdb.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            passwd=db_password
        )
        cursor = conn.cursor()
        
        # Dropar banco se existir
        print(f"🗑️  Dropando banco '{db_name}' (se existir)...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        print("   ✅ Banco dropado")
        
        # Criar banco novo
        print(f"🆕 Criando banco '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("   ✅ Banco criado")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ Banco de dados resetado com sucesso!")
        print("=" * 60)
        print()
        print("📋 Próximos passos:")
        print("   1. python manage.py migrate")
        print("   2. python scripts/popular_dados_teste.py")
        print("   3. python manage.py runserver")
        
    except MySQLdb.Error as e:
        print(f"\n❌ Erro ao conectar no MySQL: {e}")
        print("\n💡 Verifique:")
        print("   - MySQL está rodando?")
        print("   - Credenciais no .env estão corretas?")
        print("   - Usuário tem permissão para criar/dropar bancos?")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    resetar_banco()
