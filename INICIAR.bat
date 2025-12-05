@echo off
title Score de Credito

echo.
echo  ====================================
echo     SIMULADOR DE SCORE DE CREDITO
echo  ====================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo.
    echo Execute primeiro:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit
)

call venv\Scripts\activate.bat

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
