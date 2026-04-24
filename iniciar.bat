@echo off
chcp 65001 >nul
cls

echo ============================================================
echo   🌾 FieldNode - Sistema de Telemetria Agrícola
echo   Iniciando ambiente de desenvolvimento...
echo ============================================================
echo.

REM Verifica se está na pasta correta
if not exist "manage.py" (
    echo ❌ ERRO: Arquivo manage.py não encontrado!
    echo    Execute este script na pasta raiz do projeto.
    pause
    exit /b 1
)

REM Verifica se o virtualenv existe
if not exist ".venv\Scripts\activate.bat" (
    echo ⚠️  Virtualenv não encontrado. Criando...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ ERRO: Falha ao criar virtualenv.
        echo    Verifique se o Python 3.12+ está instalado.
        pause
        exit /b 1
    )
    echo ✅ Virtualenv criado com sucesso!
    echo.
)

REM Ativa o virtualenv
echo 🔧 Ativando virtualenv...
call .venv\Scripts\activate.bat

REM Verifica se o Django está instalado
python -c "import django" 2>nul
if errorlevel 1 (
    echo ⚠️  Dependências não encontradas. Instalando...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ ERRO: Falha ao instalar dependências.
        pause
        exit /b 1
    )
    echo ✅ Dependências instaladas com sucesso!
    echo.
)

REM Verifica se o .env existe
if not exist ".env" (
    echo ⚠️  Arquivo .env não encontrado.
    if exist ".env.example" (
        echo    Copiando .env.example para .env...
        copy .env.example .env >nul
        echo.
        echo ⚠️  ATENÇÃO: Configure suas credenciais do MySQL no arquivo .env
        echo    Pressione qualquer tecla após configurar...
        pause >nul
    ) else (
        echo ❌ ERRO: Arquivo .env.example não encontrado.
        pause
        exit /b 1
    )
)

REM Verifica conexão com MySQL
echo 🔍 Verificando conexão com MySQL...
python -c "import os; from decouple import config; import pymysql; pymysql.connect(host=config('DB_HOST'), user=config('DB_USER'), password=config('DB_PASSWORD'))" 2>nul
if errorlevel 1 (
    echo ❌ ERRO: Não foi possível conectar ao MySQL.
    echo    Verifique se:
    echo    1. O MySQL está rodando
    echo    2. As credenciais no .env estão corretas
    echo    3. O banco 'fieldnode' foi criado
    echo.
    echo    Para criar o banco, execute no MySQL:
    echo    CREATE DATABASE fieldnode CHARACTER SET utf8mb4;
    echo.
    pause
    exit /b 1
)
echo ✅ Conexão com MySQL OK!
echo.

REM Aplica migrations
echo 🔧 Aplicando migrations...
python manage.py migrate --noinput
if errorlevel 1 (
    echo ❌ ERRO: Falha ao aplicar migrations.
    pause
    exit /b 1
)
echo ✅ Migrations aplicadas com sucesso!
echo.

REM Pergunta se quer popular dados
echo.
echo ============================================================
echo   Deseja popular o banco com dados de demonstração?
echo   (Recomendado para primeira execução)
echo ============================================================
echo.
set /p POPULAR="Digite S para popular ou N para pular [S/n]: "

if /i "%POPULAR%"=="S" (
    echo.
    echo 📊 Populando banco de dados...
    python simular_dados.py
    if errorlevel 1 (
        echo ⚠️  Aviso: Erro ao popular dados. Continuando...
    ) else (
        echo ✅ Dados populados com sucesso!
    )
    echo.
) else if /i "%POPULAR%"=="" (
    echo.
    echo 📊 Populando banco de dados...
    python simular_dados.py
    if errorlevel 1 (
        echo ⚠️  Aviso: Erro ao popular dados. Continuando...
    ) else (
        echo ✅ Dados populados com sucesso!
    )
    echo.
)

REM Inicia o servidor Django em uma nova janela
echo.
echo ============================================================
echo   🚀 Iniciando servidor Django...
echo ============================================================
echo.
start "FieldNode - Django Server" cmd /k "cd /d %CD% && .venv\Scripts\activate.bat && python manage.py runserver"

REM Aguarda 3 segundos para o Django iniciar
timeout /t 3 /nobreak >nul

REM Inicia o servidor do frontend em outra janela
echo 🌐 Iniciando servidor do frontend...
start "FieldNode - Frontend Server" cmd /k "cd /d %CD%\frontend && python -m http.server 5500"

REM Aguarda 2 segundos
timeout /t 2 /nobreak >nul

REM Abre o navegador
echo 🌐 Abrindo dashboard no navegador...
start http://127.0.0.1:5500/index.html

echo.
echo ============================================================
echo   ✅ Sistema iniciado com sucesso!
echo ============================================================
echo.
echo   📊 Dashboard:     http://127.0.0.1:5500/index.html
echo   🔧 API Django:    http://127.0.0.1:8000
echo   📚 Swagger:       http://127.0.0.1:8000/swagger/
echo   👤 Admin:         http://127.0.0.1:8000/admin/
echo.
echo   💡 Dica: Aguarde 3 segundos para o polling atualizar a tabela
echo.
echo   ⚠️  Para parar os servidores, feche as janelas do Django e Frontend
echo      ou pressione Ctrl+C em cada uma delas.
echo.
echo ============================================================
echo.
pause
