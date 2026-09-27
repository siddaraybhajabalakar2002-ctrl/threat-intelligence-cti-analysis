@echo off
title CTI Analysis Platform - Live Public Link
color 0b
echo ========================================================
echo        CTI Analysis Platform - Live Public Link
echo ========================================================
echo.

cd /d "%~dp0"

set "PYTHON_EXE=..\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
)
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo [1/2] Starting CTI Backend Server on http://localhost:5000 ...
start "CTI Server" /B "%PYTHON_EXE%" src\api\app.py

timeout /t 3 /nobreak >nul

echo [2/2] Launching Cloudflare Public Tunnel ...
echo.
echo Look for the URL ending with '.trycloudflare.com' below!
echo Share that link with anyone to view your live project.
echo (Keep this window open while sharing)
echo ========================================================
echo.

if exist "cloudflared.exe" (
    cloudflared.exe tunnel --url http://127.0.0.1:5000
) else if exist "..\threat-intelligence-cti-analysis-main\cloudflared.exe" (
    ..\threat-intelligence-cti-analysis-main\cloudflared.exe tunnel --url http://127.0.0.1:5000
) else (
    echo [ERROR] cloudflared.exe not found!
    pause
)
