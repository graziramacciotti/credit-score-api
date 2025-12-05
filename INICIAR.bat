@echo off
title Score de Credito

echo.
echo  ====================================
echo     SIMULADOR DE SCORE DE CREDITO
echo  ====================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Baixe em: https://www.python.org/downloads/
    echo.
    pause
    exit
)

if not exist "venv\Scripts\activate.bat" (
    echo Primeira execucao detectada!
    echo.
    echo Criando ambiente virtual...
    python -m venv venv
    
    echo Ativando ambiente...
    call venv\Scripts\activate.bat
    
    echo Instalando dependencias...
    pip install -r requirements.txt
    
    echo.
    echo Instalacao concluida!
    echo.
) else (
    call venv\Scripts\activate.bat
)

echo Abrindo interface no navegador...
timeout /t 2 /nobreak >nul
start "" "index.html"

echo.
echo API rodando em: http://localhost:8000
echo Swagger em: http://localhost:8000/docs
echo.
echo Para encerrar, pressione CTRL+C
echo.

python main.py
