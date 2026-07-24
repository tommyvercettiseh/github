@echo off
setlocal
cd /d "%~dp0"
title Turbo GitHub Hub

where python >nul 2>&1
if errorlevel 1 (
    echo [FOUT] Python is niet gevonden.
    echo Installeer Python 3.11 of nieuwer en vink Add Python to PATH aan.
    pause
    exit /b 1
)

if not exist logs mkdir logs

echo Turbo GitHub Hub starten...
python app.py >> logs\launcher.log 2>&1

if errorlevel 1 (
    echo.
    echo [FOUT] De app kon niet worden gestart.
    echo Bekijk logs\launcher.log voor details.
    pause
)

endlocal
