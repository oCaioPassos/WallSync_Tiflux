@echo off
title WallSync Tiflux
echo ============================================
echo       WallSync Tiflux - Inicializando
echo ============================================
echo.
echo Verificando dependencias...
pip install -r requirements.txt --quiet
echo.
echo Iniciando WallSync Tiflux...
python main.py
pause
