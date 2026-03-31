@echo off
title Simulador de Lanzamiento
echo =======================================================
echo     Iniciando el Simulador de Lanzamiento...
echo =======================================================
echo.
echo Por favor, espera un momento mientras se carga el servidor local.
echo La aplicacion se abrira automaticamente en tu navegador por defecto.
echo.
echo (Para cerrar el simulador, simplemente cierra esta ventana)
echo.

:: Intenta ejecutar streamlit directamente (útil si está en el PATH de Windows)
python -m streamlit run app.py

:: Si el proceso falla por alguna razón, hace una pausa para que el usuario pueda leer el error
if %errorlevel% neq 0 (
    echo.
    echo =======================================================
    echo ERROR: Ocurrió un problema al iniciar el simulador.
    echo Asegurate de haber instalado las dependencias con:
    echo pip install -r requirements.txt
    echo =======================================================
    pause
)
